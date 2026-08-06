import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";

import { getHistory } from "../services/history.service";
import type { AuthenticatedUser } from "../types/auth";
import "./home.css";

function getAuthenticatedUser(): AuthenticatedUser | null {
  const storedUser = sessionStorage.getItem(
    "authenticated_user",
  );

  if (!storedUser) {
    return null;
  }

  try {
    return JSON.parse(storedUser) as AuthenticatedUser;
  } catch {
    sessionStorage.removeItem("authenticated_user");
    return null;
  }
}

export default function Home() {
  const navigate = useNavigate();
  const user = getAuthenticatedUser();

  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  async function handleViewHistory(): Promise<void> {
    setMessage("");
    setIsLoading(true);

    try {
      const result = await getHistory();

      setMessage(result.message);
    } catch (error: unknown) {
      setMessage(
        error instanceof Error
          ? error.message
          : "No fue posible obtener el historial.",
      );
    } finally {
      setIsLoading(false);
    }
  }

  function handleLogout(): void {
    sessionStorage.removeItem("authenticated_user");

    navigate("/login", {
      replace: true,
    });
  }

  const roleLabel =
    user.role === "ADMIN"
      ? "Administrador"
      : "Cliente";

  return (
    <main className="dashboard-page">
      <header className="dashboard-header">
        <div>
          <p className="dashboard-eyebrow">
            Panel principal
          </p>

          <h1>
            Hola, {user.first_name}
          </h1>

          <p className="dashboard-subtitle">
            Bienvenido nuevamente al sistema.
          </p>
        </div>

        <div className="dashboard-user">
          <div className="user-avatar">
            {user.first_name.charAt(0).toUpperCase()}
          </div>

          <div>
            <strong>
              {user.first_name} {user.last_name}
            </strong>

            <span>{roleLabel}</span>
          </div>
        </div>
      </header>

      <section className="dashboard-grid">
        <article className="dashboard-card profile-card">
          <div className="card-icon">
            
          </div>

          <div>
            <h2>Información de cuenta</h2>

            <p>
              Consulta los datos asociados a tu sesión.
            </p>
          </div>

          <dl className="profile-data">
            <div>
              <dt>Correo</dt>
              <dd>{user.email}</dd>
            </div>

            <div>
              <dt>Rol</dt>
              <dd>
                <span className="role-badge">
                  {roleLabel}
                </span>
              </dd>
            </div>
          </dl>
        </article>

        <article className="dashboard-card history-card">
          <div className="card-icon history-icon">
            
          </div>

          <div>
            <h2>Historial</h2>

            <p>
              Consulta la actividad registrada en tu cuenta.
            </p>
          </div>

          <button
            className="primary-action"
            type="button"
            onClick={handleViewHistory}
            disabled={isLoading}
          >
            {isLoading
              ? "Consultando..."
              : "Ver historial"}
          </button>

          {message && (
            <div className="dashboard-message">
              {message}
            </div>
          )}
        </article>

        {user.role === "ADMIN" && (
          <article className="dashboard-card admin-card">
            <div className="card-icon admin-icon">
              
            </div>

            <div>
              <h2>Panel administrativo</h2>

              <p>
                Acceso disponible únicamente para administradores.
              </p>
            </div>

            <button
              className="secondary-action"
              type="button"
              onClick={() => {
                navigate("/admin");
              }}
            >
              Ir al panel
            </button>
          </article>
        )}
      </section>

      <footer className="dashboard-footer">
        <p>
          Sesión iniciada como{" "}
          <strong>{roleLabel}</strong>
        </p>

        <button
          className="logout-button"
          type="button"
          onClick={handleLogout}
        >
          Cerrar sesión
        </button>
      </footer>
    </main>
  );
}