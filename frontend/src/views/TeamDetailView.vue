<template>
  <div class="team-detail">
    <button class="back-btn" @click="$router.back()">← Back</button>

    <div v-if="!actual" class="state-msg">No data for {{ code }}.</div>

    <template v-else>
      <h1 class="team-title">{{ code }}</h1>

      <div class="stats-row">
        <div class="stat">
          <span class="stat-label">Qualify</span>
          <span class="stat-value">{{ pct(actual.qualify_prob) }}</span>
          <span v-if="hasScenarioDiff" class="stat-scenario">{{ pct(scenario?.qualify_prob) }}</span>
        </div>
        <div class="stat">
          <span class="stat-label">Win tournament</span>
          <span class="stat-value">{{ pct(actual.win_prob) }}</span>
          <span v-if="hasScenarioDiff" class="stat-scenario">{{ pct(scenario?.win_prob) }}</span>
        </div>
      </div>

      <div class="chart-section">
        <h2>Round-by-round probability</h2>
        <ProbabilityBar
          :labels="roundLabels"
          :actual="actualRoundData"
          :scenario="hasScenarioDiff ? scenarioRoundData : null"
        />
        <p v-if="hasScenarioDiff" class="scenario-note">
          Yellow bars reflect your scenario predictions.
        </p>
      </div>

      <div class="rounds-table-section">
        <h2>Breakdown</h2>
        <table class="rounds-table">
          <thead>
            <tr>
              <th>Round</th>
              <th>Actual</th>
              <th v-if="hasScenarioDiff">Scenario</th>
              <th v-if="hasScenarioDiff">Δ</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(label, i) in roundLabels" :key="label">
              <td>{{ label }}</td>
              <td>{{ pct(actualRoundData[i]) }}</td>
              <td v-if="hasScenarioDiff">{{ pct(scenarioRoundData[i]) }}</td>
              <td v-if="hasScenarioDiff" :class="deltaClass(i)">
                {{ delta(i) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import ProbabilityBar from '@/components/ProbabilityBar.vue'
import { useTeamProbs } from '@/composables/useTeamProbs'

const route = useRoute()
const code = computed(() => route.params.code?.toUpperCase() ?? '')

const { actual, scenario, roundLabels, actualRoundData, scenarioRoundData, hasScenarioDiff } =
  useTeamProbs(code)

function pct(v) {
  if (v == null) return '—'
  return `${(v * 100).toFixed(1)}%`
}

function delta(i) {
  const d = (scenarioRoundData.value[i] - actualRoundData.value[i]) * 100
  return (d >= 0 ? '+' : '') + d.toFixed(1) + 'pp'
}

function deltaClass(i) {
  const d = (scenarioRoundData.value[i] - actualRoundData.value[i]) * 100
  if (d > 0.5) return 'pos'
  if (d < -0.5) return 'neg'
  return ''
}
</script>

<style scoped>
.team-detail { max-width: 800px; margin: 0 auto; padding: 20px 24px; }
.back-btn { background: none; border: none; cursor: pointer; color: #3b82f6; font-size: 0.9rem; margin-bottom: 16px; padding: 0; }
.team-title { font-size: 2rem; font-weight: 800; margin-bottom: 20px; }

.stats-row { display: flex; gap: 24px; margin-bottom: 28px; flex-wrap: wrap; }
.stat { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 14px 20px; display: flex; flex-direction: column; gap: 4px; }
.stat-label { font-size: 0.75rem; color: var(--text-muted); font-weight: 600; text-transform: uppercase; }
.stat-value { font-size: 1.6rem; font-weight: 800; }
.stat-scenario { font-size: 0.9rem; color: #ca8a04; }

.chart-section, .rounds-table-section { margin-bottom: 28px; }
.chart-section h2, .rounds-table-section h2 { font-size: 1rem; font-weight: 700; margin-bottom: 12px; }
.scenario-note { font-size: 0.75rem; color: var(--text-muted); margin-top: 6px; }

.rounds-table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
.rounds-table th { text-align: left; padding: 6px 12px; color: var(--text-muted); border-bottom: 1px solid var(--border); }
.rounds-table td { padding: 8px 12px; border-bottom: 1px solid var(--border-subtle); }
.pos { color: #10b981; font-weight: 600; }
.neg { color: #ef4444; font-weight: 600; }
.state-msg { color: var(--text-muted); padding: 40px 0; text-align: center; }
</style>
