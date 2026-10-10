import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import api from "../api";

function DashboardPage() {
  const [summary, setSummary] = useState(null);
  const [hourlyTraffic, setHourlyTraffic] = useState([]);
  const [weekdayTraffic, setWeekdayTraffic] = useState([]);
  const [weatherTraffic, setWeatherTraffic] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadDashboard() {
      try {
        const [
          summaryResponse,
          hourlyResponse,
          weekdayResponse,
          weatherResponse,
        ] = await Promise.all([
          api.get("/traffic/summary"),
          api.get("/traffic/hourly"),
          api.get("/traffic/weekday"),
          api.get("/traffic/weather"),
        ]);

        setSummary(summaryResponse.data);
        setHourlyTraffic(hourlyResponse.data);
        setWeekdayTraffic(weekdayResponse.data);
        setWeatherTraffic(weatherResponse.data);
      } catch {
        setError("Could not load traffic data");
      }
    }

    loadDashboard();
  }, []);

  function logout() {
    localStorage.removeItem("access_token");
    window.location.href = "/login";
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div>
          <h1>Traffic Dashboard</h1>
          <p>AI Traffic Platform</p>
        </div>

        <button onClick={logout}>Logout</button>
      </header>

      {error && <div className="error-message">{error}</div>}

      {!summary ? (
        <p>Loading traffic data...</p>
      ) : (
        <>
          <div className="summary-grid">
            <div className="summary-card">
              <span>Total Records</span>
              <strong>{summary.total_records}</strong>
            </div>

            <div className="summary-card">
              <span>Average Traffic</span>
              <strong>{summary.average_traffic_volume}</strong>
            </div>

            <div className="summary-card">
              <span>Minimum Traffic</span>
              <strong>{summary.minimum_traffic_volume}</strong>
            </div>

            <div className="summary-card">
              <span>Maximum Traffic</span>
              <strong>{summary.maximum_traffic_volume}</strong>
            </div>
          </div>

          <div className="chart-card">
            <h2>Average Traffic by Hour</h2>

            <ResponsiveContainer width="100%" height={350}>
              <LineChart data={hourlyTraffic}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="hour" />
                <YAxis />
                <Tooltip />

                <Line
                  type="monotone"
                  dataKey="average_traffic_volume"
                  name="Average Traffic"
                  stroke="#2563eb"
                  strokeWidth={3}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="charts-grid">
            <div className="chart-card">
              <h2>Traffic by Weekday</h2>

              <ResponsiveContainer width="100%" height={320}>
                <BarChart data={weekdayTraffic}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="day" />
                  <YAxis />
                  <Tooltip />

                  <Bar
                    dataKey="average_traffic_volume"
                    name="Average Traffic"
                    fill="#2563eb"
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="chart-card">
              <h2>Traffic by Weather</h2>

              <ResponsiveContainer width="100%" height={320}>
                <BarChart data={weatherTraffic}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="weather"
                    angle={-35}
                    textAnchor="end"
                    height={75}
                  />
                  <YAxis />
                  <Tooltip />

                  <Bar
                    dataKey="average_traffic_volume"
                    name="Average Traffic"
                    fill="#2563eb"
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default DashboardPage;