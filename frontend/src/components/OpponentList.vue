<template>
  <div class="opponents">
    <div
      v-for="round in roundsWithOpps"
      :key="round.id"
      class="opp-round"
    >
      <h4 class="round-heading">
        <span class="round-dot"></span>
        If you reach <strong>{{ round.label }}</strong>
        <span class="reach-prob">({{ pct(round.reachProb) }} chance)</span>
      </h4>

      <div class="opp-list">
        <div
          v-for="opp in round.top"
          :key="opp.code"
          class="opp-row"
          @click="$router.push(`/team/${opp.code}`)"
        >
          <span class="opp-flag">{{ opp.flag }}</span>
          <span class="opp-name">{{ opp.name }}</span>
          <div class="opp-bar-wrap">
            <div class="opp-bar-fill" :style="{ width: `${(opp.prob * 100).toFixed(0)}%` }"></div>
          </div>
          <span class="opp-pct">{{ pct(opp.prob) }}</span>
        </div>

        <div v-if="round.overflow > 0" class="opp-overflow">
          +{{ round.overflow }} more
        </div>
      </div>
    </div>

    <p v-if="roundsWithOpps.length === 0" class="no-opps">
      No opponent data yet — waiting for more matches.
    </p>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { teamFlag, teamName } from '@/data/teams'

const router = useRouter()

const props = defineProps({
  opponents: { type: Object, default: () => ({}) },   // round → { code: prob }
  roundProbs: { type: Object, default: () => ({}) },  // round → P(reach)
  qualifyProb: { type: Number, default: 0 },
})

const MAX_SHOWN = 6

const ROUND_META = [
  { id: 'r32',   label: 'Round of 32' },
  { id: 'r16',   label: 'Round of 16' },
  { id: 'qf',    label: 'Quarter Final' },
  { id: 'sf',    label: 'Semi Final' },
  { id: 'final', label: 'Final' },
]

const roundsWithOpps = computed(() =>
  ROUND_META
    .map(r => {
      const oppsRaw = props.opponents[r.id] ?? {}
      const sorted = Object.entries(oppsRaw)
        .sort(([, a], [, b]) => b - a)
      const top = sorted.slice(0, MAX_SHOWN).map(([code, prob]) => ({
        code,
        prob,
        flag: teamFlag(code),
        name: teamName(code),
      }))
      const reachProb = r.id === 'r32'
        ? props.qualifyProb
        : (props.roundProbs[r.id] ?? 0)
      return { ...r, top, overflow: sorted.length - top.length, reachProb }
    })
    .filter(r => r.top.length > 0)
)

function pct(v) {
  if (v == null || v === 0) return '—'
  if (v < 0.01) return '<1%'
  return `${(v * 100).toFixed(0)}%`
}
</script>

<style scoped>
.opponents { display: flex; flex-direction: column; gap: 20px; }

.opp-round {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 14px 16px;
}

.round-heading {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.88rem;
  font-weight: 600;
  margin-bottom: 12px;
  color: var(--text);
}

.round-dot {
  width: 8px; height: 8px;
  background: #3b82f6;
  border-radius: 50%;
  flex-shrink: 0;
}

.reach-prob {
  font-weight: 400;
  font-size: 0.78rem;
  color: var(--text-muted);
  margin-left: 2px;
}

.opp-list { display: flex; flex-direction: column; gap: 6px; }

.opp-row {
  display: grid;
  grid-template-columns: 1.8rem 1fr 120px 44px;
  align-items: center;
  gap: 8px;
  padding: 5px 4px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.12s;
}
.opp-row:hover { background: var(--surface-hover); }

.opp-flag { font-size: 1.2rem; text-align: center; }
.opp-name { font-size: 0.83rem; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.opp-bar-wrap {
  height: 6px;
  background: var(--border-subtle);
  border-radius: 3px;
  overflow: hidden;
}
.opp-bar-fill {
  height: 100%;
  background: #3b82f6;
  border-radius: 3px;
  transition: width 0.4s ease;
  max-width: 100%;
}

.opp-pct {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--text-muted);
  text-align: right;
}

.opp-overflow {
  font-size: 0.75rem;
  color: var(--text-muted);
  padding: 2px 4px;
}

.no-opps {
  color: var(--text-muted);
  font-size: 0.85rem;
  padding: 12px 0;
}
</style>
