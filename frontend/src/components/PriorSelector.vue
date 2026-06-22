<template>
  <div class="prior-selector">
    <span class="label">Prior knowledge:</span>
    <button
      v-for="src in priorStore.availableSources"
      :key="src.id"
      class="pill"
      :class="{ active: priorStore.activeSources.includes(src.id) }"
      :title="src.description"
      :disabled="priorStore.saving"
      @click="toggle(src.id)"
    >
      {{ src.id === 'flat' ? '⚽ Match results only' : src.label }}
    </button>
    <span v-if="priorStore.saving" class="saving">updating…</span>
  </div>
</template>

<script setup>
import { usePriorStore } from '@/stores/prior'

const priorStore = usePriorStore()

async function toggle(id) {
  const current = priorStore.activeSources
  const next = current.includes(id)
    ? current.filter(s => s !== id)
    : [...current, id]
  if (next.length === 0) return   // must have at least one
  await priorStore.setActiveSources(next)
}
</script>

<style scoped>
.prior-selector {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.label { font-size: 0.78rem; color: rgba(255,255,255,0.6); font-weight: 600; white-space: nowrap; }

.pill {
  padding: 5px 13px;
  border-radius: 16px;
  border: 1px solid rgba(255,255,255,0.25);
  background: rgba(255,255,255,0.08);
  font-size: 0.78rem;
  cursor: pointer;
  transition: all 0.15s;
  color: rgba(255,255,255,0.75);
}
.pill:hover:not(:disabled) {
  border-color: rgba(255,255,255,0.6);
  color: #fff;
  background: rgba(255,255,255,0.15);
}
.pill.active {
  background: #3b82f6;
  color: #fff;
  border-color: #3b82f6;
}
.pill:disabled { opacity: 0.4; cursor: not-allowed; }
.saving { font-size: 0.72rem; color: rgba(255,255,255,0.5); font-style: italic; }
</style>
