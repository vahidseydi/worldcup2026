<template>
  <div class="team-view">
    <!-- Back nav -->
    <div class="back-bar">
      <button class="back-btn" @click="$router.push('/')">← All Teams</button>
    </div>

    <!-- Not found -->
    <div v-if="!probs && !store.loading" class="status-msg">
      Team <strong>{{ code }}</strong> not found or data not yet loaded.
    </div>

    <template v-else-if="probs">
      <!-- Team header -->
      <header class="team-header">
        <div class="team-identity">
          <span class="team-flag">{{ flag }}</span>
          <div>
            <h1 class="team-name">{{ fullName }}</h1>
            <div class="team-meta">
              <span class="group-badge">Group {{ groupId }}</span>
              <span class="standing-text" v-if="myStanding">
                {{ ordinal(myRank) }} · {{ myStanding.points }} pts
                · GD {{ myStanding.goals_for - myStanding.goals_against }}
              </span>
            </div>
          </div>
        </div>

        <div class="qualify-chip" :class="qualifyClass">
          {{ pct(probs.qualify_prob) }}
          <span class="chip-label">qualify</span>
        </div>
      </header>

      <!-- Section: Tournament Path -->
      <section class="card">
        <h2 class="section-title">Tournament Path</h2>
        <p class="section-desc">
          Probability of reaching each stage, based on Bayesian inference from confirmed match results.
        </p>
        <TournamentPath
          :round-probs="probs.round_probs"
          :qualify-prob="probs.qualify_prob"
        />
      </section>

      <!-- Section: Possible Opponents -->
      <section class="card">
        <h2 class="section-title">Possible Opponents</h2>
        <p class="section-desc">
          Conditional on reaching each round — who is the model most likely to send your way?
        </p>
        <OpponentList
          :opponents="probs.opponents"
          :round-probs="probs.round_probs"
          :qualify-prob="probs.qualify_prob"
        />
      </section>

      <!-- Section: Group Matches -->
      <section class="card">
        <h2 class="section-title">Group {{ groupId }} Matches</h2>

        <div class="group-columns">
          <!-- Standings -->
          <div class="standings-col">
            <table class="standings-table">
              <thead>
                <tr>
                  <th></th>
                  <th>Team</th>
                  <th>Pld</th>
                  <th>Pts</th>
                  <th>GD</th>
                  <th>GF</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(s, idx) in groupStandings"
                  :key="s.team"
                  :class="{ 'my-team': s.team === code, 'qualify-line': idx === 1 }"
                >
                  <td class="rank-cell">{{ idx + 1 }}</td>
                  <td class="team-cell">
                    <span class="small-flag">{{ teamFlag(s.team) }}</span>
                    <button class="team-link" @click="$router.push(`/team/${s.team}`)">
                      {{ teamName(s.team) }}
                    </button>
                  </td>
                  <td>{{ s.played }}</td>
                  <td class="pts">{{ s.points }}</td>
                  <td :class="gdClass(s)">{{ gdStr(s) }}</td>
                  <td>{{ s.goals_for }}</td>
                </tr>
              </tbody>
            </table>
            <p class="qual-note">↑ Top 2 qualify automatically · Best thirds also advance</p>
          </div>

          <!-- Match list -->
          <div class="matches-col">
            <div v-if="myMatches.length === 0" class="no-matches">No matches yet.</div>
            <div
              v-for="m in myMatches"
              :key="m.id"
              class="match-row"
              :class="{ confirmed: m.is_confirmed }"
            >
              <div class="match-teams">
                <span class="match-team" :class="{ 'is-me': m.home_team === code }">
                  {{ teamFlag(m.home_team) }} {{ teamName(m.home_team) }}
                </span>
                <span class="match-score" v-if="m.is_confirmed">
                  {{ m.home_score }} – {{ m.away_score }}
                </span>
                <span class="match-score future" v-else>vs</span>
                <span class="match-team away" :class="{ 'is-me': m.away_team === code }">
                  {{ teamName(m.away_team) }} {{ teamFlag(m.away_team) }}
                </span>
              </div>
              <span v-if="m.is_confirmed" class="result-badge" :class="resultClass(m)">
                {{ resultLabel(m) }}
              </span>
              <span v-else class="result-badge upcoming">Upcoming</span>
            </div>
          </div>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTournamentStore } from '@/stores/tournament'
import TournamentPath from '@/components/TournamentPath.vue'
import OpponentList from '@/components/OpponentList.vue'
import { teamFlag, teamName } from '@/data/teams'

const route  = useRoute()
const router = useRouter()
const store  = useTournamentStore()

const code = computed(() => route.params.code)
const flag = computed(() => teamFlag(code.value))
const fullName = computed(() => teamName(code.value))
const probs = computed(() => store.teamProbs[code.value] ?? null)

onMounted(() => {
  if (!store.hasData) store.refresh()
})

// Find which group this team belongs to
const groupId = computed(() => {
  for (const [gId, rows] of Object.entries(store.actualState?.group_standings ?? {})) {
    if (rows.some(r => r.team === code.value)) return gId
  }
  return null
})

const groupStandings = computed(() =>
  groupId.value ? (store.actualState?.group_standings[groupId.value] ?? []) : []
)

const myRank = computed(() =>
  groupStandings.value.findIndex(s => s.team === code.value) + 1
)

const myStanding = computed(() =>
  groupStandings.value.find(s => s.team === code.value) ?? null
)

const qualifyClass = computed(() => {
  const p = probs.value?.qualify_prob ?? 0
  if (p >= 0.70) return 'high'
  if (p >= 0.40) return 'mid'
  return 'low'
})

// Matches involving this team, group stage only
const myMatches = computed(() =>
  store.matches.filter(
    m =>
      m.stage === 'GROUP_STAGE' &&
      (m.home_team === code.value || m.away_team === code.value)
  )
)

function pct(v) {
  if (v == null) return '—'
  return `${(v * 100).toFixed(1)}%`
}

function ordinal(n) {
  const s = ['th', 'st', 'nd', 'rd']
  const v = n % 100
  return n + (s[(v - 20) % 10] || s[v] || s[0])
}

function gdStr(s) {
  const gd = s.goals_for - s.goals_against
  return gd > 0 ? `+${gd}` : `${gd}`
}

function gdClass(s) {
  const gd = s.goals_for - s.goals_against
  return gd > 0 ? 'pos' : gd < 0 ? 'neg' : ''
}

function resultClass(m) {
  if (!m.result) return ''
  const win =
    (m.result === 'home_win' && m.home_team === code.value) ||
    (m.result === 'away_win' && m.away_team === code.value)
  const lose =
    (m.result === 'home_win' && m.away_team === code.value) ||
    (m.result === 'away_win' && m.home_team === code.value)
  if (win)  return 'win'
  if (lose) return 'loss'
  return 'draw'
}

function resultLabel(m) {
  const c = resultClass(m)
  return { win: 'W', loss: 'L', draw: 'D' }[c] ?? ''
}
</script>

<style scoped>
.team-view {
  max-width: 860px;
  margin: 0 auto;
  padding: 0 20px 48px;
}

/* ── Back ── */
.back-bar { padding: 14px 0 4px; }
.back-btn {
  background: none;
  border: none;
  color: #3b82f6;
  font-size: 0.88rem;
  font-weight: 600;
  cursor: pointer;
  padding: 4px 0;
}
.back-btn:hover { text-decoration: underline; }

/* ── Status ── */
.status-msg {
  padding: 60px 0;
  text-align: center;
  color: var(--text-muted);
}

/* ── Team header ── */
.team-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  padding: 16px 0 20px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 20px;
}

.team-identity {
  display: flex;
  align-items: center;
  gap: 14px;
}

.team-flag { font-size: 3rem; line-height: 1; }
.team-name { font-size: 1.6rem; font-weight: 800; }

.team-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 4px;
  flex-wrap: wrap;
}

.group-badge {
  background: #eff6ff;
  color: #1d4ed8;
  border-radius: 20px;
  padding: 2px 10px;
  font-size: 0.78rem;
  font-weight: 700;
}

.standing-text {
  font-size: 0.82rem;
  color: var(--text-muted);
}

.qualify-chip {
  display: flex;
  flex-direction: column;
  align-items: center;
  border-radius: 12px;
  padding: 12px 20px;
  font-size: 1.8rem;
  font-weight: 800;
  line-height: 1;
}
.chip-label { font-size: 0.7rem; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase; margin-top: 4px; }
.qualify-chip.high { background: #d1fae5; color: #065f46; }
.qualify-chip.mid  { background: #fef3c7; color: #92400e; }
.qualify-chip.low  { background: #fee2e2; color: #991b1b; }

/* ── Cards ── */
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
}

.section-title {
  font-size: 1rem;
  font-weight: 700;
  margin-bottom: 4px;
}

.section-desc {
  font-size: 0.8rem;
  color: var(--text-muted);
  margin-bottom: 16px;
}

/* ── Group columns ── */
.group-columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}
@media (max-width: 600px) {
  .group-columns { grid-template-columns: 1fr; }
}

/* ── Standings table ── */
.standings-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.82rem;
}
.standings-table th {
  text-align: left;
  padding: 4px 6px;
  color: var(--text-muted);
  font-weight: 600;
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  border-bottom: 1px solid var(--border);
}
.standings-table td {
  padding: 7px 6px;
  border-bottom: 1px solid var(--border-subtle);
}

.standings-table tr.my-team td { background: #eff6ff; }
.standings-table tr.qualify-line td { border-bottom: 2px dashed #3b82f6; }

.rank-cell { color: var(--text-muted); width: 20px; }
.team-cell { display: flex; align-items: center; gap: 6px; }
.small-flag { font-size: 1rem; }
.team-link {
  background: none; border: none; cursor: pointer;
  color: var(--text); font-size: 0.82rem; font-weight: 500;
  padding: 0; text-align: left;
}
.team-link:hover { color: #3b82f6; }
.pts { font-weight: 700; }
.pos { color: #10b981; }
.neg { color: #ef4444; }

.qual-note {
  font-size: 0.72rem;
  color: var(--text-muted);
  margin-top: 8px;
  line-height: 1.4;
}

/* ── Match list ── */
.matches-col { display: flex; flex-direction: column; gap: 8px; }

.match-row {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.match-row.confirmed { border-color: #bfdbfe; background: #f0f7ff; }

.match-teams {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.82rem;
  flex-wrap: wrap;
}
.match-team { flex: 1; }
.match-team.away { text-align: right; }
.match-team.is-me { font-weight: 700; }

.match-score {
  font-weight: 800;
  font-size: 1rem;
  white-space: nowrap;
  text-align: center;
  min-width: 40px;
}
.match-score.future { color: var(--text-muted); font-weight: 500; font-size: 0.82rem; }

.result-badge {
  align-self: flex-start;
  font-size: 0.7rem;
  font-weight: 700;
  padding: 1px 8px;
  border-radius: 20px;
}
.result-badge.win     { background: #d1fae5; color: #065f46; }
.result-badge.loss    { background: #fee2e2; color: #991b1b; }
.result-badge.draw    { background: #fef3c7; color: #92400e; }
.result-badge.upcoming { background: #e5e7eb; color: #6b7280; }

.no-matches { color: var(--text-muted); font-size: 0.85rem; padding: 8px 0; }
</style>
