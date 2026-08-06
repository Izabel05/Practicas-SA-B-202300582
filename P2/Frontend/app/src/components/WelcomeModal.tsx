import { useAuthFeedback } from "../context/AuthFeedbackContext";
import "./modal.css";

export default function WelcomeModal() {
  const {
    welcomeData,
    hideWelcome,
  } = useAuthFeedback();

  if (!welcomeData) {
    return null;
  }

  const isAdmin = welcomeData.role === "ADMIN";

  const title = isAdmin
    ? "Bienvenido, administrador"
    : "Bienvenido, usuario";

  const message = isAdmin
    ? "Ha ingresado con permisos de administrador."
    : "Ha ingresado correctamente al sistema.";

  return (
    <div
      className="modal-overlay"
      role="dialog"
      aria-modal="true"
      aria-labelledby="welcome-title"
    >
      <section className="modal-card">
        <h2 id="welcome-title">{title}</h2>

        <p>
          Hola, {welcomeData.firstName}. {message}
        </p>

        <button type="button" onClick={hideWelcome}>
          Continuar
        </button>
      </section>
    </div>
  );
}