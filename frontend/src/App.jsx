import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import DashboardPage from "./pages/DashboardPage";
import LoginPage from "./pages/LoginPage";
import "./App.css";

function App() {
  const token = localStorage.getItem("access_token");

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/login"
          element={
            token ? <Navigate to="/dashboard" /> : <LoginPage />
          }
        />

        <Route
          path="/dashboard"
          element={
            token ? <DashboardPage /> : <Navigate to="/login" />
          }
        />

        <Route
          path="*"
          element={
            <Navigate to={token ? "/dashboard" : "/login"} />
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;