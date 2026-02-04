// frontend/src/api/http.js
import axios from "axios";

// Para Docker, usar /api como base (Nginx faz proxy)
// Para desenvolvimento local, manter localhost:8000
const baseURL = import.meta.env.SSR || import.meta.env.PROD
  ? (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000")
  : '';  // ← No navegador, use proxy

export const http = axios.create({
  baseURL,
  timeout: 30000,
});

http.interceptors.response.use(
  (r) => r,
  (err) => {
    const status = err?.response?.status;
    const msg =
      err?.response?.data?.detail ||
      err?.response?.data?.message ||
      err?.message ||
      "Erro desconhecido";
    
    // Log útil para debug em Docker
    if (import.meta.env.DEV) {
      console.error("API Error:", {
        status,
        msg,
        url: err.config?.url,
        baseURL: err.config?.baseURL
      });
    }
    
    return Promise.reject({ status, msg, raw: err });
  }
);