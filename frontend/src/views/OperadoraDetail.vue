<template>
  <div class="page">
    <header class="topbar">
      <button class="btn" @click="router.push('/')">← Voltar</button>
      <div class="chip mono">CNPJ: {{ formatCnpj(cnpj) }}</div>
      <button class="btn" @click="refresh" :disabled="loadingAny">Atualizar</button>
    </header>

    <UiState :loading="loadingAny" :error="errorAny" :empty="!loadingAny && !store.detail">
      <div class="grid">
        <section class="card">
          <div class="sectionTitle">Dados da Operadora</div>

          <div class="kv">
            <div class="k">Razão Social</div><div class="v">{{ store.detail?.razao_social }}</div>
            <div class="k">Modalidade</div><div class="v">{{ store.detail?.modalidade }}</div>
            <div class="k">Registro ANS</div><div class="v">{{ store.detail?.registro_operadora }}</div>
            <div class="k">UF</div><div class="v">{{ store.detail?.uf }}</div>
            <div class="k">Cidade</div><div class="v">{{ store.detail?.cidade }}</div>
            <div class="k">E-mail</div><div class="v">{{ store.detail?.endereco_eletronico }}</div>
            <div class="k">Telefone</div><div class="v">{{ formatPhone(store.detail?.ddd, store.detail?.telefone) }}</div>
          </div>

          <div class="divider"></div>

          <div class="sectionTitle">Endereço</div>
          <div class="muted">
            {{ store.detail?.logradouro }}, {{ store.detail?.numero }} {{ store.detail?.complemento ? `- ${store.detail?.complemento}` : "" }}<br/>
            {{ store.detail?.bairro }} • CEP {{ store.detail?.cep }}
          </div>

          <div class="divider"></div>

          <div class="sectionTitle">Representante</div>
          <div class="muted">
            {{ store.detail?.representante }} • {{ store.detail?.cargo_representante }}
          </div>
        </section>

        <section class="card">
          <div class="sectionTitle">Histórico de Despesas</div>
          

          <table>
            <thead>
              <tr>
                <th>Ano</th>
                <th>Trimestre</th>
                <th>Valor</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="d in orderedDespesas" :key="d.ano + '-' + d.trimestre">
                <td>{{ d.ano }}</td>
                <td>T{{ d.trimestre }}</td>
                <td>{{ money(d.valor_despesas) }}</td>
              </tr>
            </tbody>
          </table>

          <div v-if="orderedDespesas.length === 0" class="muted" style="margin-top:10px;">
            Sem despesas registradas para esta operadora.
          </div>
        </section>
      </div>
    </UiState>
  </div>
</template>

<script setup>
import { computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useOperadorasStore } from "../stores/operadoras.store";
import UiState from "../components/UiState.vue";

const store = useOperadorasStore();
const route = useRoute();
const router = useRouter();

const cnpj = route.params.cnpj;

const loadingAny = computed(() => store.loadingDetail || store.loadingDespesas);
const errorAny = computed(() => store.errorDetail || store.errorDespesas);

onMounted(async () => {
  await Promise.all([store.fetchDetail(cnpj), store.fetchDespesas(cnpj)]);
});

function refresh() {
  store.fetchDetail(cnpj);
  store.fetchDespesas(cnpj);
}

const orderedDespesas = computed(() => {
  const arr = store.despesas || [];
  // ordena desc: ano, trimestre
  return [...arr].sort((a, b) => (b.ano - a.ano) || (b.trimestre - a.trimestre));
});

function money(v) {
  const n = Number(v || 0);
  return n.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function formatPhone(ddd, tel) {
  if (!tel) return "";
  const d = ddd ? `(${ddd}) ` : "";
  return d + String(tel);
}

function formatCnpj(v) {
  const d = String(v || "").replace(/\D/g, "");

  if (d.length !== 14) return v; // fallback se vier incompleto

  return d.replace(
    /^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/,
    "$1.$2.$3/$4-$5"
  );
}

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
  display:flex; align-items:center; gap:10px; flex-wrap:wrap;
  background: rgba(255,255,255,0.82);
  border: 1px solid var(--stroke);
  border-radius: 22px;
  padding: 14px 16px;
  box-shadow: 0 18px 50px rgba(32, 24, 64, 0.10);
  backdrop-filter: blur(10px);
  margin-bottom: 14px;
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
.btn:disabled { opacity: 0.6; cursor: not-allowed; }
.chip {
  border: 1px solid var(--stroke);
  background: #fff;
  color: var(--muted);
  font-size: 12px;
  padding: 8px 10px;
  border-radius: 999px;
}
.mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; }

.grid {
  display:grid;
  grid-template-columns: 1fr 1.1fr;
  gap: 14px;
}
@media (max-width: 980px){ .grid{ grid-template-columns: 1fr; } }

.card {
  background:#fff;
  border:1px solid var(--stroke);
  border-radius:22px;
  padding: 14px 16px 16px;
  box-shadow: 0 10px 30px rgba(32, 24, 64, 0.08);
}
.sectionTitle { font-weight: 900; margin-bottom: 8px; }
.subtitle { color: var(--muted); font-size: 12px; margin-top: -4px; margin-bottom: 10px; }

.kv {
  display:grid;
  grid-template-columns: 160px 1fr;
  gap: 8px 12px;
}
.k { color: var(--muted); font-size: 12px; }
.v { font-weight: 700; font-size: 13px; }

.divider { height: 1px; background: var(--stroke); margin: 12px 0; }
.muted { color: var(--muted); font-size: 12px; line-height: 1.5; }

table { width:100%; border-collapse:collapse; margin-top: 10px; }
th, td { border-top: 1px solid var(--stroke); padding: 10px; text-align:left; }
th { color: var(--muted); font-size: 12px; }
</style>
