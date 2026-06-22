import { computed } from 'vue'
import { useTournamentStore } from '@/stores/tournament'

const ROUND_ORDER = ['r32', 'r16', 'qf', 'sf', 'final', 'winner']
const ROUND_LABELS = {
  r32: 'R32', r16: 'R16', qf: 'QF', sf: 'SF', final: 'Final', winner: 'Winner',
}

export function useTeamProbs(teamCode) {
  const store = useTournamentStore()

  const actual = computed(() => store.teamProbs[teamCode.value] ?? null)
  const scenario = computed(() => store.scenarioTeamProbs[teamCode.value] ?? null)

  const roundLabels = ROUND_ORDER.map(r => ROUND_LABELS[r])

  const actualRoundData = computed(() =>
    ROUND_ORDER.map(r => actual.value?.round_probs?.[r] ?? 0)
  )

  const scenarioRoundData = computed(() =>
    ROUND_ORDER.map(r => scenario.value?.round_probs?.[r] ?? 0)
  )

  const hasScenarioDiff = computed(() => {
    if (!actual.value || !scenario.value) return false
    return ROUND_ORDER.some(
      r => Math.abs((actual.value.round_probs[r] ?? 0) - (scenario.value.round_probs[r] ?? 0)) > 0.001
    )
  })

  return { actual, scenario, roundLabels, actualRoundData, scenarioRoundData, hasScenarioDiff }
}
