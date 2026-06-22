<template>
  <div class="dashboard">
    <header class="dash-header">
      <div class="title-block">
        <h1>World Cup 2026</h1>
        <span v-if="store.actualState" class="updated">
          Updated {{ updatedAgo }}
        </span>
      </div>
      <PriorSelector />
    </header>

    <div v-if="store.loading" class="state-msg">Loading tournament data…</div>
    <div v-else-if="store.error" class="state-msg error">
      {{ store.error }}
      <button @click="store.refresh()">Retry</button>
    </div>
    <div v-else-if="!store.hasData" class="state-msg muted">
      Waiting for live data… The API poller updates every 60 s.
    </div>

    <template v-else>
      <!-- Win-probability leaderboard — always visible, no predictions needed -->
      <section class="win-board">
        <h2 class="section-title">Win Probability</h2>
        <div class="win-grid">
          <div
            v-for="(item, i) in winLeaderboard"
            :key="item.code"
            class="win-row"
            @click="$router.push(`/team/${item.code}`)"
          >
            <span class="rank">{{ i + 1 }}</span>
            <span class="team-code">{{ item.code }}</span>
            <div class="bar-track">
              <div
                class="bar-fill"
                :style="{ width: `${item.actualPct / maxWinPct * 100}%` }"
              />
              <div
                v-if="item.scenarioPct !== null && Math.abs(item.scenarioPct - item.actualPct) > 0.1"
                class="bar-scenario"
                :style="{ width: `${item.scenarioPct / maxWinPct * 100}%` }"
              />
            </div>
            <span class="win-pct">{{ item.actualPct.toFixed(1) }}%</span>
            <span
              v-if="item.scenarioPct !== null && Math.abs(item.scenarioPct - item.actualPct) > 0.1"
              class="win-scenario-pct"
              :class="item.scenarioPct > item.actualPct ? 'up' : 'down'"
            >
              → {{ item.scenarioPct.toFixed(1) }}%
            </span>
          </div>
        </div>
      </section>

      <div class="layout">
        <!-- Left: group standings -->
        <section class="groups-col">
          <h2 class="section-title">Group Standings</h2>
          <GroupStandings
            v-for="(rows, groupName) in store.groups"
            :key="groupName"
            :group-name="groupName"
            :standings="rows"
          />
        </section>

        <!-- Right: predictions + team detail cards -->
        <aside class="side-col">
          <PredictionPanel />

          <h2 class="section-title" style="margin-top: 20px;">Team Probabilities</h2>
          <section class="team-grid">
            <TeamCard
              v-for="code in teamCodes"
              :key="code"
              :code="code"
            />
          </section>
        </aside>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import { useTournamentStore } from '@/stores/tournament'
import { usePredictionsStore } from '@/stores/predictions'
import { usePriorStore } from '@/stores/prior'
import GroupStandings from '@/components/GroupStandings.vue'
import TeamCard from '@/components/TeamCard.vue'
import PredictionPanel from '@/components/PredictionPanel.vue'
import PriorSelector from '@/components/PriorSelector.vue'

const store = useTournamentStore()
const predictionsStore = usePredictionsStore()
const priorStore = usePriorStore()

const ROUND_ORDER = ['r32', 'r16', 'qf', 'sf', 'final', 'winner']

const teamCodes = computed(() =>
  Object.keys(store.teamProbs).sort(
    (a, b) => (store.teamProbs[b]?.win_prob ?? 0) - (store.teamProbs[a]?.win_prob ?? 0)
  )
)

// Win-probability leaderboard — shows actual vs scenario side-by-side
const winLeaderboard = computed(() => {
  return teamCodes.value
    .filter(code => (store.teamProbs[code]?.win_prob ?? 0) > 0)
    .map(code => {
      const actualPct = (store.teamProbs[code]?.win_prob ?? 0) * 100
      const scenarioProb = store.scenarioTeamProbs[code]?.win_prob ?? null
      const scenarioPct = scenarioProb !== null ? scenarioProb * 100 : null
      return { code, actualPct, scenarioPct }
    })
})

const maxWinPct = computed(() =>
  Math.max(...winLeaderboard.value.map(r => r.actualPct), 1)
)

const updatedAgo = computed(() => {
  if (!store.actualState?.last_updated) return ''
  const diff = Math.round((Date.now() - new Date(store.actualState.last_updated)) / 1000)
  if (diff < 60) return `${diff}s ago`
  return `${Math.round(diff / 60)}m ago`
})

onMounted(async () => {
  await Promise.all([store.refresh(), predictionsStore.load(), priorStore.load()])
  pollTimer = setInterval(() => store.refresh(), 60_000)
})

let pollTimer = null
onUnmounted(() => clearInterval(pollTimer))
</script>

<style scoped>
.dashboard { max-width: 1400px; margin: 0 auto; padding: 20px 24px; }

.dash-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 12px;
}
.title-block { display: flex; align-items: baseline; gap: 12px; }
.title-block h1 { font-size: 1.5rem; font-weight: 800; margin: 0; }
.updated { font-size: 0.75rem; color: var(--text-muted); }

.section-title {
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-muted);
  margin-bottom: 12px;
}

.state-msg {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-muted);
  font-size: 0.9rem;
}
.state-msg.error { color: #ef4444; }
.state-msg button { margin-left: 12px; padding: 4px 10px; cursor: pointer; }

/* ── Win leaderboard ── */
.win-board {
  margin-bottom: 28px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 16px 20px;
}

.win-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 6px 20px;
}

.win-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 3px 0;
  cursor: pointer;
  border-radius: 4px;
}
.win-row:hover .team-code { color: #3b82f6; }

.rank { font-size: 0.7rem; color: var(--text-muted); width: 18px; text-align: right; flex-shrink: 0; }
.win-row .team-code { font-size: 0.85rem; font-weight: 700; width: 32px; flex-shrink: 0; }

.bar-track {
  flex: 1;
  height: 8px;
  background: var(--border);
  border-radius: 4px;
  position: relative;
  overflow: hidden;
}
.bar-fill {
  position: absolute;
  left: 0; top: 0; bottom: 0;
  background: rgba(59, 130, 246, 0.8);
  border-radius: 4px;
  transition: width 0.5s ease;
}
.bar-scenario {
  position: absolute;
  left: 0; top: 0; bottom: 0;
  background: rgba(234, 179, 8, 0.7);
  border-radius: 4px;
  transition: width 0.5s ease;
}

.win-pct { font-size: 0.8rem; font-weight: 600; width: 40px; text-align: right; flex-shrink: 0; }
.win-scenario-pct { font-size: 0.75rem; width: 52px; flex-shrink: 0; }
.win-scenario-pct.up { color: #10b981; }
.win-scenario-pct.down { color: #ef4444; }

/* ── Main layout ── */
.layout {
  display: grid;
  grid-template-columns: 340px 1fr;
  gap: 24px;
  align-items: start;
}
@media (max-width: 900px) {
  .layout { grid-template-columns: 1fr; }
  .win-grid { grid-template-columns: 1fr; }
}

.groups-col { display: flex; flex-direction: column; gap: 8px; }
.side-col { display: flex; flex-direction: column; gap: 0; }

.team-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 14px;
}
</style>
