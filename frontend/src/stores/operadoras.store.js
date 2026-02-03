import { defineStore } from "pinia";
import {
  getOperadoras,
  getOperadora,
  getDespesasOperadora,
  getEstatisticas,
} from "../api/operadoras";

export const useOperadorasStore = defineStore("operadoras", {
  state: () => ({
    // list
    list: [],
    meta: { total: 0, page: 1, limit: 10, total_pages: 0 },
    loadingList: false,
    errorList: null,

    // texto cru do input (não normaliza aqui)
    search: "",

    // ✅ FLAG: mostrar só operadoras com despesas
    onlyWithData: true,

    // stats
    stats: [],
    loadingStats: false,
    errorStats: null,

    // detail
    detail: null,
    loadingDetail: false,
    errorDetail: null,

    // despesas
    despesas: [],
    loadingDespesas: false,
    errorDespesas: null,

    // anti-race
    reqId: 0,
  }),

  actions: {
    async fetchList(page = this.meta.page, limit = this.meta.limit, qOverride = null) {
      const myReq = ++this.reqId;

      this.loadingList = true;
      this.errorList = null;

      try {
        const q = qOverride !== null ? qOverride : (this.search || "");
        const has_despesas = this.onlyWithData === true;

        // ✅ usa o flag de verdade
        const res = await getOperadoras({ page, limit, q, has_despesas });

        if (myReq !== this.reqId) return;

        this.list = res?.data ?? [];
        this.meta = res?.meta ?? { total: 0, page, limit, total_pages: 0 };
      } catch (e) {
        if (myReq !== this.reqId) return;
        this.errorList = e;
      } finally {
        if (myReq === this.reqId) this.loadingList = false;
      }
    },

    setSearch(term) {
      this.search = term || "";
      // sempre volta pra primeira página ao buscar
      this.fetchList(1, this.meta.limit, this.search);
    },

    // ✅ toggle da flag
    setOnlyWithData(val) {
      this.onlyWithData = !!val;
      this.fetchList(1, this.meta.limit, this.search);
    },

    async fetchStats() {
      this.loadingStats = true;
      this.errorStats = null;
      try {
        this.stats = await getEstatisticas();
      } catch (e) {
        this.errorStats = e;
      } finally {
        this.loadingStats = false;
      }
    },

    async fetchDetail(cnpj) {
      this.loadingDetail = true;
      this.errorDetail = null;
      try {
        this.detail = await getOperadora(cnpj);
      } catch (e) {
        this.errorDetail = e;
      } finally {
        this.loadingDetail = false;
      }
    },

    async fetchDespesas(cnpj) {
      this.loadingDespesas = true;
      this.errorDespesas = null;
      try {
        this.despesas = await getDespesasOperadora(cnpj);
      } catch (e) {
        this.errorDespesas = e;
      } finally {
        this.loadingDespesas = false;
      }
    },
  },
});
