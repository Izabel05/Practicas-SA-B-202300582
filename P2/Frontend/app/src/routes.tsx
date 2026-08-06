import {
  Navigate,
  Route,
  Routes,
} from "react-router-dom";

import Home from "./Home/home";
import Login from "./Login/login";
import Registro from "./Registro/registro";

export default function AppRoutes() {
  return (
    <Routes>
      <Route
        path="/"
        element={<Navigate to="/login" replace />}
      />

      <Route path="/login" element={<Login />} />

      <Route
        path="/registro"
        element={<Registro />}
      />

      <Route path="/home" element={<Home />} />

      <Route
        path="*"
        element={<Navigate to="/login" replace />}
      />
    </Routes>
  );
}