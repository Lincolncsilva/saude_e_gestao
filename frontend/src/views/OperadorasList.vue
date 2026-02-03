<template>
  <div class="page">
    <!-- TOPBAR -->
    <header class="topbar">
      <div class="brand">
        <div class="logoMark">
          <img :src="logo" alt="Logo" class="logoImage" />
        </div>
        <div>
          <div class="brandName">Saúde e Gestão</div>
          <div class="brandTag">Operadoras • Despesas • Indicadores</div>
        </div>
      </div>

      <div class="right">
        <div class="apiStatus" :title="apiOnline ? 'API conectada' : 'API indisponível'">
          <span class="dot" :class="apiOnline ? 'ok' : 'fail'"></span>
          <span class="label">
            API {{ apiOnline ? 'Online' : 'Offline' }}
          </span>
        </div>

        <button class="btn" @click="refreshAll" :disabled="anyLoading">
          Atualizar
        </button>
      </div>
    </header>

    <!-- STATES -->
    <UiState
      :loading="anyLoading"
      :error="anyError"
      :empty="false"
    >
      <!-- GRID -->
      <main class="grid2">
        <!-- Linha 1 esquerda: Tabela -->
        <OperatorsTable
          :items="store.list"
          :meta="store.meta"
          :selectedCnpj="selectedOp?.cnpj || ''"
          v-model:search="store.search"
          :onlyWithData="store.onlyWithData"
          @page="onPage"
          @open="goDetail"
          @select="onSelect"
          @search="onSearch"
          
          @toggleOnlyWithData="onToggleOnlyWithData"
        />


        <!-- Linha 1 direita: Mapa -->
        <UfHeatmapMap :dataByUf="byUf" />

        <!-- Linha 2 esquerda: Histórico Trimestral -->
        <QuarterlyTrendBar
          :series="selectedSeries"
          :label="selectedOp?.razao_social || ''"
        />

        <!-- Linha 2 direita: Ranking -->
        <Top5Rank :stats="store.stats" />
      </main>
    </UiState>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { useOperadorasStore } from "../stores/operadoras.store";
import axios from "axios";

import UiState from "../components/UiState.vue";
import OperatorsTable from "../components/OperatorsTable.vue";
import UfHeatmapMap from "../components/UfHeatmapMap.vue";
import QuarterlyTrendBar from "../components/QuarterlyTrendBar.vue";
import Top5Rank from "../components/Top5Rank.vue";
import logo from "@/assets/lotus_SG.png"


const apiOnline = ref(false);

async function checkApi() {
  try {
    // usa o endpoint mais leve possível
    await axios.get("http://localhost:8000/api/estatisticas", { timeout: 3000 });
    apiOnline.value = true;
  } catch (e) {
    apiOnline.value = false;
  }
}

onMounted(() => {
  checkApi();
  // revalida a cada 30s
  setInterval(checkApi, 30000);
});
// ---------------- STORE / ROUTER ----------------
const store = useOperadorasStore();

watch(
  () => store.list,
  (val) => {
    console.log(
      "STORE LIST UPDATED:",
      "len =", val?.length,
      "first =", val?.[0]?.razao_social,
      "cnpj =", val?.[0]?.cnpj
    );
  }
);

const router = useRouter();

// ---------------- LOCAL STATE ----------------
const selectedOp = ref(null);
const selectedSeries = ref([]);
const lastQ = ref(""); // filtro server-side ativo

// ---------------- COMPUTEDS ----------------
const anyLoading = computed(
  () => store.loadingList || store.loadingStats
);

const anyError = computed(
  () => store.errorList || store.errorStats
);

// ---------------- LIFECYCLE ----------------
onMounted(async () => {
  await Promise.all([
    store.fetchList(1, 10, lastQ.value),
    store.fetchStats(),
  ]);
});

// ---------------- ACTIONS ----------------
function onSearch(normalizedQ) {
  lastQ.value = normalizedQ || "";
  store.fetchList(1, store.meta.limit, lastQ.value);
}

function onPage(p) {
  store.fetchList(p, store.meta.limit, lastQ.value);
}

function refreshAll() {
  store.fetchList(store.meta.page, store.meta.limit, lastQ.value);
  store.fetchStats();
}

function goDetail(cnpj) {
  router.push(`/operadoras/${encodeURIComponent(cnpj)}`);
}

function onToggleOnlyWithData(val) {
  store.setOnlyWithData(val);
}

// Seleção da tabela → carrega histórico trimestral
async function onSelect(op) {
  selectedOp.value = op;
  await store.fetchDespesas(op.cnpj);
  selectedSeries.value = store.despesas;
}

// ---------------- DERIVED DATA ----------------
// Agrega /api/estatisticas -> { UF: total }
const byUf = computed(() => {
  const obj = {};
  const arr = store.stats || [];

  for (const it of arr) {
    const uf = it.uf;
    if (!uf) continue;

    if (!obj[uf]) obj[uf] = 0;
    obj[uf] += Number(it.total_despesas || 0);
  }

  return obj;
});



</script>

<style scoped>
.page {
  min-height: 100vh;
  padding: 18px;
  background:
    radial-gradient(1200px 600px at 15% 0%, rgba(247, 201, 221, 0.22), transparent 55%),
    radial-gradient(900px 500px at 85% 15%, rgba(205, 184, 255, 0.20), transparent 55%),
    linear-gradient(180deg, #ffffff 0%, #ffffff 60%, #fbfbfe 100%);
}

/* TOPBAR */
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  background: rgba(255, 255, 255, 0.82);
  border: 1px solid var(--stroke);
  border-radius: 22px;
  padding: 14px 16px;
  box-shadow: 0 18px 50px rgba(32, 24, 64, 0.10);
  backdrop-filter: blur(10px);
  margin-bottom: 14px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logoMark {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  background: linear-gradient(
    135deg,
    rgba(247,201,221,0.65),
    rgba(205,184,255,0.65)
  );
  border: 1px solid rgba(142,107,255,0.18);
  display: grid;
  place-items: center;
}

.logoText {
  font-weight: 900;
  color: rgba(44,44,55,0.85);
}

.brandName {
  font-weight: 900;
}

.brandTag {
  color: var(--muted);
  font-size: 12px;
  margin-top: 4px;
}

.right {
  display: flex;
  gap: 10px;
  align-items: center;
}

.chip {
  border: 1px solid var(--stroke);
  background: #fff;
  color: var(--muted);
  font-size: 12px;
  padding: 8px 10px;
  border-radius: 999px;
}

.btn {
  padding: 10px 12px;
  border-radius: 14px;
  border: 1px solid var(--stroke);
  background: #fff;
  cursor: pointer;
  font-weight: 800;
  font-size: 12px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* GRID LAYOUT
   [Tabela | Mapa]
   [Barras | Top5]
*/
.grid2 {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  grid-template-rows: auto auto;
  gap: 14px;
}

.grid2 > :nth-child(1) {
  grid-column: 1;
  grid-row: 1;
}

.grid2 > :nth-child(2) {
  grid-column: 2;
  grid-row: 1;
}

.grid2 > :nth-child(3) {
  grid-column: 1;
  grid-row: 2;
}

.grid2 > :nth-child(4) {
  grid-column: 2;
  grid-row: 2;
}

@media (max-width: 980px) {
  .grid2 {
    grid-template-columns: 1fr;
    grid-template-rows: auto;
  }

  .grid2 > * {
    grid-column: auto;
    grid-row: auto;
  }
}
/* Toggle */

.toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 700;
  color: var(--muted);
  background: rgba(255,255,255,0.7);
  border: 1px solid var(--stroke);
  padding: 8px 12px;
  border-radius: 999px;
  cursor: pointer;
}

.toggle input {
  accent-color: #8e6bff;
  cursor: pointer;
}

/*Status da api*/

.apiStatus {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 999px;
  border: 1px solid var(--stroke);
  background: #fff;
  font-size: 12px;
  font-weight: 800;
  color: var(--muted);
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  box-shadow: 0 0 0 3px rgba(0,0,0,0.03);
}

.dot.ok {
  background: #22c55e;
  box-shadow: 0 0 6px rgba(34, 197, 94, 0.6);
}

.dot.fail {
  background: #ef4444;
  box-shadow: 0 0 6px rgba(239, 68, 68, 0.6);
}

.label {
  letter-spacing: 0.04em;
}

.logoMark {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  background: linear-gradient(
    135deg,
    rgba(247,201,221,0.65),
    rgba(205,184,255,0.65)
  );
  border: 1px solid rgba(142,107,255,0.18);
  display: grid;
  place-items: center;
  overflow: hidden; /* garante que não vaze */
}

.logoImage {
  width: 45px;      /* controla melhor que height */
  height: 45px;
  object-fit: contain;
  display: block;
  transition: transform 0.2s ease, filter 0.2s ease;
}



</style>
