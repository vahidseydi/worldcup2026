<template>
  <div class="prediction-panel">

    <!-- Active predictions list -->
    <div v-if="predictionsStore.predictions.length" class="pred-list">
      <div v-for="p in predictionsStore.predictions" :key="p.id" class="pred-row">
        <span class="pred-teams">
          {{ teamFlag(p.home_team) }} {{ teamName(p.home_team) }}
          <strong class="pred-score">{{ p.home_score }} – {{ p.away_score }}</strong>
          {{ teamName(p.away_team) }} {{ teamFlag(p.away_team) }}
        </span>
        <span class="pred-group">Grp {{ p.group?.toUpperCase() }}</span>
        <button class="btn-remove" @click="remove(p.id)" title="Remove">✕</button>
      </div>
    </div>
    <p v-else class="empty">No predictions yet — add one below.</p>

    <!-- Add prediction form -->
    <div class="add-form">
      <div class="form-row">
        <!-- Group selector -->
        <select v-model="selectedGroup" class="sel sel-group">
          <option value="" disabled>Group…</option>
          <option v-for="g in availableGroups" :key="g" :value="g">Group {{ g }}</option>
        </select>

        <!-- Match selector -->
        <select v-model="selectedMatchId" class="sel sel-match" :disabled="!selectedGroup">
          <option value="" disabled>Match…</option>
          <option v-for="m in matchesForGroup" :key="m.id" :value="m.id">
            {{ teamName(m.home_team) }} vs {{ teamName(m.away_team) }}
          </option>
        </select>
      </div>

      <div v-if="selectedMatch" class="score-row">
        <span class="score-team">{{ teamFlag(selectedMatch.home_team) }} {{ teamName(selectedMatch.home_team) }}</span>
        <input v-model.number="homeScore" type="number" min="0" max="20" class="score-box" />
        <span class="score-dash">–</span>
        <input v-model.number="awayScore" type="number" min="0" max="20" class="score-box" />
        <span class="score-team">{{ teamName(selectedMatch.away_team) }} {{ teamFlag(selectedMatch.away_team) }}</span>
        <button class="btn-add" :disabled="predictionsStore.saving" @click="submit">
          {{ predictionsStore.saving ? '…' : '+ Add' }}
        </button>
      </div>

      <p v-if="predictionsStore.error" class="form-error">{{ predictionsStore.error }}</p>
    </div>

    <!-- Clear all -->
    <div v-if="predictionsStore.predictions.length" class="footer-row">
      <button class="btn-clear" @click="clearAll">Clear all predictions</button>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { usePredictionsStore } from '@/stores/predictions'
import { useTournamentStore } from '@/stores/tournament'
import { teamFlag, teamName } from '@/data/teams'

const predictionsStore = usePredictionsStore()
const tournamentStore  = useTournamentStore()

const selectedGroup   = ref('')
const selectedMatchId = ref('')
const homeScore       = ref(0)
const awayScore       = ref(0)

// All upcoming (unconfirmed) group matches
const upcomingMatches = computed(() =>
  tournamentStore.matches.filter(m => m.stage === 'group' && !m.is_confirmed)
)

// Groups that still have upcoming matches
const availableGroups = computed(() => {
  const groups = new Set(upcomingMatches.value.map(m => m.group?.toUpperCase()).filter(Boolean))
  return [...groups].sort()
})

// Upcoming matches for the selected group (exclude already-predicted)
const predictedIds = computed(() => new Set(predictionsStore.predictions.map(p => p.id)))
const matchesForGroup = computed(() =>
  upcomingMatches.value.filter(
    m => m.group?.toUpperCase() === selectedGroup.value && !predictedIds.value.has(m.id)
  )
)

const selectedMatch = computed(() =>
  tournamentStore.matches.find(m => m.id === selectedMatchId.value) ?? null
)

// Reset match when group changes
watch(selectedGroup, () => {
  selectedMatchId.value = ''
  homeScore.value = 0
  awayScore.value = 0
})

watch(selectedMatchId, () => {
  homeScore.value = 0
  awayScore.value = 0
})

async function submit() {
  if (!selectedMatch.value) return
  const m = selectedMatch.value
  await predictionsStore.add({
    match_id:  m.id,
    home_team: m.home_team,
    away_team: m.away_team,
    home_score: homeScore.value,
    away_score: awayScore.value,
    stage: m.stage,
    group: m.group ?? null,
  })
  if (!predictionsStore.error) {
    selectedMatchId.value = ''
    homeScore.value = 0
    awayScore.value = 0
  }
}

async function remove(matchId) {
  await predictionsStore.remove(matchId)
}

async function clearAll() {
  await predictionsStore.clear()
}
</script>

<style scoped>
.prediction-panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* ── Active predictions ── */
.pred-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.pred-row {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f5f3ff;
  border: 1px solid #ddd6fe;
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 0.83rem;
  flex-wrap: wrap;
}

.pred-teams { flex: 1; display: flex; align-items: center; gap: 5px; flex-wrap: wrap; }
.pred-score { font-size: 1rem; color: #7c3aed; margin: 0 4px; }
.pred-group { font-size: 0.72rem; color: #7c3aed; background: #ede9fe; padding: 2px 7px; border-radius: 20px; white-space: nowrap; }
.btn-remove { background: none; border: none; color: #a78bfa; cursor: pointer; font-size: 0.85rem; margin-left: auto; }
.btn-remove:hover { color: #ef4444; }

/* ── Add form ── */
.add-form {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.form-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.sel {
  padding: 6px 8px;
  border: 1.5px solid var(--border);
  border-radius: 6px;
  background: var(--bg);
  color: var(--text);
  font-size: 0.83rem;
  cursor: pointer;
}
.sel:focus { outline: none; border-color: #7c3aed; }
.sel-group { width: 110px; }
.sel-match { flex: 1; min-width: 160px; }

.score-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.score-team { font-size: 0.82rem; font-weight: 600; flex: 1; white-space: nowrap; }
.score-team:last-of-type { text-align: right; }

.score-box {
  width: 40px;
  text-align: center;
  padding: 4px;
  border: 1.5px solid var(--border);
  border-radius: 6px;
  background: var(--bg);
  color: var(--text);
  font-size: 1rem;
  font-weight: 700;
  -moz-appearance: textfield;
}
.score-box::-webkit-inner-spin-button,
.score-box::-webkit-outer-spin-button { -webkit-appearance: none; }
.score-box:focus { outline: none; border-color: #7c3aed; }

.score-dash { font-weight: 700; color: var(--text-muted); font-size: 1.1rem; }

.btn-add {
  padding: 6px 16px;
  background: #7c3aed;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
}
.btn-add:hover:not(:disabled) { background: #6d28d9; }
.btn-add:disabled { opacity: 0.5; cursor: not-allowed; }

.form-error { font-size: 0.8rem; color: #ef4444; }
.empty { font-size: 0.83rem; color: var(--text-muted); }

/* ── Footer ── */
.footer-row { display: flex; justify-content: flex-end; }
.btn-clear { font-size: 0.75rem; color: #ef4444; background: none; border: none; cursor: pointer; padding: 2px 0; }
.btn-clear:hover { text-decoration: underline; }
</style>
