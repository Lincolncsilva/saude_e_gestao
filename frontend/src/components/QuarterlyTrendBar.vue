<template>
  <div class="card">
    <div class="cardHeader">
      <div>
        <div class="title">Despesas por Trimestre ao Longo dos Anos</div>
        <div class="subtitle" v-if="label">Operadora selecionada: {{ label }}</div>
        <div class="subtitle" v-else>Selecione uma operadora na tabela para visualizar</div>
      </div>
    </div>

    <div class="chartWrap">
      <v-chart class="echart" :option="option" autoresize />
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import VChart from "vue-echarts";
import * as echarts from "echarts/core";
import { BarChart } from "echarts/charts";
import { TooltipComponent, GridComponent, LegendComponent } from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";


echarts.use([BarChart, TooltipComponent, GridComponent, LegendComponent, CanvasRenderer]);

const props = defineProps({
  series: { type: Array, default: () => [] }, // [{ano, trimestre, valor_despesas}]
  label: { type: String, default: "" },
});


const years = computed(() => {
  const set = new Set(props.series.map((x) => x.ano));
  return Array.from(set).sort((a,b) => a-b);
});

const quarters = ["T1","T2","T3","T4"];

const datasetByYear = computed(() => {
  // retorna {2024: [t1,t2,t3,t4], 2025:[...]}
  const obj = {};
  for (const y of years.value) obj[y] = [0,0,0,0];

  for (const item of props.series) {
    const y = item.ano;
    const q = Number(item.trimestre) - 1;
    if (obj[y] && q >= 0 && q < 4) obj[y][q] = Number(item.valor_despesas || 0);
  }
  return obj;
});

const option = computed(() => ({
  tooltip: {
    trigger: "axis",
    axisPointer: { type: "shadow" },
    formatter: (params) => {
      const lines = params.map(p => {
        const v = Number(p.value || 0);
        return `${p.seriesName}: ${v.toLocaleString("pt-BR", { style:"currency", currency:"BRL" })}`;
      });
      return `${params[0]?.name}<br/>` + lines.join("<br/>");
    }
  },
  legend: { top: 8 },
  grid: { left: 60, right: 20, top: 50, bottom: 30 },
  xAxis: { type: "category", data: quarters },
  yAxis: {
    type: "value",
    axisLabel: { formatter: (v) => Number(v).toLocaleString("pt-BR") }
  },
  series: years.value.map((y) => ({
    name: String(y),
    type: "bar",
    data: datasetByYear.value[y],
    barGap: "10%",
  })),
}));
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
.subtitle{ color:var(--muted); font-size:14px; margin-top:4px; }
.chartWrap{ padding:12px 16px 16px; }
.echart{ height: 320px; width: 100%; }
</style>
