<template>
  <div class="card">
    <div class="cardHeader">
      <div>
        <div class="title">Distribuição de Despesas por UF</div>
        <div class="subtitle">Agregado a partir de /api/estatisticas</div>
      </div>
      <button class="btnGhost" @click="downloadPng">Exportar PNG</button>
    </div>

    <div class="canvasWrap">
      <canvas ref="el"></canvas>
    </div>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from "vue";
import Chart from "chart.js/auto";

const props = defineProps({
  dataByUf: { type: Object, default: () => ({}) }, // { SP: 123, RJ: 45 }
});

const el = ref(null);
let chart = null;

function build(obj) {
  const labels = Object.keys(obj).sort();
  const values = labels.map((k) => obj[k]);
  return { labels, values };
}

function render() {
  if (!el.value) return;

  const { labels, values } = build(props.dataByUf);

  if (chart) chart.destroy();

  chart = new Chart(el.value, {
    type: "bar",
    data: {
      labels,
      datasets: [{ label: "Total de Despesas (R$)", data: values }],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: true },
        tooltip: {
          callbacks: {
            label: (ctx) => {
              const v = Number(ctx.raw || 0);
              return ` ${v.toLocaleString("pt-BR", { style: "currency", currency: "BRL" })}`;
            },
          },
        },
      },
      scales: {
        y: {
          ticks: {
            callback: (v) => Number(v).toLocaleString("pt-BR"),
          },
        },
      },
    },
  });
}

function downloadPng() {
  if (!chart) return;
  const a = document.createElement("a");
  a.href = chart.toBase64Image();
  a.download = "despesas_por_uf.png";
  a.click();
}

onMounted(render);
watch(() => props.dataByUf, render, { deep: true });
onBeforeUnmount(() => chart?.destroy());
</script>

<style scoped>
.card { background:#fff; border:1px solid var(--stroke); border-radius:22px; overflow:hidden; }
.cardHeader {
  padding: 14px 16px;
  display:flex; align-items:flex-start; justify-content:space-between; gap:12px; flex-wrap:wrap;
  background: linear-gradient(180deg, rgba(233,221,255,0.40), rgba(253,232,242,0.18));
  border-bottom: 1px solid var(--stroke);
}
.title { font-weight:900; }
.subtitle { color: var(--muted); font-size: 12px; margin-top: 4px; }
.btnGhost {
  padding: 9px 10px;
  border-radius: 14px;
  border: 1px solid var(--stroke);
  background: rgba(255,255,255,0.65);
  cursor:pointer;
  font-weight: 700;
  font-size: 12px;
}
.canvasWrap { padding: 12px 16px 16px; }
</style>
