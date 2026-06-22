const BASE = '/api/admin'

export async function seedTournament(fixtures) {
  const res = await fetch(`${BASE}/seed`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ fixtures }),
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}
