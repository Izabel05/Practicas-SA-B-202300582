import { api } from "./api";

export interface HistoryItem {
  id: number;
  action: string;
  date: string;
}

export interface HistoryResponse {
  message: string;
  items: HistoryItem[];
}

export async function getHistory(): Promise<HistoryResponse> {
  const response = await api.get<HistoryResponse>(
    "/protected/ruta-2",
  );

  return response.data;
}