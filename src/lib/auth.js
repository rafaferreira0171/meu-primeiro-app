import { supabase, hasSupabaseConfig } from './supabase'

export async function signIn(email, password) {
  if (!hasSupabaseConfig()) throw new Error('BACKEND_NOT_CONFIGURED')
  return supabase.auth.signInWithPassword({ email, password })
}

export async function signUp(email, password) {
  if (!hasSupabaseConfig()) throw new Error('BACKEND_NOT_CONFIGURED')
  return supabase.auth.signUp({ email, password })
}

export async function signOut() {
  if (supabase) await supabase.auth.signOut()
}

export async function getSession() {
  if (!supabase) return null
  const { data } = await supabase.auth.getSession()
  return data.session
}

export function onAuthStateChange(callback) {
  if (!supabase) return { data: { subscription: { unsubscribe() {} } } }
  return supabase.auth.onAuthStateChange((_event, session) => callback(session))
}
