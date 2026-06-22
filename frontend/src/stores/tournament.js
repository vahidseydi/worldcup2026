import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { fetchActualState, fetchScenarioState, fetchMatches } from '@/api/tournament'

export const useTournamentStore = defineStore('tournament', () => {
  const actualState = ref(null)
  const scenarioState = ref(null)
  const matches = ref([])
  const loading = ref(false)
  const error = ref(null)

  const groups = computed(() => {
    if (!actualState.value) return {}
    return actualState.value.group_standings
  })

  const teamProbs = computed(() => {
    if (!actualState.value) return {}
    return actualState.value.team_probs
  })

  const scenarioTeamProbs = computed(() => {
    if (!scenarioState.value) return {}
    return scenarioState.value.team_probs
  })

  const hasData = computed(() => actualState.value !== null)

  async function loadActualState() {
    loading.value = true
    error.value = null
    try {
      actualState.value = await fetchActualState()
    } catch (e) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function loadScenarioState() {
    try {
      scenarioState.value = await fetchScenarioState()
    } catch {
      // scenario state may not exist yet — silent fail
    }
  }

  async function loadMatches() {
    try {
      matches.value = await fetchMatches()
    } catch {
      matches.value = []
    }
  }

  async function refresh() {
    await Promise.all([loadActualState(), loadScenarioState(), loadMatches()])
  }

  return {
    actualState, scenarioState, matches,
    loading, error,
    groups, teamProbs, scenarioTeamProbs, hasData,
    loadActualState, loadScenarioState, loadMatches, refresh,
  }
})
