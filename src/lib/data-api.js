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

  // Budget default cards are intentionally not updated in Supabase because the
  // production RLS policy is INSERT/DELETE-oriented. Keep their editable budget
  // values in the user's local, user-scoped snapshot so a refresh does not reset
  // them to zero. Custom Budget accounts remain fully persisted in Supabase.
  const local = loadLocal(fallback, userId)
  const localDefaultBudgets = (local.budgetAccounts || []).filter(row => row.legacy_key)
  const localBudgetByKey = new Map(localDefaultBudgets.map(row => [`${row.month}:${row.legacy_key}`, row]))
  const serverBudget = rows.budget_account || []
  const mergedBudget = serverBudget.map(row => {
    const localRow = localBudgetByKey.get(`${row.month}:${row.legacy_key}`)
    return localRow ? { ...row, budget: Number(localRow.budget || 0), ativo: localRow.ativo !== false } : row
  })
  const serverBudgetKeys = new Set(serverBudget.filter(row => row.legacy_key).map(row => `${row.month}:${row.legacy_key}`))
  for (const row of localDefaultBudgets) {
    const key = `${row.month}:${row.legacy_key}`
    if (!serverBudgetKeys.has(key)) mergedBudget.push(row)
  }

  if (!settings) await upsertUserSettings(userId, { start_month: startMonth })
  const data = { ...fallback, startMonth, fluxo: rows.fluxo || [], entradas: rows.entrada || [], prestadores: rows.prestador || rows.empregada || [], despesas: rows.despesa || [], gastos: rows.gasto || [], transferencias: rows.transferencia || [], budgetAccounts: mergedBudget }
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

  // normalizeData generates the standard Budget cards for planning months.
  // They are UI defaults, not user-created records. Their editable values are
  // retained in the user-scoped local snapshot; custom accounts are persisted
  // normally in Supabase.
  const budgetAccountsToPersist = (data.budgetAccounts || []).filter(row => !row.legacy_key)

  await Promise.all([
    upsertUserSettings(userId, { start_month: data.startMonth || currentMonth }),
    upsertRows('fluxo', data.fluxo || [], userId),
    upsertRows('entrada', data.entradas || [], userId),
    upsertRows('prestador', data.prestadores || [], userId),
    upsertRows('despesa', data.despesas || [], userId),
    upsertRows('gasto', data.gastos || [], userId),
    upsertRows('transferencia', data.transferencias || [], userId),
    ...(budgetAccountsToPersist.length ? [upsertRows('budget_account', budgetAccountsToPersist, userId)] : [])
  ])

  const cleanupOptions = { preserveHistory: true, fromMonth: currentMonth }
  await Promise.all([
    deleteRowsNotInIds('entrada', (data.entradas || []).map(row => row.id), userId, cleanupOptions),
    deleteRowsNotInIds('prestador', (data.prestadores || []).map(row => row.id), userId, cleanupOptions),
    deleteRowsNotInIds('despesa', (data.despesas || []).map(row => row.id), userId, cleanupOptions),
    deleteRowsNotInIds('gasto', (data.gastos || []).map(row => row.id), userId, cleanupOptions),
    deleteRowsNotInIds('transferencia', (data.transferencias || []).map(row => row.id), userId, cleanupOptions),
    deleteRowsNotInIds('budget_account', budgetAccountsToPersist.map(row => row.id), userId, cleanupOptions)
  ])
  return { persisted: true, mode: 'supabase' }
}
