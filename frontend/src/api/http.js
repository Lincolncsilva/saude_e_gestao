import axios from "axios";

export const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
  timeout: 20000,
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
    return Promise.reject({ status, msg, raw: err });
  }
);
