import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import {
  FiActivity,
  FiClock,
  FiLogOut,
  FiShield,
  FiUser,
} from "react-icons/fi";

import {
  getRutaDos,
  getRutaUno,
} from "../services/protected.service";
import type { AuthenticatedUser } from "../types/auth";
import "./home.css";

type MessageType = "success" | "error" | null;

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

  const [commonMessage, setCommonMessage] = useState("");
  const [commonMessageType, setCommonMessageType] =
    useState<MessageType>(null);

  const [adminMessage, setAdminMessage] = useState("");
  const [adminMessageType, setAdminMessageType] =
    useState<MessageType>(null);

  const [isCommonLoading, setIsCommonLoading] =
    useState(false);

  const [isAdminLoading, setIsAdminLoading] =
    useState(false);

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  const roleLabel =
    user.role === "ADMIN"
      ? "Administrador"
      : "Cliente";

  async function handleCommonAccess(): Promise<void> {
    setCommonMessage("");
    setCommonMessageType(null);
    setIsCommonLoading(true);

    try {
      const result = await getRutaDos();

      setCommonMessage(result.message);
      setCommonMessageType("success");
    } catch (error: unknown) {
      setCommonMessage(
        error instanceof Error
          ? error.message
          : "No fue posible acceder a la Ruta 2.",
      );

      setCommonMessageType("error");
    } finally {
      setIsCommonLoading(false);
    }
  }

  async function handleAdminAccess(): Promise<void> {
    setAdminMessage("");
    setAdminMessageType(null);
    setIsAdminLoading(true);

    try {
      const result = await getRutaUno();

      setAdminMessage(result.message);
      setAdminMessageType("success");
    } catch (error: unknown) {
      setAdminMessage(
        error instanceof Error
          ? error.message
          : "Acceso denegado para Ruta 1.",
      );

      setAdminMessageType("error");
    } finally {
      setIsAdminLoading(false);
    }
  }

  function handleLogout(): void {
    sessionStorage.removeItem("authenticated_user");

    navigate("/login", {
      replace: true,
    });
  }

  return (
    <main className="dashboard-page">
      <header className="dashboard-header">
        <div>
          <p className="dashboard-eyebrow">
            Panel principal
          </p>

          <h1>Hola, {user.first_name}</h1>

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
            <FiUser />
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

        <article className="dashboard-card common-card">
          <div className="card-icon common-icon">
            <FiActivity />
          </div>

          <div>
            <span className="route-label">
              Ruta 2
            </span>

            <h2>Acceso compartido</h2>

            <p>
              Esta sección está disponible para administradores
              y clientes.
            </p>
          </div>

          <div className="permission-list">
            <p>
              <strong>Administrador:</strong> acceso permitido
            </p>

            <p>
              <strong>Cliente:</strong> acceso permitido
            </p>
          </div>

          <button
            className="primary-action"
            type="button"
            onClick={handleCommonAccess}
            disabled={isCommonLoading}
          >
            <FiClock />

            {isCommonLoading
              ? "Consultando..."
              : "Ver historial"}
          </button>

          {commonMessage && (
            <div
              className={
                commonMessageType === "success"
                  ? "dashboard-message"
                  : "dashboard-message dashboard-error"
              }
            >
              {commonMessage}
            </div>
          )}
        </article>

        <article className="dashboard-card admin-card">
          <div className="card-icon admin-icon">
            <FiShield />
          </div>

          <div>
            <span className="route-label admin-route-label">
              Ruta 1
            </span>

            <h2>Acceso administrativo</h2>

            <p>
              Esta ruta comprueba si el usuario tiene permisos
              de administrador.
            </p>
          </div>

          <div className="permission-list">
            <p>
              <strong>Administrador:</strong> acceso permitido
            </p>

            <p>
              <strong>Cliente:</strong> acceso denegado
            </p>
          </div>

          <button
            className="admin-action"
            type="button"
            onClick={handleAdminAccess}
            disabled={isAdminLoading}
          >
            <FiShield />

            {isAdminLoading
              ? "Verificando..."
              : "Probar acceso a Ruta 1"}
          </button>

          {adminMessage && (
            <div
              className={
                adminMessageType === "success"
                  ? "dashboard-message"
                  : "dashboard-message dashboard-error"
              }
            >
              {adminMessage}
            </div>
          )}
        </article>
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
          <FiLogOut />
          Cerrar sesión
        </button>
      </footer>
    </main>
  );
}