const BASE = '/api/simulation'

export async function fetchSimulationSummary() {
  const res = await fetch(`${BASE}/summary`)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function fetchTeamProbabilities(teamCode) {
  const res = await fetch(`${BASE}/team/${teamCode.toUpperCase()}`)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}
