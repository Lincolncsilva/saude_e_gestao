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
          <span class="label">API {{ apiOnline ? 'Online' : 'Offline' }}</span>
        </div>

        <button class="btn" @click="refreshAll" :disabled="anyLoading">
          Atualizar
        </button>
      </div>
    </header>

    <!-- STATES -->
    <UiState :loading="anyLoading" :error="anyError" :empty="false">
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
        <div class="ufWrap">
          <UfHeatmapMap
            :dataByUf="ufTotalsObj"
            :selectedUf="selectedUf"
            @selectUf="onSelectUf"
          />

          <!-- POPOVER (balão) em cima do mapa -->
          <div
            v-if="ufPopover.open"
            class="ufPopover"
            :style="{ left: ufPopover.left + 'px', top: ufPopover.top + 'px' }"
          >
            <div class="ufPopHeader">
              <div class="ufPopTitle">{{ ufPopover.uf }}</div>

              <button class="ufPopClose" @click="closeUfPopover" aria-label="Fechar">
                ✕
              </button>
            </div>

            <div class="ufPopTotal">
              Total: <b>{{ money(ufTotal) }}</b>
            </div>

            <div class="ufPopList">
              <div v-if="loadingUfTop5" class="ufPopLoading">Carregando…</div>

              <div v-else-if="ufTop5.length === 0" class="ufPopEmpty">
                Sem despesas registradas para este estado.
              </div>

              <div v-else class="ufPopRows">
                <div class="ufRow" v-for="(r, idx) in ufTop5" :key="r.cnpj || idx">
                  <div class="ufRowLeft">
                    <div class="ufRowName">{{ r.razao_social }}</div>
                    <div class="ufRowCnpj">{{ formatCnpj(r.cnpj) }}</div>
                  </div>
                  <div class="ufRowVal">{{ money(r.total) }}</div>
                </div>
              </div>
            </div>

            <!-- Seta condicional -->
            <div 
              class="ufArrow" 
              :class="{ 
                'left': ufPopover.opensLeft,
                'top': ufPopover.opensTop 
              }"
            ></div>
          </div>
        </div>

        <!-- Linha 2 esquerda: Histórico Trimestral -->
        <QuarterlyTrendBar
          :series="selectedSeries"
          :label="selectedOp?.razao_social || ''"
        />

        <!-- Linha 2 direita: Ranking por UF selecionada -->
        <Top5Rank :stats="store.stats" />
      </main>
    </UiState>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { useOperadorasStore } from "../stores/operadoras.store";
import { http } from "@/api/http";

import UiState from "../components/UiState.vue";
import OperatorsTable from "../components/OperatorsTable.vue";
import UfHeatmapMap from "../components/UfHeatmapMap.vue";
import QuarterlyTrendBar from "../components/QuarterlyTrendBar.vue";
import Top5Rank from "../components/Top5Rank.vue";


// ---------------- API STATUS ----------------
const apiOnline = ref(false);
const logo = '/lotus_SG.png';
async function checkApi() {
  try {
    await http.get("/api/estatisticas", { timeout: 3000 });    
    apiOnline.value = true;
  } catch {
    apiOnline.value = false;
  }
}

// ---------------- STORE / ROUTER ----------------
const store = useOperadorasStore();
const router = useRouter();

// ---------------- LOCAL STATE ----------------
const selectedOp = ref(null);
const selectedSeries = ref([]);
const lastQ = ref(""); // filtro server-side ativo

// ---- UF MAP STATE ----
const ufTotals = ref([]);   // [{ uf, total }]
const selectedUf = ref(""); // "SP"
const ufTop5 = ref([]);     // [{ operadora_id, razao_social, cnpj, total, ... }]
const ufTotal = ref(0);     // total do estado

// ---- UF POPOVER STATE ----
const ufPopover = ref({
  open: false,
  uf: "",
  left: 0,
  top: 0,
  opensLeft: false,   // se abre para a esquerda
  opensTop: false     // se abre para cima
});

const loadingUfTop5 = ref(false);

// ---------------- COMPUTEDS ----------------
const anyLoading = computed(() => store.loadingList || store.loadingStats);
const anyError = computed(() => store.errorList || store.errorStats);

// heatmap: transforma array -> { UF: total }
const ufTotalsObj = computed(() => {
  const obj = {};
  for (const it of ufTotals.value || []) {
    if (!it?.uf) continue;
    obj[it.uf] = Number(it.total || 0);
  }
  return obj;
});

// ---------------- HELPER FUNCTIONS ----------------
// Formatar CNPJ
function formatCnpj(cnpj) {
  if (!cnpj) return "";
  const cleaned = cnpj.toString().replace(/\D/g, '');
  if (cleaned.length === 14) {
    return cleaned.replace(
      /^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/,
      '$1.$2.$3/$4-$5'
    );
  }
  return cnpj;
}

// Formatar dinheiro
function money(v) {
  return Number(v || 0).toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  });
}

// Fechar popover
function closeUfPopover() {
  ufPopover.value.open = false;
  selectedUf.value = "";
  ufTop5.value = [];
  ufTotal.value = 0;
}

// ---------------- UF ENDPOINTS ----------------
async function fetchUfTotals() {
  const { data } = await http.get("/api/estatisticas/uf");
  ufTotals.value = Array.isArray(data) ? data : [];
}

// Clique no mapa - COM POPOVER INTELIGENTE (4 direções)
async function onSelectUf(data) {
  if (!data?.uf) return;
  
  const { uf, x, y } = data;
  selectedUf.value = uf;
  loadingUfTop5.value = true;
  
  // Dimensões do popover
  const popoverWidth = 320;
  const popoverHeight = 400;
  
  // Obter dimensões do container
  const container = document.querySelector('.ufWrap');
  if (!container) return;
  
  const containerRect = container.getBoundingClientRect();
  const containerWidth = containerRect.width;
  const containerHeight = containerRect.height;
  
  // Calcular posição inicial
  let left = x + 20;
  let top = y + 20;
  let opensLeft = false;
  let opensTop = false;
  
  // VERIFICAR BORDA DIREITA
  if (left + popoverWidth > containerWidth - 10) {
    left = x - popoverWidth - 10;
    opensLeft = true;
  }
  
  // VERIFICAR BORDA INFERIOR
  if (top + popoverHeight > containerHeight - 10) {
    top = y - popoverHeight - 10;
    opensTop = true;
  }
  
  // Ajustar se ainda sair (caso clique muito na borda)
  if (left < 10) {
    left = 10;
    opensLeft = false; // Forçar para direita
  }
  
  if (top < 10) {
    top = 10;
    opensTop = false; // Forçar para baixo
  }
  
  // Se abrir para esquerda e ainda couber na direita, melhor abrir na direita
  if (opensLeft && (x + popoverWidth + 20 < containerWidth)) {
    left = x + 20;
    opensLeft = false;
  }
  
  // Posicionar popover
  ufPopover.value = {
    open: true,
    uf: uf,
    left: left,
    top: top,
    opensLeft: opensLeft,
    opensTop: opensTop
  };
  
  try {
    const { data } = await http.get(`/api/estatisticas/uf/${encodeURIComponent(uf)}`);
    ufTop5.value = data?.top5 || [];
    ufTotal.value = Number(data?.total_uf || 0);
  } catch (error) {
    console.error("Erro ao buscar dados da UF:", error);
    ufTop5.value = [];
    ufTotal.value = 0;
  } finally {
    loadingUfTop5.value = false;
  }
}

// ---------------- LIFECYCLE ----------------
onMounted(async () => {
  checkApi();
  setInterval(checkApi, 30000);

  await Promise.all([
    store.fetchList(1, 10, lastQ.value),
    store.fetchStats(),
    fetchUfTotals(),
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

async function refreshAll() {
  await Promise.all([
    store.fetchList(store.meta.page, store.meta.limit, lastQ.value),
    store.fetchStats(),
    fetchUfTotals(),
  ]);

  if (selectedUf.value) {
    // Reabrir popover se estiver aberto
    if (ufPopover.value.open) {
      await onSelectUf({ uf: selectedUf.value, x: ufPopover.value.left, y: ufPopover.value.top });
    }
  }
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

// ---------------- DEBUG opcional ----------------
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
  background: linear-gradient(135deg, rgba(247,201,221,0.65), rgba(205,184,255,0.65));
  border: 1px solid rgba(142,107,255,0.18);
  display: grid;
  place-items: center;
  overflow: hidden;
}

.logoImage {
  width: 45px;
  height: 45px;
  object-fit: contain;
  display: block;
  transition: transform 0.2s ease, filter 0.2s ease;
}

.brandName { 
  font-weight: 900;
  font-size: 30px; 
}

.brandTag { 
  color: var(--muted); 
  font-size: 14px; 
  margin-top: 4px; 
}

.right { 
  display: flex; 
  gap: 10px; 
  align-items: center; 
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

.grid2 {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  grid-template-rows: auto auto;
  gap: 14px;
}

@media (max-width: 980px) {
  .grid2 { 
    grid-template-columns: 1fr; 
    grid-template-rows: auto; 
  }
}

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

/* UF WRAPPER */
.ufWrap {
  position: relative;
}

/* UF POPOVER STYLES */
.ufPopover {
  position: absolute;
  z-index: 1000;
  background: white;
  border: 1px solid var(--stroke);
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  width: 320px;
  max-height: 400px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.ufPopHeader {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: linear-gradient(180deg, rgba(233, 221, 255, 0.40), rgba(253, 232, 242, 0.18));
  border-bottom: 1px solid var(--stroke);
}

.ufPopTitle {
  font-weight: 900;
  font-size: 16px;
  color: #2c3e50;
}

.ufPopClose {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: #7f8c8d;
  line-height: 1;
  padding: 4px;
  border-radius: 4px;
  transition: background 0.2s;
}

.ufPopClose:hover {
  background: rgba(0, 0, 0, 0.05);
}

.ufPopTotal {
  padding: 10px 16px;
  background: #f8f9fa;
  border-bottom: 1px solid var(--stroke);
  font-size: 14px;
  color: #2c3e50;
}

.ufPopTotal b {
  color: #8e6bff;
}

.ufPopList {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

.ufPopLoading {
  padding: 30px;
  text-align: center;
  color: #7f8c8d;
  font-size: 14px;
}

.ufPopEmpty {
  padding: 30px 20px;
  text-align: center;
  color: #95a5a6;
  font-size: 14px;
}

.ufPopRows {
  padding: 0 8px;
}

.ufRow {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  border-bottom: 1px solid #f0f0f0;
  transition: background 0.2s;
}

.ufRow:hover {
  background: #f9f9ff;
}

.ufRowLeft {
  flex: 1;
  min-width: 0;
}

.ufRowName {
  font-weight: 600;
  font-size: 13px;
  color: #2c3e50;
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.ufRowCnpj {
  font-size: px;
  color: #7f8c8d;
}

.ufRowVal {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 13px;
  font-weight: 600;
  color: #2c3e50;
  margin-left: 12px;
}

/* Seta do popover - LADO DIREITO (padrão - aponta para direita) */
.ufArrow {
  position: absolute;
  top: 20px;
  left: -8px; /* Fora do popover à esquerda */
  width: 0;
  height: 0;
  border-top: 8px solid transparent;
  border-bottom: 8px solid transparent;
  border-right: 8px solid white;
}

/* Seta do popover - LADO ESQUERDO (aponta para esquerda) */
.ufArrow.left {
  left: auto;
  right: -8px; /* Fora do popover à direita */
  border-right: none;
  border-left: 8px solid white;
}

/* Seta do popover - PARTE SUPERIOR (aponta para cima) */
.ufArrow.top {
  top: auto;
  bottom: -8px;
  left: 20px;
  border-right: 8px solid transparent;
  border-left: 8px solid transparent;
  border-top: 8px solid white;
  border-bottom: none;
}

/* Ajustar posição se popover sair da tela (mobile) */
@media (max-width: 768px) {
  .ufPopover {
    width: 280px;
    max-height: 350px;
    transform: translateX(-50%);
    left: 50% !important;
    top: 50% !important;
    transform: translate(-50%, -50%);
  }
  
  .ufArrow {
    display: none;
  }
}
</style>
