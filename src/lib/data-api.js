import { hasSupabaseConfig } from './supabase'
import { getSession } from './auth'
import { loadFinanceData, upsertRows, deleteRowsNotInIds } from './repository'

const KEY = 'looklip-finance-data'

export function saveLocal(data) { localStorage.setItem(KEY, JSON.stringify(data)) }
export function loadLocal(fallback) {
  try { const raw = localStorage.getItem(KEY); return raw ? JSON.parse(raw) : fallback } catch { return fallback }
}

export async function loadData(fallback) {
  if (!hasSupabaseConfig()) return loadLocal(fallback)
  const session = await getSession()
  if (!session?.user) throw new Error('AUTH_REQUIRED')
  const rows = await loadFinanceData(session.user.id)
  const data = { fluxo: rows.fluxo || [], empregada: rows.empregada || [], despesas: rows.despesa || [], gastos: rows.gasto || [] }
  saveLocal(data)
  return data
}

export async function persistData(data) {
  saveLocal(data)
  if (!hasSupabaseConfig()) return { persisted: false, mode: 'local' }
  const session = await getSession()
  if (!session?.user) throw new Error('AUTH_REQUIRED')
  await Promise.all([
    upsertRows('fluxo', data.fluxo || [], session.user.id),
    upsertRows('empregada', data.empregada || [], session.user.id),
    upsertRows('despesa', data.despesas || [], session.user.id),
    upsertRows('gasto', data.gastos || [], session.user.id)
  ])
  await Promise.all([
    deleteRowsNotInIds('despesa', (data.despesas || []).map(row => row.id), session.user.id),
    deleteRowsNotInIds('gasto', (data.gastos || []).map(row => row.id), session.user.id)
  ])
  return { persisted: true, mode: 'supabase' }
}
