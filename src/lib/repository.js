import { supabase, hasSupabaseConfig } from './supabase'

const tables = ['fluxo','empregada','despesa','gasto']

export async function loadFinanceData(userId) {
  if (!hasSupabaseConfig()) throw new Error('BACKEND_NOT_CONFIGURED')
  const results = await Promise.all(tables.map(async table => {
    const { data, error } = await supabase.from(table).select('*').eq('user_id', userId).order('month')
    if (error) throw error
    return [table, data || []]
  }))
  return Object.fromEntries(results)
}

export async function upsertRows(table, rows, userId) {
  if (!hasSupabaseConfig()) throw new Error('BACKEND_NOT_CONFIGURED')
  if (!rows.length) return []
  const payload = rows.map(row => ({ ...row, user_id: userId }))
  const { data, error } = await supabase.from(table).upsert(payload, { onConflict: table === 'fluxo' || table === 'empregada' ? 'user_id,month' : 'id' }).select()
  if (error) throw error
  return data || []
}

export async function updateRow(table, id, patch) {
  if (!hasSupabaseConfig()) throw new Error('BACKEND_NOT_CONFIGURED')
  const { data, error } = await supabase.from(table).update(patch).eq('id', id).select().single()
  if (error) throw error
  return data
}

export async function insertRow(table, row, userId) {
  if (!hasSupabaseConfig()) throw new Error('BACKEND_NOT_CONFIGURED')
  const { data, error } = await supabase.from(table).insert({ ...row, user_id: userId }).select().single()
  if (error) throw error
  return data
}

export async function deleteRow(table, id) {
  if (!hasSupabaseConfig()) throw new Error('BACKEND_NOT_CONFIGURED')
  const { error } = await supabase.from(table).delete().eq('id', id)
  if (error) throw error
}
