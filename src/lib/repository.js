import { supabase, hasSupabaseConfig } from './supabase'

const tables = ['fluxo','empregada','prestador','entrada','despesa','gasto','transferencia','budget_account']

export async function loadFinanceData(userId) {
  if (!hasSupabaseConfig()) throw new Error('BACKEND_NOT_CONFIGURED')
  const results = await Promise.all(tables.map(async table => {
    const { data, error } = await supabase.from(table).select('*').eq('user_id', userId).order('month')
    if (error) throw error
    return [table, data || []]
  }))
  return Object.fromEntries(results)
}

export async function loadUserSettings(userId) {
  if (!hasSupabaseConfig()) throw new Error('BACKEND_NOT_CONFIGURED')
  const { data, error } = await supabase.from('user_settings').select('*').eq('user_id', userId).maybeSingle()
  if (error) throw error
  return data || null
}

export async function upsertUserSettings(userId, settings) {
  if (!hasSupabaseConfig()) throw new Error('BACKEND_NOT_CONFIGURED')
  const payload = { user_id: userId, ...settings, updated_at: new Date().toISOString() }
  const { data, error } = await supabase.from('user_settings').upsert(payload, { onConflict: 'user_id' }).select().single()
  if (error) throw error
  return data
}

export async function upsertRows(table, rows, userId) {
  if (!hasSupabaseConfig()) throw new Error('BACKEND_NOT_CONFIGURED')
  if (!rows.length) return []
  const payload = rows.map(row => ({ ...row, user_id: userId }))
  const conflict = table === 'fluxo' || table === 'empregada' ? 'user_id,month' : 'id'
  const { data, error } = await supabase.from(table).upsert(payload, { onConflict: conflict }).select()
  if (error) throw error
  return data || []
}

export async function deleteRowsNotInIds(table, ids, userId, options = {}) {
  if (!hasSupabaseConfig()) throw new Error('BACKEND_NOT_CONFIGURED')
  if (table === 'fluxo' || table === 'empregada') return
  const { preserveHistory = false, fromMonth = null } = options
  let query = supabase.from(table).select('id,month').eq('user_id', userId)
  if (preserveHistory && fromMonth) query = query.gte('month', fromMonth)
  const { data: existing, error: readError } = await query
  if (readError) throw readError
  const keep = new Set(ids.filter(Boolean))
  const stale = (existing || []).map(row => row.id).filter(id => !keep.has(id))
  if (!stale.length) return
  const { error } = await supabase.from(table).delete().eq('user_id', userId).in('id', stale)
  if (error) throw error
}
