import { useEffect, useState } from "react";

// -------- Chart.js Imports --------
import {
  Chart as ChartJS,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Tooltip,
  Legend,
  Title,
} from "chart.js";
import { Line } from "react-chartjs-2";

ChartJS.register(
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Tooltip,
  Legend,
  Title
);

// -------- Table styles --------
const thStyle = {
  border: "1px solid #ddd",
  padding: "10px",
  textAlign: "center",
  fontWeight: "bold",
  backgroundColor: "#f5f5f5",
};

const tdStyle = {
  border: "1px solid #ddd",
  padding: "8px",
  textAlign: "center",
};

function App() {
  const [consumers, setConsumers] = useState([]);
  const [selectedConsumer, setSelectedConsumer] = useState("");
  const [forecast, setForecast] = useState([]);

  // -------------------------------
  // Load consumers from backend
  // -------------------------------
  useEffect(() => {
    fetch("http://127.0.0.1:8000/consumers")
      .then((res) => res.json())
      .then((data) => setConsumers(data.consumers));
  }, []);

  // -------------------------------
  // Fetch forecast
  // -------------------------------
  const getForecast = () => {
    fetch(
      `http://127.0.0.1:8000/forecast?consumer_id=${selectedConsumer}&hours=24`
    )
      .then((res) => res.json())
      .then((data) => setForecast(data.forecast));
  };

  // -------------------------------
  // Chart Data
  // -------------------------------
  const chartData = {
    labels: forecast.map((f) => f.time),
    datasets: [
      {
        label: "Predicted Load (Wh)",
        data: forecast.map((f) => f.predicted_load_wh),
        borderColor: "#ff9800",
        backgroundColor: "rgba(255,152,0,0.25)",
        tension: 0.4,
        pointRadius: 3,
        fill: true,
      },
    ],
  };

  // -------------------------------
  // Chart Options
  // -------------------------------
  const chartOptions = {
    responsive: true,
    plugins: {
      legend: { position: "top" },
      title: {
        display: true,
        text: "Load Forecast (Time vs Load)",
        font: { size: 18 },
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: "Time",
          font: { size: 14 },
        },
        ticks: { maxRotation: 45, minRotation: 45 },
      },
      y: {
        title: {
          display: true,
          text: "Predicted Load (Wh)",
          font: { size: 14 },
        },
      },
    },
  };

  return (
    <div
      style={{
        maxWidth: "1000px",
        margin: "40px auto",
        padding: "30px",
        borderRadius: "12px",
        boxShadow: "0 0 18px rgba(0,0,0,0.15)",
        fontFamily: "Segoe UI, sans-serif",
        backgroundColor: "#ffffff",
      }}
    >
      <h2 style={{ textAlign: "center", marginBottom: "30px" }}>
        ⚡ AI-Based Load Forecasting Dashboard

      </h2>

      {/* Consumer Dropdown */}
      <select
        value={selectedConsumer}
        onChange={(e) => setSelectedConsumer(e.target.value)}
        style={{
          padding: "10px",
          width: "100%",
          marginBottom: "20px",
          fontSize: "15px",
        }}
      >
        <option value="">Select Consumer</option>
        {consumers.map((c) => (
          <option key={c} value={c}>
            {c}
          </option>
        ))}
      </select>

      {/* Button */}
      <button
        onClick={getForecast}
        disabled={!selectedConsumer}
        style={{
          padding: "12px",
          width: "100%",
          backgroundColor: "#ff9800",
          border: "none",
          color: "white",
          fontSize: "16px",
          borderRadius: "6px",
          cursor: "pointer",
        }}
      >
        Get Forecast
      </button>

      {/* Output */}
      {forecast.length > 0 && (
        <>
          <h3 style={{ marginTop: "35px" }}>Forecast Table</h3>

          {/* -------- TABLE -------- */}
          <table
            style={{
              width: "100%",
              borderCollapse: "collapse",
              marginTop: "15px",
            }}
          >
            <thead>
              <tr>
                <th style={thStyle}>Time</th>
                <th style={thStyle}>Predicted Load (Wh)</th>
              </tr>
            </thead>
            <tbody>
              {forecast.map((f, i) => (
                <tr key={i}>
                  <td style={tdStyle}>{f.time}</td>
                  <td style={tdStyle}>{f.predicted_load_wh}</td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* -------- LINE GRAPH -------- */}
          <div style={{ marginTop: "40px" }}>
            <Line data={chartData} options={chartOptions} />
          </div>
        </>
      )}
    </div>
  );
}

export default App;
