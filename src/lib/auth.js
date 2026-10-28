import { supabase, hasSupabaseConfig } from './supabase'

function appRedirectUrl() {
  if (typeof window === 'undefined') return undefined
  return `${window.location.origin}${window.location.pathname}`
}

export async function signIn(email, password) {
  if (!hasSupabaseConfig()) throw new Error('BACKEND_NOT_CONFIGURED')
  return supabase.auth.signInWithPassword({ email, password })
}

export async function signUp(email, password) {
  if (!hasSupabaseConfig()) throw new Error('BACKEND_NOT_CONFIGURED')
  const emailRedirectTo = appRedirectUrl()
  return supabase.auth.signUp({
    email,
    password,
    options: emailRedirectTo ? { emailRedirectTo } : undefined,
  })
}

export async function signOut() {
  if (supabase) await supabase.auth.signOut()
}

export async function getSession() {
  if (!supabase) return null
  const { data } = await supabase.auth.getSession()
  return data.session
}

export async function ensureStartMonth(session, fallbackMonth) {
  if (!hasSupabaseConfig() || !session?.user) return fallbackMonth
  const existing = session.user.user_metadata?.looklip_start_month
  if (existing && /^\d{4}-\d{2}$/.test(existing)) return existing
  const { data, error } = await supabase.auth.updateUser({ data: { looklip_start_month: fallbackMonth } })
  if (error) throw error
  return data.user?.user_metadata?.looklip_start_month || fallbackMonth
}

export function onAuthStateChange(callback) {
  if (!supabase) return { data: { subscription: { unsubscribe() {} } } }
  return supabase.auth.onAuthStateChange((_event, session) => callback(session))
}
