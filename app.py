from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from model import lstm_forecast_for_consumer
import pandas as pd
import os

app = FastAPI(
    title="AI-Based Load Forecasting API",
    description="Consumer-wise short-term load forecasting using LSTM",
    version="1.0"
)

# ---------------------------
# CORS Middleware
# ---------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # React localhost + future deploy
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Constants
# ---------------------------
DATA_PATH = os.path.join("data", "nbpdcl1_data.csv")

# ---------------------------
# Home
# ---------------------------
@app.get("/")
def home():
    return {"status": "API is running successfully"}

# ---------------------------
# CSV-based Consumers API
# ---------------------------
@app.get("/consumers")
def get_consumers():
    if not os.path.exists(DATA_PATH):
        return {
            "error": "Dataset not found. Please run: python download_data.py"
        }

    df = pd.read_csv(DATA_PATH)

    # 🔁 Change column name if required
    consumer_ids = df["msn"].astype(str).unique().tolist()

    return {"consumers": consumer_ids}

# ---------------------------
# Forecast API
# ---------------------------
@app.get("/forecast")
def forecast(consumer_id: str, hours: int = 24):
    return lstm_forecast_for_consumer(consumer_id, hours)
