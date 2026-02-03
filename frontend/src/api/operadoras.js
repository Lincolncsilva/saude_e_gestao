import { http } from "./http";

/**
 * GET /api/operadoras?page=&limit=
 * Retorno: { data: [...], meta: { total, page, limit, total_pages } }
 */
export async function getOperadoras({ page = 1, limit = 10, q = "", has_despesas = true }) {
  const params = { page, limit, has_despesas };
  if (q && q.trim()) params.q = q.trim();

  const { data } = await http.get("/api/operadoras", { params });
  return data;
}


/**
 * GET /api/operadoras/{cnpj}
 */
export async function getOperadora(cnpj) {
  const { data } = await http.get(`/api/operadoras/${encodeURIComponent(cnpj)}`);
  return data;
}

/**
 * GET /api/operadoras/{cnpj}/despesas
 * Retorno: Array<{ ano, trimestre, valor_despesas, ... }>
 */
export async function getDespesasOperadora(cnpj) {
  const { data } = await http.get(`/api/operadoras/${encodeURIComponent(cnpj)}/despesas`);
  return data;
}

/**
 * GET /api/estatisticas
 * Retorno: Array<{ uf, total_despesas, ... }>
 */
export async function getEstatisticas() {
  const { data } = await http.get("/api/estatisticas");
  return data;
}
