import { hasSupabaseConfig } from './supabase'
import { getSession, ensureStartMonth } from './auth'
import { loadFinanceData, loadUserSettings, upsertUserSettings, upsertRows, deleteRowsNotInIds } from './repository'

const KEY = 'looklip-finance-data'
const DEMO_KEY = `${KEY}:demo`
const userKey = userId => `${KEY}:${userId}`

export function saveLocal(data, userId = null) {
  const key = userId ? userKey(userId) : DEMO_KEY
  localStorage.setItem(key, JSON.stringify(data))
}

export function loadLocal(fallback, userId = null) {
  try {
    const key = userId ? userKey(userId) : DEMO_KEY
    const raw = localStorage.getItem(key)
    if (!raw) return fallback
    const parsed = JSON.parse(raw)
    return { ...fallback, ...parsed, entradas: parsed.entradas || [], prestadores: parsed.prestadores || parsed.empregada || [], transferencias: parsed.transferencias || [], despesas: parsed.despesas || [], gastos: parsed.gastos || [], budgetAccounts: parsed.budgetAccounts || [] }
  } catch { return fallback }
}

export async function loadData(fallback) {
  if (!hasSupabaseConfig()) return loadLocal(fallback)
  const session = await getSession()
  if (!session?.user) throw new Error('AUTH_REQUIRED')
  const userId = session.user.id
  const [rows, settings] = await Promise.all([loadFinanceData(userId), loadUserSettings(userId)])
  const fallbackMonth = new Date().toISOString().slice(0, 7)
  const startMonth = settings?.start_month || await ensureStartMonth(session, fallbackMonth)
  if (!settings) await upsertUserSettings(userId, { start_month: startMonth })
  const data = { ...fallback, startMonth, fluxo: rows.fluxo || [], entradas: rows.entrada || [], prestadores: rows.prestador || rows.empregada || [], despesas: rows.despesa || [], gastos: rows.gasto || [], transferencias: rows.transferencia || [], budgetAccounts: rows.budget_account || [] }
  saveLocal(data, userId)
  return data
}

export async function persistData(data) {
  if (!hasSupabaseConfig()) {
    saveLocal(data)
    return { persisted: false, mode: 'local' }
  }
  const session = await getSession()
  if (!session?.user) throw new Error('AUTH_REQUIRED')
  const userId = session.user.id
  const currentMonth = new Date().toISOString().slice(0, 7)
  saveLocal(data, userId)
  await Promise.all([
    upsertUserSettings(userId, { start_month: data.startMonth || currentMonth }),
    upsertRows('fluxo', data.fluxo || [], userId),
    upsertRows('entrada', data.entradas || [], userId),
    upsertRows('prestador', data.prestadores || [], userId),
    upsertRows('despesa', data.despesas || [], userId),
    upsertRows('gasto', data.gastos || [], userId),
    upsertRows('transferencia', data.transferencias || [], userId),
    upsertRows('budget_account', data.budgetAccounts || [], userId)
  ])
  const cleanupOptions = { preserveHistory: true, fromMonth: currentMonth }
  await Promise.all([
    deleteRowsNotInIds('entrada', (data.entradas || []).map(row => row.id), userId, cleanupOptions),
    deleteRowsNotInIds('prestador', (data.prestadores || []).map(row => row.id), userId, cleanupOptions),
    deleteRowsNotInIds('despesa', (data.despesas || []).map(row => row.id), userId, cleanupOptions),
    deleteRowsNotInIds('gasto', (data.gastos || []).map(row => row.id), userId, cleanupOptions),
    deleteRowsNotInIds('transferencia', (data.transferencias || []).map(row => row.id), userId, cleanupOptions),
    deleteRowsNotInIds('budget_account', (data.budgetAccounts || []).map(row => row.id), userId, cleanupOptions)
  ])
  return { persisted: true, mode: 'supabase' }
}
