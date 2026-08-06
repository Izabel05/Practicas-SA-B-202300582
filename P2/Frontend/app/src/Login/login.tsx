import {
  type ChangeEvent,
  type FormEvent,
  useState,
} from "react";
import {
  Link,
  useLocation,
  useNavigate,
} from "react-router-dom";

import { iniciarSesion } from "../services/auth.service";
import type {
  AuthenticatedUser,
  LoginSchema,
} from "../types/auth";
import "./login.css";
import { useAuthFeedback } from "../context/AuthFeedbackContext";

const initialForm: LoginSchema = {
  email: "",
  password: "",
};

interface LocationState {
  message?: string;
}

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();

  const { showWelcome } = useAuthFeedback();
  const locationState =
    location.state as LocationState | null;

  const [form, setForm] =
    useState<LoginSchema>(initialForm);

  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  function handleChange(
    event: ChangeEvent<HTMLInputElement>,
  ): void {
    const { name, value } = event.target;

    setForm((currentForm) => ({
      ...currentForm,
      [name]: value,
    }));
  }

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ): Promise<void> {
    event.preventDefault();

    setError("");
    setIsLoading(true);

    try {
      const result = await iniciarSesion(form);

      const user: AuthenticatedUser = result.user;

      sessionStorage.setItem(
        "authenticated_user",
        JSON.stringify(user),
      );
    showWelcome({
      firstName: result.user.first_name,
      role: result.user.role,
    });

      navigate("/home", {
        replace: true,
      });
    } catch (requestError: unknown) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "No fue posible iniciar sesión.",
      );
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-card">
        <h1>Iniciar sesión</h1>

        {locationState?.message && (
          <p className="success-message">
            {locationState.message}
          </p>
        )}

        <form onSubmit={handleSubmit}>
          <input
            name="email"
            type="email"
            placeholder="Correo"
            value={form.email}
            onChange={handleChange}
            required
          />

          <input
            name="password"
            type="password"
            placeholder="Contraseña"
            value={form.password}
            onChange={handleChange}
            required
          />

          <button type="submit" disabled={isLoading}>
            {isLoading
              ? "Ingresando..."
              : "Ingresar"}
          </button>
        </form>

        {error && <p className="error-message">{error}</p>}

        <p>
          ¿No tienes cuenta?{" "}
          <Link to="/registro">Regístrate</Link>
        </p>
      </section>
    </main>
  );
}