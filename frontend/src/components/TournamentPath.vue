<template>
  <div class="path-wrap">
    <div class="path-track">
      <div
        v-for="round in rounds"
        :key="round.id"
        class="path-node"
        :class="nodeClass(round)"
      >
        <div class="node-top">
          <span class="node-label">{{ round.label }}</span>
          <span class="node-pct">{{ pct(round.prob) }}</span>
        </div>
        <div class="node-bar-bg">
          <div
            class="node-bar-fill"
            :style="{ height: barHeight(round.prob) }"
          ></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  roundProbs: { type: Object, required: true }, // { r32, r16, qf, sf, final, winner }
  qualifyProb: { type: Number, required: true },
})

const ROUNDS = [
  { id: 'qualify', label: 'Qualify' },
  { id: 'r32',     label: 'R32' },
  { id: 'r16',     label: 'R16' },
  { id: 'qf',      label: 'QF' },
  { id: 'sf',      label: 'SF' },
  { id: 'final',   label: 'Final' },
  { id: 'winner',  label: 'Winner' },
]

const rounds = computed(() =>
  ROUNDS.map(r => ({
    ...r,
    prob: r.id === 'qualify' ? props.qualifyProb : (props.roundProbs[r.id] ?? 0),
  }))
)

function nodeClass(round) {
  const p = round.prob
  if (p >= 0.7)  return 'strong'
  if (p >= 0.35) return 'mid'
  if (p >= 0.05) return 'low'
  return 'faint'
}

function barHeight(p) {
  return `${Math.max(2, (p * 100)).toFixed(0)}%`
}

function pct(v) {
  if (v == null) return '—'
  if (v < 0.001) return '<0.1%'
  return `${(v * 100).toFixed(v < 0.01 ? 1 : 0)}%`
}
</script>

<style scoped>
.path-wrap {
  width: 100%;
  overflow-x: auto;
  padding-bottom: 4px;
}

.path-track {
  display: flex;
  gap: 6px;
  min-width: 420px;
  align-items: flex-end;
  height: 160px;
  padding: 0 2px 0;
}

.path-node {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  height: 100%;
  justify-content: flex-end;
}

.node-top {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.node-label {
  font-size: 0.68rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--text-muted);
}

.node-pct {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--text);
}

.node-bar-bg {
  width: 100%;
  height: 90px;
  background: var(--border-subtle);
  border-radius: 6px 6px 0 0;
  display: flex;
  align-items: flex-end;
  overflow: hidden;
}

.node-bar-fill {
  width: 100%;
  border-radius: 6px 6px 0 0;
  transition: height 0.5s ease;
}

/* Colour tiers */
.strong .node-bar-fill  { background: #10b981; }
.strong .node-pct       { color: #065f46; }

.mid .node-bar-fill     { background: #3b82f6; }

.low .node-bar-fill     { background: #f59e0b; }
.low .node-pct          { color: #92400e; }

.faint .node-bar-fill   { background: #e5e7eb; }
.faint .node-pct        { color: var(--text-muted); }
.faint .node-label      { opacity: 0.6; }
</style>
