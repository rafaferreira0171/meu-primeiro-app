import { hasSupabaseConfig } from './supabase'
import { getSession } from './auth'
import { loadFinanceData, upsertRows, deleteRowsNotInIds } from './repository'

const KEY = 'looklip-finance-data'
export function saveLocal(data) { localStorage.setItem(KEY, JSON.stringify(data)) }
export function loadLocal(fallback) {
  try {
    const raw = localStorage.getItem(KEY)
    if (!raw) return fallback
    const parsed = JSON.parse(raw)
    return { ...fallback, ...parsed, entradas: parsed.entradas || [], prestadores: parsed.prestadores || parsed.empregada || [], transferencias: parsed.transferencias || [], despesas: parsed.despesas || [], gastos: parsed.gastos || [], budgetAccounts: parsed.budgetAccounts || [] }
  } catch { return fallback }
}
export async function loadData(fallback) {
  if (!hasSupabaseConfig()) return loadLocal(fallback)
  const session = await getSession()
  if (!session?.user) throw new Error('AUTH_REQUIRED')
  const rows = await loadFinanceData(session.user.id)
  const data = { ...fallback, fluxo: rows.fluxo || [], entradas: rows.entrada || [], prestadores: rows.prestador || rows.empregada || [], despesas: rows.despesa || [], gastos: rows.gasto || [], transferencias: rows.transferencia || [], budgetAccounts: rows.budget_account || [] }
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
    upsertRows('entrada', data.entradas || [], session.user.id),
    upsertRows('prestador', data.prestadores || [], session.user.id),
    upsertRows('despesa', data.despesas || [], session.user.id),
    upsertRows('gasto', data.gastos || [], session.user.id),
    upsertRows('transferencia', data.transferencias || [], session.user.id),
    upsertRows('budget_account', data.budgetAccounts || [], session.user.id)
  ])
  await Promise.all([
    deleteRowsNotInIds('entrada', (data.entradas || []).map(row => row.id), session.user.id),
    deleteRowsNotInIds('prestador', (data.prestadores || []).map(row => row.id), session.user.id),
    deleteRowsNotInIds('despesa', (data.despesas || []).map(row => row.id), session.user.id),
    deleteRowsNotInIds('gasto', (data.gastos || []).map(row => row.id), session.user.id),
    deleteRowsNotInIds('transferencia', (data.transferencias || []).map(row => row.id), session.user.id),
    deleteRowsNotInIds('budget_account', (data.budgetAccounts || []).map(row => row.id), session.user.id)
  ])
  return { persisted: true, mode: 'supabase' }
}
