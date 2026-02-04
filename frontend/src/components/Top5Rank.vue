<template>
  <div class="card">
    <div class="cardHeader">
      <div>
        <div class="title">Rank Top 5 — Maior Despesa</div>
      </div>
    </div>

    <div class="body">
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Operadora</th>
            <th>UF</th>
            <th>Total</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(x, i) in top5" :key="x.agg_id">
            <td class="mono">{{ i + 1 }}</td>
            <td class="name">{{ x.razao_social }}</td>
            <td>{{ x.uf }}</td>
            <td class="mono">{{ money(x.total_despesas) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  stats: { type: Array, default: () => [] }, // array do /api/estatisticas
});

const top5 = computed(() => {
  return [...props.stats]
    .sort((a, b) => Number(b.total_despesas || 0) - Number(a.total_despesas || 0))
    .slice(0, 5);
});

function money(v) {
  const n = Number(v || 0);
  return n.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}
</script>

<style scoped>
.card { background:#fff; border:1px solid var(--stroke); border-radius:22px; overflow:hidden; }
.cardHeader{
  font-size: 22px;
  padding:14px 16px;
  background: linear-gradient(180deg, rgba(233,221,255,0.40), rgba(253,232,242,0.18));
  border-bottom:1px solid var(--stroke);
}
.title{ font-weight:900; }
.subtitle{ color:var(--muted); font-size:12px; margin-top:4px; }
.body{ padding:12px 16px 16px; }
table{ width:100%; border-collapse:collapse; }
th, td{ border-top:1px solid var(--stroke); padding:10px; text-align:left; vertical-align:top; }
th{ color:var(--muted); font-size:16px; }
.name{ font-weight:700; font-size:14px; }
.mono{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono"; font-size:15px; }
</style>
