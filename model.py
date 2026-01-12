# model.py
# ---------------------------------------
# Clean inference-only LSTM pipeline
# ---------------------------------------

import os
import numpy as np
import pandas as pd
import joblib


# ---------------------------------------
# CONFIG
# ---------------------------------------
DATA_PATH = os.path.join("data", "nbpdcl1_data.csv")
MODEL_PATH = "load_prediction_model.pkl"
SCALER_PATH = "load_model.pkl"

WINDOW_SIZE = 48
MIN_HISTORY = 100
SMOOTH_WINDOW = 3


# ---------------------------------------
# LOAD DATA
# ---------------------------------------
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"CSV not found: {DATA_PATH}")

df = pd.read_csv(DATA_PATH)


df["ts"] = pd.to_datetime(df["ts"], format="mixed", errors="coerce")
df = df.dropna(subset=["ts"])
df = df.sort_values("ts")

if df.empty:
    raise ValueError("Dataset is empty after timestamp cleaning")


# ---------------------------------------
# LOAD MODEL & SCALER
# ---------------------------------------
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")

if not os.path.exists(SCALER_PATH):
    raise FileNotFoundError(f"Scaler file not found: {SCALER_PATH}")

model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)


# ---------------------------------------
# MAIN FORECAST FUNCTION (USED BY FastAPI)
# ---------------------------------------
def lstm_forecast_for_consumer(consumer_id: str, hours: int = 24):

    consumer_df = df[df["msn"] == consumer_id].copy()

    if consumer_df.empty or len(consumer_df) < MIN_HISTORY:
        return {
            "consumer_id": consumer_id,
            "message": "Not enough historical data",
            "forecast": []
        }

    # Hourly aggregation
    ts_data = (
        consumer_df
        .set_index("ts")["wh_imp"]
        .resample("H")
        .sum()
        .ffill()
    )

    if len(ts_data) < WINDOW_SIZE:
        return {
            "consumer_id": consumer_id,
            "message": "Insufficient hourly data after resampling",
            "forecast": []
        }

    # Scaling
    scaled_data = scaler.transform(ts_data.values.reshape(-1, 1))

    # Last input window
    current_window = scaled_data[-WINDOW_SIZE:].reshape(1, WINDOW_SIZE, 1)

    future_scaled = []
    future_times = []

    last_ts = ts_data.index[-1]

    # -----------------------------------
    # Prediction loop
    # -----------------------------------
    for i in range(hours):
        pred_scaled = model.predict(current_window, verbose=0)[0][0]
        future_scaled.append(pred_scaled)

        # slide window
        current_window = np.append(
            current_window[:, 1:, :],
            [[[pred_scaled]]],
            axis=1
        )

        future_times.append(last_ts + pd.Timedelta(hours=i + 1))

    # Inverse scaling
    forecast = scaler.inverse_transform(
        np.array(future_scaled).reshape(-1, 1)
    ).flatten()

    # -----------------------------------
    # DOMAIN CONSTRAINT (NO NEGATIVE LOAD)
    # -----------------------------------
    forecast = np.maximum(forecast, 0)

    # -----------------------------------
    # SMOOTHING
    # -----------------------------------
    forecast = (
        pd.Series(forecast)
        .rolling(window=SMOOTH_WINDOW, min_periods=1)
        .mean()
        .round(2)
        .tolist()
    )

    # -----------------------------------
    # RESPONSE FORMAT
    # -----------------------------------
    result = []
    for t, v in zip(future_times, forecast):
        result.append({
            "time": t.strftime("%Y-%m-%d %H:%M:%S"),
            "predicted_load_wh": v
        })

    return {
        "consumer_id": consumer_id,
        "hours": hours,
        "forecast": result,
        "note": "LSTM inference with domain constraints & smoothing"
    }
