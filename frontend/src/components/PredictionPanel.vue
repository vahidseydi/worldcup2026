<template>
  <div class="prediction-panel">
    <div class="panel-header">
      <h2>Your Predictions</h2>
      <button v-if="predictionsStore.predictions.length" class="btn-clear" @click="clearAll">
        Clear all
      </button>
    </div>

    <p class="hint">
      Predict future matches to see how stage probabilities would shift.
      These never affect the actual state.
    </p>

    <!-- Add prediction form -->
    <form class="pred-form" @submit.prevent="submit">
      <select v-model="selectedMatchId" class="input match-select">
        <option value="" disabled>Pick a match…</option>
        <optgroup v-for="g in groupsWithFuture" :key="g" :label="`Group ${g}`">
          <option v-for="m in futureByGroup[g]" :key="m.id" :value="m.id">
            {{ m.home_team }} vs {{ m.away_team }} ({{ fmtDate(m.scheduled_at) }})
          </option>
        </optgroup>
      </select>
      <select v-model="form.result" class="input result-select">
        <option value="" disabled>Result</option>
        <option value="home_win">{{ selectedMatch ? selectedMatch.home_team : 'Home' }} win</option>
        <option value="draw">Draw</option>
        <option value="away_win">{{ selectedMatch ? selectedMatch.away_team : 'Away' }} win</option>
      </select>
      <button type="submit" class="btn-add" :disabled="!canSubmit || predictionsStore.saving">
        Add
      </button>
    </form>
    <p v-if="formError" class="form-error">{{ formError }}</p>

    <!-- Prediction list -->
    <ul v-if="predictionsStore.predictions.length" class="pred-list">
      <li v-for="p in predictionsStore.predictions" :key="p.id" class="pred-item">
        <span class="pred-match">
          {{ p.home_team }}
          <em :class="resultClass(p.result)">{{ resultLabel(p.result) }}</em>
          {{ p.away_team }}
          <span v-if="p.group" class="pred-group">(Grp {{ p.group }})</span>
        </span>
        <button class="btn-remove" @click="remove(p.id)">✕</button>
      </li>
    </ul>
    <p v-else class="empty">No predictions yet.</p>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { usePredictionsStore } from '@/stores/predictions'
import { useTournamentStore } from '@/stores/tournament'

const predictionsStore = usePredictionsStore()
const tournamentStore = useTournamentStore()

const selectedMatchId = ref('')
const form = ref({ result: '' })
const formError = ref(null)

// Only offer group-stage matches that haven't been confirmed yet
const futureGroupMatches = computed(() =>
  tournamentStore.matches.filter(m => m.stage === 'group' && !m.is_confirmed)
)

// Group them by group letter, sorted
const futureByGroup = computed(() => {
  const byGroup = {}
  for (const m of futureGroupMatches.value) {
    if (!byGroup[m.group]) byGroup[m.group] = []
    byGroup[m.group].push(m)
  }
  return byGroup
})

const groupsWithFuture = computed(() =>
  Object.keys(futureByGroup.value).sort()
)

const selectedMatch = computed(() =>
  tournamentStore.matches.find(m => m.id === selectedMatchId.value) ?? null
)

const canSubmit = computed(() =>
  selectedMatchId.value !== '' && form.value.result !== ''
)

watch(selectedMatchId, () => {
  form.value.result = ''
  formError.value = null
})

async function submit() {
  if (!canSubmit.value) return
  const m = selectedMatch.value
  if (!m) { formError.value = 'Match not found.'; return }
  formError.value = null
  await predictionsStore.add({
    match_id: m.id,
    home_team: m.home_team,
    away_team: m.away_team,
    result: form.value.result,
    stage: m.stage,
    group: m.group ?? null,
  })
  if (!predictionsStore.error) {
    selectedMatchId.value = ''
    form.value.result = ''
  } else {
    formError.value = predictionsStore.error
  }
}

async function remove(matchId) {
  await predictionsStore.remove(matchId)
}

async function clearAll() {
  await predictionsStore.clear()
}

function fmtDate(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  return d.toLocaleDateString('en-GB', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', timeZone: 'UTC' })
}

const RESULT_LABELS = { home_win: 'beats', draw: 'draws', away_win: 'loses to' }
const RESULT_CLASSES = { home_win: 'win', draw: 'draw', away_win: 'loss' }

function resultLabel(r) { return RESULT_LABELS[r] ?? r }
function resultClass(r) { return RESULT_CLASSES[r] ?? '' }
</script>

<style scoped>
.prediction-panel {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 16px 20px;
}
.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.panel-header h2 { font-size: 1rem; font-weight: 700; margin: 0; }
.hint { font-size: 0.8rem; color: var(--text-muted); margin-bottom: 12px; }

.pred-form {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}
.input {
  padding: 5px 8px;
  border: 1px solid var(--border);
  border-radius: 4px;
  background: var(--bg);
  color: var(--text);
  font-size: 0.85rem;
}
.match-select { flex: 1; min-width: 200px; }
.result-select { width: 130px; }

.btn-add {
  padding: 5px 14px;
  background: #3b82f6;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
}
.btn-add:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-clear { font-size: 0.75rem; color: #ef4444; background: none; border: none; cursor: pointer; }
.form-error { font-size: 0.8rem; color: #ef4444; margin-bottom: 8px; }

.pred-list { list-style: none; padding: 0; margin: 0; }
.pred-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
  border-bottom: 1px solid var(--border-subtle);
  font-size: 0.875rem;
}
.pred-match { display: flex; gap: 5px; align-items: center; }
.pred-group { font-size: 0.75rem; color: var(--text-muted); }
em { font-style: normal; font-weight: 600; }
em.win  { color: #10b981; }
em.draw { color: #f59e0b; }
em.loss { color: #ef4444; }

.btn-remove { background: none; border: none; color: var(--text-muted); cursor: pointer; font-size: 0.85rem; }
.btn-remove:hover { color: #ef4444; }
.empty { font-size: 0.85rem; color: var(--text-muted); }
</style>
