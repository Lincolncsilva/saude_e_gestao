<template>
  <div class="card mapCard">
    <div class="cardHeader">
      <div class="title">Mapa de Calor — Despesas por UF</div>
    </div>

    <div class="chartWrap" ref="wrapRef">
      <v-chart
        class="echart"
        :option="option"
        autoresize
        @click="handleClick"
      />
    </div>
  </div>
</template>


<script setup>
import { computed, ref } from "vue";
import VChart from "vue-echarts";
import * as echarts from "echarts/core";
import { MapChart } from "echarts/charts";
import { TooltipComponent, VisualMapComponent } from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";

echarts.use([MapChart, TooltipComponent, VisualMapComponent, CanvasRenderer]);

import brasilGeo from "../assets/maps/brasil-ufs.json";
echarts.registerMap("BR", brasilGeo);

const props = defineProps({
  dataByUf: { type: Object, default: () => ({}) },
  selectedUf: { type: String, default: "" },
});

const emit = defineEmits(["selectUf"]);

const wrapRef = ref(null);

function formatMoney(v) {
  if (v === null || v === undefined) return "R$ 0";
  return Number(v).toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  });
}

const seriesData = computed(() =>
  Object.entries(props.dataByUf).map(([uf, val]) => ({
    name: uf,
    value: Number(val || 0),
  }))
);

const maxValue = computed(() => {
  const values = Object.values(props.dataByUf || {}).map((v) => Number(v || 0));
  return values.length ? Math.max(...values) : 0;
});

function handleClick(params) {
  const uf = String(params?.name || "").toUpperCase();
  if (!uf || uf.length !== 2) return;

  // Posição do clique dentro do wrapper (em px)
  // ECharts passa o evento original em params.event.event
  const evt = params?.event?.event;
  const rect = wrapRef.value?.getBoundingClientRect?.();
  if (!evt || !rect) {
    emit("selectUf", { uf });
    return;
  }

  const x = evt.clientX - rect.left;
  const y = evt.clientY - rect.top;

  emit("selectUf", { uf, x, y });
}

const option = computed(() => ({
  tooltip: {
    trigger: "item",
    formatter: (p) => `<b>${p.name}</b><br/>${formatMoney(p.value || 0)}`,
  },
  visualMap: {
    min: 0,
    max: maxValue.value || 1,
    text: ["Maior", "Menor"],
    calculable: true,
    left: 20,
    bottom: 20,
    formatter: (v) => formatMoney(v),
    inRange: { color: ["#fde8f2", "#8e6bff"] },
  },
  series: [
    {
      name: "Despesas",
      type: "map",
      map: "BR",
      nameProperty: "sigla",
      layoutCenter: ["50%", "50%"],
      layoutSize: "100%",
      roam: false,
      emphasis: { label: { show: false } },
      itemStyle: { borderColor: "rgba(142,107,255,0.25)", borderWidth: 1 },
      data: seriesData.value.map((d) => ({
        ...d,
        selected: props.selectedUf && d.name === props.selectedUf,
      })),
      selectedMode: "single",
    },
  ],
}));
</script>



<style scoped>
.card { background:#fff; border:1px solid var(--stroke); border-radius:22px; overflow:hidden; }
.cardHeader{
  padding:14px 16px;
  background: linear-gradient(180deg, rgba(233,221,255,0.40), rgba(253,232,242,0.18));
  border-bottom:1px solid var(--stroke);
}
.titleRow{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:12px;
}
.title{ font-weight:900; font-size: 22px; }
.pill{
  border:1px solid var(--stroke);
  background:#fff;
  border-radius:999px;
  padding:6px 10px;
  font-size:12px;
  color: var(--text-main);
}
.mapCard { position: relative; }
.card { background:#fff; border:1px solid var(--stroke); border-radius:22px; overflow:hidden; }
.cardHeader{
  padding:14px 16px;
  background: linear-gradient(180deg, rgba(233,221,255,0.40), rgba(253,232,242,0.18));
  border-bottom:1px solid var(--stroke);
}

.title{ font-weight:900; font-size: 20px; }
.chartWrap{ padding:12px 16px 16px; position: relative; }
.echart{ height: 650px; width: 100%; }
</style>
