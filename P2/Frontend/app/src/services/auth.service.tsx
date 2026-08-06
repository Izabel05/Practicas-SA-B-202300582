import axios from "axios";

import { api } from "./api";
import type {
  ApiError,
  AuthSchema,
  LoginSchema,
  RegistroSchema,
} from "../types/auth";

function getErrorMessage(error: unknown): string {
  if (!axios.isAxiosError<ApiError>(error)) {
    return "Ocurrió un error inesperado.";
  }

  const responseData = error.response?.data;

  if (responseData?.error?.message) {
    return responseData.error.message;
  }

  if (typeof responseData?.detail === "string") {
    return responseData.detail;
  }

  if (Array.isArray(responseData?.detail)) {
    return responseData.detail
      .map((item) => item.msg)
      .join(", ");
  }

  return "No fue posible completar la solicitud.";
}

export async function registrarUsuario(
  schema: RegistroSchema,
): Promise<AuthSchema> {
  try {
    const response = await api.post<AuthSchema>(
      "/auth/register",
      schema,
    );

    return response.data;
  } catch (error: unknown) {
    throw new Error(getErrorMessage(error));
  }
}

export async function iniciarSesion(
  schema: LoginSchema,
): Promise<AuthSchema> {
  try {
    const response = await api.post<AuthSchema>(
      "/auth/login",
      schema,
    );

    return response.data;
  } catch (error: unknown) {
    throw new Error(getErrorMessage(error));
  }
}

export async function renovarSesion(): Promise<void> {
  try {
    await api.post("/auth/refresh");
  } catch (error: unknown) {
    throw new Error(getErrorMessage(error));
  }
}