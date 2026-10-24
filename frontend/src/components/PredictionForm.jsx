
import { useEffect, useState } from "react";
import api from "../api";

function PredictionForm() {
  const [dateTime, setDateTime] = useState("2018-05-15T16:00");
  const [temperature, setTemperature] = useState("20");
  const [rain, setRain] = useState("0");
  const [snow, setSnow] = useState("0");
  const [clouds, setClouds] = useState("20");
  const [weather, setWeather] = useState("Clear");

  const [weatherOptions, setWeatherOptions] = useState([]);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    async function loadWeatherOptions() {
      try {
        const response = await api.get("/traffic/weather-options");

        if (active) {
          setWeatherOptions(response.data.weather_options);
        }
      } catch {
        if (active) {
          setError("Could not load weather options.");
        }
      }
    }

    loadWeatherOptions();

    return () => {
      active = false;
    };
  }, []);

  async function handlePredict(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setPrediction(null);

    try {
      const response = await api.post("/predict", {
        date_time: `${dateTime}:00`,
        temp: Number(temperature) + 273.15,
        rain_1h: Number(rain),
        snow_1h: Number(snow),
        clouds_all: Number(clouds),
        weather_main: weather,
        holiday: "None",
      });

      setPrediction(response.data.predicted_traffic_volume);
    } catch (err) {
      setError(
        err.response?.status === 422
          ? "Please check the input values."
          : "Prediction failed. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="prediction-card">
      <h2>AI Traffic Prediction</h2>
      <p>Estimate traffic volume using our trained ML model.</p>

      <form className="prediction-grid" onSubmit={handlePredict}>
        <div className="filter-field">
          <label htmlFor="prediction-datetime">Date & Time</label>
          <input
            id="prediction-datetime"
            type="datetime-local"
            value={dateTime}
            onChange={(e) => setDateTime(e.target.value)}
            required
          />
        </div>

        <div className="filter-field">
          <label htmlFor="prediction-temp">Temperature (°C)</label>
          <input
            id="prediction-temp"
            type="number"
            min="-80"
            max="70"
            step="0.1"
            value={temperature}
            onChange={(e) => setTemperature(e.target.value)}
            required
          />
        </div>

        <div className="filter-field">
          <label htmlFor="prediction-weather">Weather</label>
          <select
            id="prediction-weather"
            value={weather}
            onChange={(e) => setWeather(e.target.value)}
          >
            {(weatherOptions.length ? weatherOptions : ["Clear"]).map(
              (option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              )
            )}
          </select>
        </div>

        <div className="filter-field">
          <label htmlFor="prediction-clouds">Cloud Cover (%)</label>
          <input
            id="prediction-clouds"
            type="number"
            min="0"
            max="100"
            value={clouds}
            onChange={(e) => setClouds(e.target.value)}
            required
          />
        </div>

        <div className="filter-field">
          <label htmlFor="prediction-rain">Rain (mm / hour)</label>
          <input
            id="prediction-rain"
            type="number"
            min="0"
            step="any"
            value={rain}
            onChange={(e) => setRain(e.target.value)}
            required
          />
        </div>

        <div className="filter-field">
          <label htmlFor="prediction-snow">Snow (mm / hour)</label>
          <input
            id="prediction-snow"
            type="number"
            min="0"
            step="any"
            value={snow}
            onChange={(e) => setSnow(e.target.value)}
            required
          />
        </div>

        <button type="submit" disabled={loading}>
          {loading ? "Predicting..." : "Predict Traffic"}
        </button>
      </form>

      {error && <p className="error-message" role="alert">{error}</p>}

      {prediction !== null && (
        <div className="prediction-result" role="status">
          <span>Estimated Traffic Volume</span>
          <strong>{prediction.toLocaleString()} vehicles/hour</strong>
          <p>Model estimate based on historical traffic patterns.</p>
        </div>
      )}
    </section>
  );
}

export default PredictionForm;
