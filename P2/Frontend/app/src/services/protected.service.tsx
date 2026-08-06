import { api } from "./api";

export interface ProtectedRouteResponse {
  message: string;
  role: "ADMIN" | "CLIENTE";
  user_id: string;
}

export async function getRutaUno(): Promise<ProtectedRouteResponse> {
  const response = await api.get<ProtectedRouteResponse>(
    "/protected/ruta-1",
  );

  return response.data;
}

export async function getRutaDos(): Promise<ProtectedRouteResponse> {
  const response = await api.get<ProtectedRouteResponse>(
    "/protected/ruta-2",
  );

  return response.data;
}