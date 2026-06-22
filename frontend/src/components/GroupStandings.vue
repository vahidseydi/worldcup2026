<template>
  <div class="group-block">
    <h3 class="group-title">Group {{ groupName }}</h3>
    <table class="standings-table">
      <thead>
        <tr>
          <th>Team</th>
          <th>P</th>
          <th>W</th>
          <th>D</th>
          <th>L</th>
          <th>GD</th>
          <th>Pts</th>
          <th>Qualify %</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="row in standings"
          :key="row.team"
          class="standing-row"
          @click="$router.push(`/team/${row.team}`)"
        >
          <td class="team-cell">{{ row.team }}</td>
          <td>{{ row.played }}</td>
          <td>{{ row.won }}</td>
          <td>{{ row.drawn }}</td>
          <td>{{ row.lost }}</td>
          <td>{{ row.goals_for - row.goals_against }}</td>
          <td><strong>{{ row.points }}</strong></td>
          <td>
            <div class="qualify-bar-wrap">
              <div
                class="qualify-bar"
                :style="{ width: qualifyPct(row.team) }"
                :class="qualifyClass(row.team)"
              />
              <span class="qualify-label">{{ qualifyPct(row.team) }}</span>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useTournamentStore } from '@/stores/tournament'

const props = defineProps({
  groupName: { type: String, required: true },
  standings: { type: Array, required: true },
})

const store = useTournamentStore()

function getQualify(teamCode) {
  return store.teamProbs[teamCode]?.qualify_prob ?? 0
}

function qualifyPct(teamCode) {
  return `${(getQualify(teamCode) * 100).toFixed(1)}%`
}

function qualifyClass(teamCode) {
  const p = getQualify(teamCode)
  if (p >= 0.75) return 'bar-high'
  if (p >= 0.4)  return 'bar-mid'
  return 'bar-low'
}
</script>

<style scoped>
.group-block { margin-bottom: 24px; }
.group-title { font-size: 1rem; font-weight: 700; margin-bottom: 8px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }

.standings-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}
.standings-table th {
  text-align: left;
  padding: 4px 8px;
  color: var(--text-muted);
  font-weight: 600;
  border-bottom: 1px solid var(--border);
}
.standing-row {
  cursor: pointer;
  transition: background 0.1s;
}
.standing-row:hover { background: var(--surface-hover); }
.standing-row td { padding: 6px 8px; border-bottom: 1px solid var(--border-subtle); }
.team-cell { font-weight: 600; }

.qualify-bar-wrap {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 120px;
}
.qualify-bar {
  height: 8px;
  border-radius: 4px;
  transition: width 0.4s;
}
.bar-high { background: #10b981; }
.bar-mid  { background: #f59e0b; }
.bar-low  { background: #ef4444; }
.qualify-label { font-size: 0.75rem; color: var(--text-muted); white-space: nowrap; }
</style>
