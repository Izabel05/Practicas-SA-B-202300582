import { useNavigate } from "react-router-dom";

import { useAuthFeedback } from "../context/AuthFeedbackContext";
import "./modal.css";

export default function SessionExpiredModal() {
  const navigate = useNavigate();

  const {
    sessionExpired,
    hideSessionExpired,
  } = useAuthFeedback();

  if (!sessionExpired) {
    return null;
  }

  function handleAccept(): void {
    sessionStorage.removeItem("authenticated_user");

    hideSessionExpired();

    navigate("/login", {
      replace: true,
    });
  }

  return (
    <div
      className="modal-overlay"
      role="dialog"
      aria-modal="true"
      aria-labelledby="session-expired-title"
    >
      <section className="modal-card">
        <h2 id="session-expired-title">
          Sesión expirada
        </h2>

        <p>
          Su sesión ha expirado. Inicie sesión nuevamente
          para continuar.
        </p>

        <button type="button" onClick={handleAccept}>
          Aceptar
        </button>
      </section>
    </div>
  );
}