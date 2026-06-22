import { defineStore } from 'pinia'
import { ref } from 'vue'
import { fetchAvailableSources, fetchActiveSources, putActiveSources } from '@/api/prior'
import { useTournamentStore } from '@/stores/tournament'

export const usePriorStore = defineStore('prior', () => {
  const availableSources = ref([])
  const activeSources = ref([])
  const saving = ref(false)
  const error = ref(null)

  async function load() {
    try {
      const [available, active] = await Promise.all([
        fetchAvailableSources(),
        fetchActiveSources(),
      ])
      availableSources.value = available
      activeSources.value = active.sources
    } catch (e) {
      error.value = e.message
    }
  }

  async function setActiveSources(sources) {
    saving.value = true
    error.value = null
    try {
      await putActiveSources(sources)
      activeSources.value = sources
      await useTournamentStore().refresh()
    } catch (e) {
      error.value = e.message
    } finally {
      saving.value = false
    }
  }

  return { availableSources, activeSources, saving, error, load, setActiveSources }
})
