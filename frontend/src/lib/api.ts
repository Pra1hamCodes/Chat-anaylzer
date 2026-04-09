import axios from "axios";

export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  timeout: 60_000,
});

export async function uploadFile(file: File): Promise<{ session_id: string; status: string }> {
  const form = new FormData();
  form.append("file", file);
  const { data } = await api.post("/api/v1/upload", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function getStatus(sid: string) {
  const { data } = await api.get(`/api/v1/analysis/${sid}/status`);
  return data as { session_id: string; status: "pending" | "processing" | "done" | "error"; error: string | null };
}

async function fetchJSON<T>(sid: string, path: string): Promise<T> {
  const { data } = await api.get(`/api/v1/analysis/${sid}/${path}`);
  return data as T;
}

export const fetchOverview = (sid: string) => fetchJSON<any>(sid, "overview");
export const fetchUsers = (sid: string) => fetchJSON<any>(sid, "users");
export const fetchTemporal = (sid: string) => fetchJSON<any>(sid, "temporal");
export const fetchNLP = (sid: string) => fetchJSON<any>(sid, "nlp");
export const fetchNetwork = (sid: string) => fetchJSON<any>(sid, "network");
export const fetchEngagement = (sid: string) => fetchJSON<any>(sid, "engagement");
export const fetchRetention = (sid: string) => fetchJSON<any>(sid, "retention");

export function exportUrl(sid: string, fmt: "pdf" | "csv" | "html") {
  return `${api.defaults.baseURL}/api/v1/export/${sid}/${fmt}`;
}
