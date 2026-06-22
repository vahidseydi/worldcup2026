<template>
  <div class="home">
    <!-- Header -->
    <header class="home-header">
      <div class="header-inner">
        <div class="header-title">
          <span class="trophy">🏆</span>
          <div>
            <h1>World Cup 2026</h1>
            <p class="subtitle">Select a team to explore their path to the trophy</p>
          </div>
        </div>
        <PriorSelector />
      </div>
    </header>

    <!-- Search -->
    <div class="search-bar-wrap">
      <input
        v-model="search"
        class="search-bar"
        placeholder="Search teams…"
        type="search"
        autocomplete="off"
      />
    </div>

    <!-- Loading / error -->
    <div v-if="store.loading" class="status-msg">Loading tournament data…</div>
    <div v-else-if="store.error" class="status-msg error">{{ store.error }}</div>

    <!-- Group grid -->
    <main v-else-if="store.hasData" class="groups-grid">
      <section
        v-for="[groupId, teams] in visibleGroups"
        :key="groupId"
        class="group-section"
      >
        <h2 class="group-label">Group {{ groupId }}</h2>
        <div class="team-tiles">
          <button
            v-for="standing in teams"
            :key="standing.team"
            class="team-tile"
            :class="qualifyClass(standing.team)"
            @click="$router.push(`/team/${standing.team}`)"
          >
            <span class="tile-flag">{{ flag(standing.team) }}</span>
            <span class="tile-name">{{ name(standing.team) }}</span>
            <span class="tile-prob">{{ pct(qualify(standing.team)) }}</span>
            <div class="tile-bar">
              <div class="tile-bar-fill" :style="{ width: barWidth(standing.team) }"></div>
            </div>
          </button>
        </div>
      </section>
    </main>

    <div v-else class="status-msg">Waiting for tournament data…</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useTournamentStore } from '@/stores/tournament'
import { usePriorStore } from '@/stores/prior'
import PriorSelector from '@/components/PriorSelector.vue'
import { teamFlag, teamName } from '@/data/teams'

const store = useTournamentStore()
const priorStore = usePriorStore()
const search = ref('')

onMounted(async () => {
  // Load prior sources first so the selector renders with the correct active state,
  // then load tournament data which depends on the active prior.
  await priorStore.load()
  store.refresh()
  setInterval(() => store.loadActualState(), 60_000)
})

const allGroups = computed(() => {
  if (!store.actualState) return []
  return Object.entries(store.actualState.group_standings)
    .sort(([a], [b]) => a.localeCompare(b))
})

const visibleGroups = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return allGroups.value
  return allGroups.value
    .map(([id, teams]) => [
      id,
      teams.filter(s =>
        s.team.toLowerCase().includes(q) ||
        teamName(s.team).toLowerCase().includes(q)
      ),
    ])
    .filter(([, teams]) => teams.length > 0)
})

function qualify(code) {
  return store.teamProbs[code]?.qualify_prob ?? null
}

function qualifyClass(code) {
  const p = qualify(code)
  if (p === null) return ''
  if (p >= 0.70) return 'high'
  if (p >= 0.40) return 'mid'
  return 'low'
}

function barWidth(code) {
  const p = qualify(code) ?? 0
  return `${(p * 100).toFixed(0)}%`
}

function pct(v) {
  if (v === null) return '—'
  return `${(v * 100).toFixed(0)}%`
}

const flag = teamFlag
const name = teamName
</script>

<style scoped>
.home {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* ── Header ── */
.home-header {
  background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%);
  padding: 20px 24px 18px;
  color: #fff;
}
.header-inner {
  max-width: 1280px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}
.header-title {
  display: flex;
  align-items: center;
  gap: 14px;
}
.trophy { font-size: 2rem; }
h1 { font-size: 1.5rem; font-weight: 700; color: #fff; }
.subtitle { font-size: 0.82rem; color: #93c5fd; margin-top: 2px; }

/* ── Search ── */
.search-bar-wrap {
  max-width: 1280px;
  margin: 16px auto 0;
  padding: 0 24px;
  width: 100%;
}
.search-bar {
  width: 100%;
  max-width: 420px;
  padding: 9px 14px;
  border: 1.5px solid var(--border);
  border-radius: 8px;
  background: var(--surface);
  color: var(--text);
  font-size: 0.9rem;
  outline: none;
  transition: border-color 0.15s;
}
.search-bar:focus { border-color: #3b82f6; }

/* ── Status ── */
.status-msg {
  text-align: center;
  padding: 60px 24px;
  color: var(--text-muted);
  font-size: 0.95rem;
}
.status-msg.error { color: #ef4444; }

/* ── Groups grid ── */
.groups-grid {
  max-width: 1280px;
  margin: 20px auto 40px;
  padding: 0 24px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.group-section {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
}

.group-label {
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text-muted);
  padding: 10px 14px 8px;
  border-bottom: 1px solid var(--border-subtle);
}

.team-tiles { display: flex; flex-direction: column; }

.team-tile {
  display: grid;
  grid-template-columns: 2rem 1fr auto;
  grid-template-rows: auto 4px;
  column-gap: 10px;
  align-items: center;
  padding: 10px 14px 10px;
  border: none;
  background: none;
  color: var(--text);
  cursor: pointer;
  text-align: left;
  transition: background 0.12s;
  border-top: 1px solid var(--border-subtle);
}
.team-tile:first-child { border-top: none; }
.team-tile:hover { background: var(--surface-hover); }

.tile-flag { font-size: 1.4rem; line-height: 1; }
.tile-name {
  font-size: 0.88rem;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tile-prob {
  font-size: 0.8rem;
  font-weight: 700;
  border-radius: 20px;
  padding: 2px 8px;
}
.high .tile-prob { background: #d1fae5; color: #065f46; }
.mid  .tile-prob { background: #fef3c7; color: #92400e; }
.low  .tile-prob { background: #fee2e2; color: #991b1b; }

/* Progress bar spans full row */
.tile-bar {
  grid-column: 1 / -1;
  height: 3px;
  background: var(--border-subtle);
  border-radius: 2px;
  margin-top: 6px;
  overflow: hidden;
}
.tile-bar-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.4s ease;
}
.high .tile-bar-fill { background: #10b981; }
.mid  .tile-bar-fill { background: #f59e0b; }
.low  .tile-bar-fill { background: #ef4444; }
</style>
