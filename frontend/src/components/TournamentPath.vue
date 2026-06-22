<template>
  <div class="path-wrap">
    <div v-if="hasScenario" class="scenario-banner">
      ⚡ Scenario mode — predictions applied
    </div>
    <div class="path-track">
      <div
        v-for="round in rounds"
        :key="round.id"
        class="path-node"
        :class="nodeClass(round.prob)"
      >
        <div class="node-top">
          <span class="node-label">{{ round.label }}</span>
          <span class="node-pct">{{ pct(round.scenarioProb ?? round.prob) }}</span>
          <span v-if="hasScenario && delta(round) !== 0" class="node-delta" :class="delta(round) > 0 ? 'up' : 'down'">
            {{ delta(round) > 0 ? '+' : '' }}{{ delta(round) }}%
          </span>
        </div>
        <div class="node-bar-bg">
          <!-- Actual bar -->
          <div class="node-bar-fill actual" :style="{ height: barHeight(round.prob) }"></div>
          <!-- Scenario overlay -->
          <div v-if="hasScenario" class="node-bar-fill scenario" :style="{ height: barHeight(round.scenarioProb ?? round.prob) }"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  roundProbs:         { type: Object, required: true },
  qualifyProb:        { type: Number, required: true },
  scenarioRoundProbs: { type: Object, default: null },
  scenarioQualifyProb:{ type: Number, default: null },
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

const hasScenario = computed(() => props.scenarioRoundProbs !== null)

const rounds = computed(() =>
  ROUNDS.map(r => {
    const prob = r.id === 'qualify' ? props.qualifyProb : (props.roundProbs[r.id] ?? 0)
    const scenarioProb = hasScenario.value
      ? (r.id === 'qualify' ? props.scenarioQualifyProb : (props.scenarioRoundProbs[r.id] ?? 0))
      : null
    return { ...r, prob, scenarioProb }
  })
)

function nodeClass(p) {
  if (p >= 0.7)  return 'strong'
  if (p >= 0.35) return 'mid'
  if (p >= 0.05) return 'low'
  return 'faint'
}

function barHeight(p) {
  return `${Math.max(2, (p ?? 0) * 100).toFixed(0)}%`
}

function pct(v) {
  if (v == null) return '—'
  if (v < 0.001) return '<0.1%'
  return `${(v * 100).toFixed(v < 0.01 ? 1 : 0)}%`
}

function delta(round) {
  if (!hasScenario.value || round.scenarioProb === null) return 0
  return Math.round((round.scenarioProb - round.prob) * 100)
}
</script>

<style scoped>
.path-wrap {
  width: 100%;
  overflow-x: auto;
  padding-bottom: 4px;
}

.scenario-banner {
  font-size: 0.75rem;
  font-weight: 600;
  color: #7c3aed;
  background: #f5f3ff;
  border: 1px solid #ddd6fe;
  border-radius: 6px;
  padding: 5px 10px;
  margin-bottom: 12px;
}

.path-track {
  display: flex;
  gap: 6px;
  min-width: 420px;
  align-items: flex-end;
  height: 180px;
  padding: 0 2px 0;
}

.path-node {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  height: 100%;
  justify-content: flex-end;
}

.node-top {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1px;
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

.node-delta {
  font-size: 0.68rem;
  font-weight: 700;
}
.node-delta.up   { color: #7c3aed; }
.node-delta.down { color: #ef4444; }

.node-bar-bg {
  width: 100%;
  height: 90px;
  background: var(--border-subtle);
  border-radius: 6px 6px 0 0;
  position: relative;
  overflow: hidden;
}

.node-bar-fill {
  position: absolute;
  bottom: 0;
  width: 100%;
  border-radius: 6px 6px 0 0;
  transition: height 0.5s ease;
}

.node-bar-fill.actual {
  width: 100%;
}

.node-bar-fill.scenario {
  width: 40%;
  right: 0;
  opacity: 0.85;
  background: #7c3aed !important;
}

/* Colour tiers (actual bar) */
.strong .node-bar-fill.actual { background: #10b981; }
.strong .node-pct { color: #065f46; }
.mid    .node-bar-fill.actual { background: #3b82f6; }
.low    .node-bar-fill.actual { background: #f59e0b; }
.low    .node-pct { color: #92400e; }
.faint  .node-bar-fill.actual { background: #e5e7eb; }
.faint  .node-pct { color: var(--text-muted); }
.faint  .node-label { opacity: 0.6; }
</style>
