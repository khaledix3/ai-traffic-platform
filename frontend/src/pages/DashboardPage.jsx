import PredictionForm from "../components/PredictionForm";
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

  const [weatherOptions, setWeatherOptions] = useState([]);
  const [dateRange, setDateRange] = useState(null);

  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [weather, setWeather] = useState("");

  const [filtering, setFiltering] = useState(false);
  const [error, setError] = useState("");

  async function loadTrafficData(params = {}) {
    const [
      summaryResponse,
      hourlyResponse,
      weekdayResponse,
      weatherResponse,
    ] = await Promise.all([
      api.get("/traffic/filter-summary", { params }),
      api.get("/traffic/hourly", { params }),
      api.get("/traffic/weekday", { params }),
      api.get("/traffic/weather", { params }),
    ]);

    setSummary(summaryResponse.data);
    setHourlyTraffic(hourlyResponse.data);
    setWeekdayTraffic(weekdayResponse.data);
    setWeatherTraffic(weatherResponse.data);
  }

  useEffect(() => {
    async function loadDashboard() {
      try {
        const [
          weatherOptionsResponse,
          dateRangeResponse,
        ] = await Promise.all([
          api.get("/traffic/weather-options"),
          api.get("/traffic/date-range"),
        ]);

        setWeatherOptions(
          weatherOptionsResponse.data.weather_options
        );

        setDateRange(dateRangeResponse.data);

        await loadTrafficData();
      } catch {
        setError("Could not load traffic data");
      }
    }

    loadDashboard();
  }, []);

  async function applyFilters(event) {
    event.preventDefault();

    try {
      setFiltering(true);
      setError("");

      const params = {};

      if (startDate) {
        params.start_date = `${startDate}T00:00:00`;
      }

      if (endDate) {
        params.end_date = `${endDate}T23:59:59`;
      }

      if (weather) {
        params.weather = weather;
      }

      await loadTrafficData(params);
    } catch (error) {
      if (error.response?.status === 400) {
        setError(
          error.response.data.detail ||
            "Invalid filter values"
        );
      } else {
        setError("Could not apply filters");
      }
    } finally {
      setFiltering(false);
    }
  }

  async function resetFilters() {
    try {
      setFiltering(true);
      setError("");

      setStartDate("");
      setEndDate("");
      setWeather("");

      await loadTrafficData();
    } catch {
      setError("Could not reset filters");
    } finally {
      setFiltering(false);
    }
  }

  function logout() {
    localStorage.removeItem("access_token");
    window.location.href = "/login";
  }

  const minimumDate = dateRange?.start_date?.slice(0, 10);
  const maximumDate = dateRange?.end_date?.slice(0, 10);

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div>
          <h1>Traffic Dashboard</h1>
          <p>AI Traffic Platform</p>
        </div>

        <button onClick={logout}>Logout</button>
      </header>
      <PredictionForm />
      
      <form className="filters-card" onSubmit={applyFilters}>
        <div className="filter-field">
          <label>Start Date</label>

          <input
            type="date"
            value={startDate}
            min={minimumDate}
            max={maximumDate}
            onChange={(event) =>
              setStartDate(event.target.value)
            }
          />
        </div>

        <div className="filter-field">
          <label>End Date</label>

          <input
            type="date"
            value={endDate}
            min={minimumDate}
            max={maximumDate}
            onChange={(event) =>
              setEndDate(event.target.value)
            }
          />
        </div>

        <div className="filter-field">
          <label>Weather</label>

          <select
            value={weather}
            onChange={(event) =>
              setWeather(event.target.value)
            }
          >
            <option value="">All Weather</option>

            {weatherOptions.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-actions">
          <button type="submit" disabled={filtering}>
            {filtering ? "Applying..." : "Apply Filters"}
          </button>

          <button
            type="button"
            className="secondary-button"
            onClick={resetFilters}
            disabled={filtering}
          >
            Reset
          </button>
        </div>
      </form>

      {error && (
        <div className="error-message">{error}</div>
      )}

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
              <strong>
                {summary.average_traffic_volume ?? "—"}
              </strong>
            </div>

            <div className="summary-card">
              <span>Minimum Traffic</span>
              <strong>
                {summary.minimum_traffic_volume ?? "—"}
              </strong>
            </div>

            <div className="summary-card">
              <span>Maximum Traffic</span>
              <strong>
                {summary.maximum_traffic_volume ?? "—"}
              </strong>
            </div>
          </div>

          <div className="chart-card">
            <h2>Average Traffic by Hour</h2>

            <ResponsiveContainer width="100%" height={350}>
              <LineChart data={hourlyTraffic}>
                <CartesianGrid strokeDasharray="3 3" />

                <XAxis
                  dataKey="hour"
                  interval={0}
                />

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

                  <XAxis
                    dataKey="day"
                    interval={0}
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

            <div className="chart-card">
              <h2>Traffic by Weather</h2>

              <ResponsiveContainer width="100%" height={320}>
                <BarChart data={weatherTraffic}>
                  <CartesianGrid strokeDasharray="3 3" />

                  <XAxis
                    dataKey="weather"
                    interval={0}
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