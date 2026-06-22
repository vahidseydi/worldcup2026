import { defineStore } from 'pinia'
import { ref } from 'vue'
import { fetchPredictions, postPrediction, deletePrediction, clearPredictions } from '@/api/predictions'
import { useTournamentStore } from '@/stores/tournament'

export const usePredictionsStore = defineStore('predictions', () => {
  const predictions = ref([])
  const saving = ref(false)
  const error = ref(null)

  async function load() {
    try {
      predictions.value = await fetchPredictions()
    } catch (e) {
      error.value = e.message
    }
  }

  async function add(prediction) {
    saving.value = true
    error.value = null
    try {
      await postPrediction(prediction)
      predictions.value = await fetchPredictions()
      await useTournamentStore().loadScenarioState()
    } catch (e) {
      error.value = e.message
    } finally {
      saving.value = false
    }
  }

  async function remove(matchId) {
    saving.value = true
    error.value = null
    try {
      await deletePrediction(matchId)
      predictions.value = predictions.value.filter(p => p.id !== matchId)
      await useTournamentStore().loadScenarioState()
    } catch (e) {
      error.value = e.message
    } finally {
      saving.value = false
    }
  }

  async function clear() {
    saving.value = true
    error.value = null
    try {
      await clearPredictions()
      predictions.value = []
      await useTournamentStore().loadScenarioState()
    } catch (e) {
      error.value = e.message
    } finally {
      saving.value = false
    }
  }

  return { predictions, saving, error, load, add, remove, clear }
})
