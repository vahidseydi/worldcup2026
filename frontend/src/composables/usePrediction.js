import { ref } from 'vue'
import { usePredictionsStore } from '@/stores/predictions'

export function usePrediction() {
  const store = usePredictionsStore()
  const form = ref({ match_id: null, home_team: '', away_team: '', result: '', stage: 'group', group: '' })
  const formError = ref(null)

  function resetForm() {
    form.value = { match_id: null, home_team: '', away_team: '', result: '', stage: 'group', group: '' }
    formError.value = null
  }

  async function submit() {
    const { match_id, home_team, away_team, result, stage, group } = form.value
    if (!match_id || !home_team || !away_team || !result) {
      formError.value = 'Match ID, both teams, and result are required.'
      return
    }
    formError.value = null
    await store.add({ match_id: Number(match_id), home_team, away_team, result, stage, group: group || null })
    if (!store.error) resetForm()
    else formError.value = store.error
  }

  async function remove(matchId) {
    await store.remove(matchId)
  }

  async function clearAll() {
    await store.clear()
  }

  return { form, formError, submit, remove, clearAll }
}
