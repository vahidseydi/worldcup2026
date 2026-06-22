<template>
  <div class="team-card" @click="$router.push(`/team/${code}`)">
    <div class="team-header">
      <span class="team-code">{{ code }}</span>
      <span class="qualify-prob" :class="qualifyClass">
        {{ pct(actual?.qualify_prob) }} qualify
      </span>
    </div>
    <ProbabilityBar
      :labels="roundLabels"
      :actual="actualRoundData"
      :scenario="hasScenarioDiff ? scenarioRoundData : null"
    />
    <div class="win-prob">
      Win: <strong>{{ pct(actual?.win_prob) }}</strong>
      <span v-if="hasScenarioDiff" class="scenario-win">
        → {{ pct(scenario?.win_prob) }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed, toRef } from 'vue'
import ProbabilityBar from '@/components/ProbabilityBar.vue'
import { useTeamProbs } from '@/composables/useTeamProbs'

const props = defineProps({
  code: { type: String, required: true },
})

const codeRef = toRef(props, 'code')
const { actual, scenario, roundLabels, actualRoundData, scenarioRoundData, hasScenarioDiff } =
  useTeamProbs(codeRef)

const qualifyClass = computed(() => {
  const p = actual.value?.qualify_prob ?? 0
  if (p >= 0.75) return 'high'
  if (p >= 0.4) return 'mid'
  return 'low'
})

function pct(v) {
  if (v == null) return '—'
  return `${(v * 100).toFixed(1)}%`
}
</script>

<style scoped>
.team-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px 16px;
  cursor: pointer;
  transition: box-shadow 0.15s;
}
.team-card:hover { box-shadow: 0 2px 12px rgba(0,0,0,0.12); }

.team-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.team-code { font-size: 1.1rem; font-weight: 700; }

.qualify-prob { font-size: 0.8rem; padding: 2px 8px; border-radius: 12px; }
.qualify-prob.high { background: #d1fae5; color: #065f46; }
.qualify-prob.mid  { background: #fef3c7; color: #92400e; }
.qualify-prob.low  { background: #fee2e2; color: #991b1b; }

.win-prob { margin-top: 6px; font-size: 0.85rem; color: var(--text-muted); }
.scenario-win { color: #ca8a04; margin-left: 4px; }
</style>
