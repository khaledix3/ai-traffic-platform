# AI Traffic Platform

A full-stack traffic analytics and machine-learning project built with **FastAPI**, **PostgreSQL**, **React**, and **NumPy**. The platform helps users explore historical traffic patterns and estimate hourly traffic volume from weather and time-related inputs.

> **Scope:** This project uses the historical **Metro Interstate Traffic Volume** dataset, representing an I-94 traffic station in the Minneapolis–St. Paul area. It is **not** a live traffic feed or a multi-city prediction system.

## Features

- User authentication with JWT-protected endpoints
- Interactive dashboard showing total records, average traffic, and minimum/maximum traffic volume
- Traffic analysis by hour, weekday, and weather condition
- Filters for date range and weather
- An AI prediction form that estimates traffic volume in **vehicles per hour**
- A Ridge Regression model trained using NumPy, with a time-based training/test split

## Technology stack

| Component | Technology |
| --- | --- |
| Frontend | React, Vite, Axios, Recharts |
| Backend API | Python, FastAPI, Pydantic |
| Database | PostgreSQL, SQLAlchemy, pg8000 |
| Authentication | JWT, password hashing |
| Data preparation | Pandas, NumPy, UCI ML Repository |
| Machine learning | Ridge Regression implemented with NumPy |

## Dataset and model

**Dataset:** UCI Machine Learning Repository — [Metro Interstate Traffic Volume](https://archive.ics.uci.edu/dataset/492/metro+interstate+traffic+volume)

The dataset contains **48,204 observations**, spanning **October 2012 to September 2018**. Inputs include date/time, temperature, precipitation, cloud coverage, weather conditions, and holidays. The target is hourly traffic volume.

The model uses a chronological training/test split and training-set preprocessing. Its recorded held-out evaluation results are:

| Metric | Result |
| --- | ---: |
| Mean Absolute Error (MAE) | 597.29 vehicles/hour |
| Root Mean Squared Error (RMSE) | 821.00 vehicles/hour |
| R² | 0.8256 |
| Baseline MAE | 1,722.45 vehicles/hour |

These results describe performance on this historical test split; they do not establish accuracy on live traffic, other roads, or other cities.

## Project structure

```text
ai-traffic-platform/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── security.py
│   │   ├── dependencies.py
│   │   ├── import_traffic_data.py
│   │   ├── train_model.py
│   │   ├── ml_service.py
│   │   ├── ml/
│   │   │   └── model_metadata.json
│   │   └── routers/
│   │       ├── traffic.py
│   │       └── prediction.py
├── frontend/
│   └── src/
│       ├── components/PredictionForm.jsx
│       └── pages/DashboardPage.jsx
├── requirements.txt
└── README.md
```

## Local setup

### 1. Prerequisites

- Python (use a version compatible with the pinned dependencies)
- Node.js and npm
- PostgreSQL

### 2. Backend dependencies

Open a terminal in the project root. For Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

For macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

### 3. Database and environment

Create a local PostgreSQL database named `ai_traffic_db` (or adjust the database configuration). Create a `.env` file in the project root and configure the database connection **using the settings required by** `backend/app/database.py`.

The API also requires a strong JWT secret in the environment:

```env
JWT_SECRET_KEY=replace_with_a_random_secret_at_least_32_bytes_long
```

Generate a strong random secret with:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

**Never commit `.env`, real credentials, or signing secrets.** This README does not include real database credentials. Review `backend/app/database.py` and `backend/app/security.py` to confirm your local environment-variable names before running the application.

### 4. Load historical data and train the model

After database configuration, run from the project root:

```powershell
python -m backend.app.import_traffic_data
python -m backend.app.train_model
```

The second command generates the trained model file at `backend/app/ml/traffic_ridge_model.npz` and its metadata. **The `.npz` file is intentionally excluded from Git**, so running model training is required after cloning the repository.

> Depending on your local database initialization logic, you may need to create the database tables before importing records. Check `backend/app/models.py` and the import script if tables do not yet exist.

### 5. Start the backend

```powershell
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8001
```

Interactive API documentation: <http://127.0.0.1:8001/docs>

### 6. Start the frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open <http://localhost:5173> in your browser. Register or log in using the app's authentication endpoints, then open the dashboard.

For a production frontend build:

```powershell
npm run build
```

## API overview

**Authentication** is required for the protected traffic and prediction endpoints.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/traffic/summary` | Overall dataset statistics |
| GET | `/traffic/hourly` | Hourly traffic patterns |
| GET | `/traffic/peak-hours` | Busiest hours |
| GET | `/traffic/weekday` | Traffic by weekday |
| GET | `/traffic/weather` | Traffic by weather |
| GET | `/traffic/filter-summary` | Statistics for selected filters |
| GET | `/traffic/weather-options` | Weather filter choices |
| GET | `/traffic/date-range` | Available historical date range |
| POST | `/predict` | Estimate hourly traffic volume |

Example prediction request (with a valid JWT):

```json
{
  "date_time": "2018-05-15T16:00:00",
  "temp": 293.15,
  "rain_1h": 0,
  "snow_1h": 0,
  "clouds_all": 20,
  "weather_main": "Clear",
  "holiday": "None"
}
```

The prediction API accepts **temperature in Kelvin**; the React prediction form accepts **Celsius** and converts it to Kelvin before sending the request. Predictions are expressed in **vehicles per hour**.

## Security notes

- Use a long random `JWT_SECRET_KEY` for each deployment.
- Do not commit `.env`, access tokens, or private database information.
- Development credentials are for local testing only.
- Before any public deployment, review allowed CORS origins, authentication settings, and deployment secrets.

## Limitations and future work

This is a portfolio and educational project based on historical traffic data. The model does not ingest current sensor data and should not be used as a real-time traffic-control or navigation decision system. Future work could include newer data, model monitoring, and deployment automation.
