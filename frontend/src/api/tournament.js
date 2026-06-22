const BASE = '/api/tournament'

export async function fetchActualState() {
  const res = await fetch(`${BASE}/state/actual`)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function fetchScenarioState() {
  const res = await fetch(`${BASE}/state/scenario`)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function fetchMatches() {
  const res = await fetch(`${BASE}/matches`)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}
