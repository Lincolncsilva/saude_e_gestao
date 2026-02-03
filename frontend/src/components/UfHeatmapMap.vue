<template>
  <div class="card">
    <div class="cardHeader">
      <div>
        <div class="title">Mapa de Calor — Despesas por UF</div>
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
import { MapChart } from "echarts/charts";
import {
  TooltipComponent,
  VisualMapComponent,
  TitleComponent,
} from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";

// 1) Registrar módulos do ECharts
echarts.use([
  MapChart,
  TooltipComponent,
  VisualMapComponent,
  TitleComponent,
  CanvasRenderer,
]);

// 2) Importar GeoJSON e registrar mapa
import brasilGeo from "../assets/maps/brasil-ufs.json";
echarts.registerMap("BR", brasilGeo);

const props = defineProps({
  dataByUf: { type: Object, default: () => ({}) }, // { SP: 123, RJ: 456 }
});

// -----------------------------
// Helpers
// -----------------------------
function formatMoney(v) {
  if (!v && v !== 0) return "R$ 0";

  return "R$ " + Number(v).toLocaleString("pt-BR", {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  });
}

// -----------------------------
// Converte {UF: valor} -> [{name, value}]
// -----------------------------
const seriesData = computed(() => {
  return Object.entries(props.dataByUf).map(([uf, val]) => ({
    // O geojson usa properties.sigla (SP, RJ, RN, etc)
    name: uf,
    value: Number(val || 0),
  }));
});

// -----------------------------
// Valor máximo para escala do mapa
// -----------------------------
const maxValue = computed(() => {
  const values = Object.values(props.dataByUf || {}).map((v) => Number(v || 0));
  return values.length ? Math.max(...values) : 0;
});

// -----------------------------
// Opções do ECharts
// -----------------------------
const option = computed(() => ({
  tooltip: {
    trigger: "item",
    formatter: (p) => {
      const v = Number(p.value || 0);
      return `
        <b>${p.name}</b><br/>
        ${v.toLocaleString("pt-BR", {
          style: "currency",
          currency: "BRL",
        })}
      `;
    },
  },

  visualMap: {
    min: 0,
    max: maxValue.value,
    text: ["Maior", "Menor"],
    calculable: true,
    left: 20,
    bottom: 20,

    formatter: (value) => formatMoney(value),

    inRange: {
      color: ["#fde8f2", "#8e6bff"],
    },
  },

  series: [
    {
      name: "Despesas",
      type: "map",
      map: "BR",

      // Match pelo campo properties.sigla do GeoJSON
      nameProperty: "sigla",

      // Centraliza e escala o mapa corretamente
      layoutCenter: ["50%", "50%"],
      layoutSize: "100%",

      roam: false,
      emphasis: { label: { show: false } },

      itemStyle: {
        borderColor: "rgba(142,107,255,0.25)",
        borderWidth: 1,
      },

      data: seriesData.value,
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
.title{ font-weight:900; font-size: 22px; }
.subtitle{ color:var(--muted); font-size:12px; margin-top:4px; }
.chartWrap{ padding:12px 16px 16px; }
.echart{ height: 560px; width: 100%; }
</style>
