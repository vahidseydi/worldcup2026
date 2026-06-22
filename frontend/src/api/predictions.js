const BASE = '/api/predictions'

export async function fetchPredictions() {
  const res = await fetch(`${BASE}/`)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function postPrediction(prediction) {
  const res = await fetch(`${BASE}/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(prediction),
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function deletePrediction(matchId) {
  const res = await fetch(`${BASE}/${matchId}`, { method: 'DELETE' })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function clearPredictions() {
  const res = await fetch(`${BASE}/`, { method: 'DELETE' })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}
