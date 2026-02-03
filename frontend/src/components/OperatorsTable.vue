<template>
  <div class="card">
    <div class="sectionHeader">
      <div class="sectionTitle">Operadoras</div>
      

      <div class="actions">
        <input
          v-model="qModel"
          class="input"
          placeholder="Buscar (razão social ou CNPJ)"
        />

        <!-- TOGGLE: só com despesas -->
        <label class="toggle">
          <input
          type="checkbox"
          :checked="props.onlyWithData"
          @change="$emit('toggleOnlyWithData', $event.target.checked)"
        />
        <span>Somente c/ dados</span>
        </label>

        <div class="pager">
          <button
            class="btn"
            :disabled="meta.page <= 1"
            @click="$emit('page', meta.page - 1)"
          >
            Anterior
          </button>

          <span class="pageInfo">
            Página {{ meta.page }} / {{ meta.total_pages || "?" }}
          </span>

          <button
            class="btn"
            :disabled="!hasNext"
            @click="$emit('page', meta.page + 1)"
          >
            Próxima
          </button>
        </div>
      </div>
  </div>      
    <div class="tableWrap">
      <table>
        <thead>
          <tr>
            <th>CNPJ</th>
            <th>Razão Social</th>
            <th>UF</th>
            <th>Modalidade</th>
            <th></th>
          </tr>
        </thead>

        <tbody>
          <tr
            v-for="op in props.items"
            :key="op.cnpj"
            @click="$emit('select', op)"
            :class="{ selectedRow: op.cnpj === props.selectedCnpj }"
            style="cursor:pointer;"
          >

            <td class="mono">{{ formatCnpj(op.cnpj) }}</td>
            <td>{{ op.razao_social }}</td>
            <td>{{ op.uf }}</td>
            <td>{{ op.modalidade }}</td>
            <td>
              <button class="btnGhost" @click.stop="$emit('open', op.cnpj)">
                Detalhes
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="props.items.length === 0" class="emptyCenter">
        <div class="emptyBox">
         <div class="emptyTitle">Nenhum resultado encontrado</div>
         <div class="emptySubtitle">
           Tente ajustar o filtro ou buscar por outro CNPJ / razão social
         </div>
       </div>
     </div>
   </div>
  </div> 
</template>

<script setup>
import { computed, watch } from "vue";

/*Propriedade de seleção na tabela */
const props = defineProps({
  items: { type: Array, default: () => [] },
  meta: { type: Object, default: () => ({ page: 1, limit: 10, total: 0, total_pages: 0 }) },

  selectedCnpj: { type: String, default: "" },

  // ✅ faltavam essas duas
  search: { type: String, default: "" },
  onlyWithData: { type: Boolean, default: true },
});


const emit = defineEmits(["page", "open", "select", "search", "update:search"]);

// v-model controlado (o campo mostra exatamente o que o usuário digitou)
const qModel = computed({
  get: () => props.search ?? "",
  set: (v) => emit("update:search", v),
});

// -------- Normalização para enviar ao servidor (q) --------
const onlyDigits = (s) => String(s ?? "").replace(/\D/g, "");

const normalizeText = (s) =>
  String(s ?? "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "") // remove acentos
    .replace(/\s+/g, " ")            // normaliza espaços
    .trim();

function buildQ(raw) {
  const s = String(raw ?? "").trim();
  if (!s) return "";

  // Se contém dígitos suficientes, assume CNPJ (com ou sem máscara)
  const digits = onlyDigits(s);
  if (digits.length >= 5) return digits;

  // Caso contrário, usa texto normalizado para razão social
  return normalizeText(s);
}

// -------- Busca: debounce + anti-repetição --------
let t = null;
let lastQ = null;

function emitSearchNow() {
  const q = buildQ(props.search);

  // evita spam (ex.: apertar Enter várias vezes)
  if (q === lastQ) return;
  lastQ = q;

  emit("search", q);
}

function clear() {
  emit("update:search", "");
  lastQ = null;
  emit("search", "");
}

watch(
  () => props.search,
  () => {
    clearTimeout(t);
    t = setTimeout(() => {
      emitSearchNow();
    }, 350);
  }
);

// -------- Paginação --------
const hasNext = computed(() => {
  if (props.meta?.total_pages) return props.meta.page < props.meta.total_pages;
  return props.items.length === props.meta.limit;
});

// -------- Formatação CNPJ --------
const formatCnpj = (v) => {
  const d = onlyDigits(v);
  if (d.length !== 14) return d;
  return d.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/, "$1.$2.$3/$4-$5");
};


</script>

<style scoped>
.card {
  background: #fff;
  border: 1px solid var(--stroke);
  border-radius: 22px;
  overflow: hidden;
}

.sectionHeader {
  display: flex;
  align-items: center;              /* alinha verticalmente */
  justify-content: space-between;   /* título esquerda, ações direita */
  gap: 14px;
  padding: 18px 18px 14px;
  background: linear-gradient(180deg, rgba(233,221,255,0.20), rgba(253,232,242,0.10));
  border-bottom: 1px solid var(--stroke);
}

.sectionTitle {
  font-size: 24px;                  /* maior */
  font-weight: 900;
  letter-spacing: 0.3px;
  color: #1f1f2e;
  line-height: 1;
  margin: 0;
  padding-left: 2px;                /* “encaixa” melhor visualmente */
  white-space: nowrap;              /* evita quebrar linha */
}

.actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  margin-left: auto;                /* garante que fica colado à direita */
}

.input {
  padding: 10px 12px;
  border-radius: 14px;
  border: 1px solid var(--stroke);
  min-width: 280px;
  outline: none;
  background: #fff;
}

.input:focus {
  box-shadow: 0 0 0 4px rgba(142,107,255,0.12);
  border-color: rgba(142,107,255,0.35);
}

.pager { display: flex; gap: 10px; align-items: center; }

.pageInfo { color: var(--muted); font-size: 12px; }

.btn {
  padding: 9px 10px;
  border-radius: 14px;
  border: 1px solid var(--stroke);
  background: #fff;
  cursor: pointer;
  font-weight: 700;
  font-size: 12px;
}

.btn:disabled { opacity: 0.5; cursor: not-allowed; }

.btnGhost {
  padding: 8px 10px;
  border-radius: 14px;
  border: 1px solid var(--stroke);
  background: rgba(255,255,255,0.65);
  cursor: pointer;
  font-weight: 700;
  font-size: 12px;
}

.tableWrap { padding: 12px 16px 16px; }

table { width: 100%; border-collapse: collapse; }

th, td { border-top: 1px solid var(--stroke); padding: 10px; text-align: left; }

th { color: var(--muted); font-size: 12px; }

.mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-size: 12px;
}

.emptySmall { padding: 12px 0 0; color: var(--muted); font-size: 12px; }

/* Seleção da linha */
.selectedRow {
  background: rgba(205, 184, 255, 0.25); /* lilás suave */
}

</style>
