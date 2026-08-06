import {
  type ChangeEvent,
  type FormEvent,
  useState,
} from "react";
import { Link, useNavigate } from "react-router-dom";

import { registrarUsuario } from "../services/auth.service";
import type { RegistroSchema } from "../types/auth";
import "./registro.css";

const initialForm: RegistroSchema = {
  first_name: "",
  last_name: "",
  email: "",
  password: "",
  password_confirmation: "",
};

export default function Registro() {
  const navigate = useNavigate();

  const [form, setForm] =
    useState<RegistroSchema>(initialForm);

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
      await registrarUsuario(form);

      navigate("/login", {
        state: {
          message:
            "Usuario registrado correctamente. Ahora inicia sesión.",
        },
      });
    } catch (requestError: unknown) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "No fue posible registrar al usuario.",
      );
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-card">
        <h1>Crear cuenta</h1>

        <form onSubmit={handleSubmit}>
          <input
            name="first_name"
            placeholder="Nombre"
            value={form.first_name}
            onChange={handleChange}
            required
          />

          <input
            name="last_name"
            placeholder="Apellido"
            value={form.last_name}
            onChange={handleChange}
            required
          />

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
            minLength={8}
            required
          />

          <input
            name="password_confirmation"
            type="password"
            placeholder="Confirmar contraseña"
            value={form.password_confirmation}
            onChange={handleChange}
            minLength={8}
            required
          />

          <button type="submit" disabled={isLoading}>
            {isLoading
              ? "Registrando..."
              : "Registrarse"}
          </button>
        </form>

        {error && <p className="error-message">{error}</p>}

        <p>
          ¿Ya tienes una cuenta?{" "}
          <Link to="/login">Inicia sesión</Link>
        </p>
      </section>
    </main>
  );
}