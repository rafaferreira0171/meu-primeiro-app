import { supabase, hasSupabaseConfig } from './supabase'

const tables = ['fluxo','empregada','prestador','entrada','despesa','gasto','transferencia','budget_account']

// Do not use select('*') here. The restored production database can retain stale
// PostgREST schema-cache metadata from older Base44-era fields (for example
// __deletedFields). Explicit columns keep the app independent from those ghosts.
const tableColumns = {
  fluxo: 'id,user_id,month,salario,va,condominio,iptu,gas,internet,luz,mercado,combustivel,seguro_carro,convenio,cartao,celular,cabelo,academia,contabilidade,pernambucanas,assin_chat,assin_apple,assin_ifood,assin_uber,outros,imposto',
  empregada: 'id,user_id,month,salario,dias_uteis,passagem_scs,passagem_sp',
  prestador: 'id,user_id,prestador_id,month,nome,salario,dias_uteis,passagem_scs,passagem_sp,fluxo_percent,ativo',
  entrada: 'id,user_id,series_id,month,nome,valor,ativo',
  despesa: 'id,user_id,series_id,month,nome,valor,ativo',
  gasto: 'id,user_id,month,conta,budget_account_id,valor,is_ajuste',
  transferencia: 'id,user_id,series_id,month,nome,items,ativo',
  budget_account: 'id,user_id,month,nome,budget,legacy_key,ativo',
}

export async function loadFinanceData(userId) {
  if (!hasSupabaseConfig()) throw new Error('BACKEND_NOT_CONFIGURED')
  const results = await Promise.all(tables.map(async table => {
    const { data, error } = await supabase.from(table).select(tableColumns[table]).eq('user_id', userId).order('month')
    if (error) throw error
    if (table === 'transferencia') {
      return [table, (data || []).map(row => ({ ...row, expenseRefs: Array.isArray(row.items) ? row.items : [] }))]
    }
    return [table, data || []]
  }))
  return Object.fromEntries(results)
}

export async function loadUserSettings(userId) {
  if (!hasSupabaseConfig()) throw new Error('BACKEND_NOT_CONFIGURED')
  const { data, error } = await supabase.from('user_settings').select('user_id,start_month,created_at,updated_at').eq('user_id', userId).maybeSingle()
  if (error) throw error
  return data || null
}

export async function upsertUserSettings(userId, settings) {
  if (!hasSupabaseConfig()) throw new Error('BACKEND_NOT_CONFIGURED')
  const payload = { user_id: userId, ...settings, updated_at: new Date().toISOString() }
  const { data, error } = await supabase.from('user_settings').upsert(payload, { onConflict: 'user_id' }).select('user_id,start_month,created_at,updated_at').single()
  if (error) throw error
  return data
}

export async function upsertRows(table, rows, userId) {
  if (!hasSupabaseConfig()) throw new Error('BACKEND_NOT_CONFIGURED')
  if (!rows.length) return []
  const payload = rows.map(row => {
    if (table === 'transferencia') {
      const { expenseRefs, ...rest } = row
      return { ...rest, items: Array.isArray(expenseRefs) ? expenseRefs : (Array.isArray(row.items) ? row.items : []), user_id: userId }
    }
    return { ...row, user_id: userId }
  })
  const conflict = table === 'fluxo' || table === 'empregada' ? 'user_id,month' : 'id'
  const { data, error } = await supabase.from(table).upsert(payload, { onConflict: conflict }).select(tableColumns[table])
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
