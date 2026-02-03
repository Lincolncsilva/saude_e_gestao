<template>
  <div class="wrap">
    <!-- ✅ slot sempre montado (não perde estado do input) -->
    <slot />

    <!-- Overlay de estados -->
    <div v-if="loading" class="overlay">
      <div class="stateBox">Carregando…</div>
    </div>

    <div v-else-if="error" class="overlay">
      <div class="stateBox err">
        <div><b>Erro:</b> {{ error.msg || "Falha na requisição." }}</div>
        <div class="muted" v-if="error.status">HTTP {{ error.status }}</div>
      </div>
    </div>

    <div v-else-if="empty" class="overlay">
      <div class="stateBox">Nenhum dado encontrado.</div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  loading: Boolean,
  error: Object,
  empty: Boolean,
});
</script>

<style scoped>
.wrap {
  position: relative;
}

/* overlay por cima do conteúdo, sem desmontar */
.overlay {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  background: rgba(255, 255, 255, 0.65);
  backdrop-filter: blur(8px);
  border-radius: 22px;
  padding: 12px;
}

/* caixa padrão */
.stateBox {
  padding: 12px 14px;
  border: 1px solid var(--stroke);
  border-radius: 16px;
  background: #fff;
  box-shadow: 0 18px 50px rgba(32, 24, 64, 0.10);
}

.err { color: #b42318; }
.muted { color: var(--muted); margin-top: 6px; font-size: 12px; }
</style>
