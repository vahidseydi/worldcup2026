const BASE = '/api/prior'

export async function fetchAvailableSources() {
  const res = await fetch(`${BASE}/sources`)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function fetchActiveSources() {
  const res = await fetch(`${BASE}/active`)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function putActiveSources(sources) {
  const res = await fetch(`${BASE}/active`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ sources }),
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}
