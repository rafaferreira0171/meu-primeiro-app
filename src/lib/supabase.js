import { createClient } from '@supabase/supabase-js'

const url = import.meta.env.VITE_SUPABASE_URL
const anonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

let supabase = null

// A malformed/missing Pages secret must never prevent the React app from mounting.
// In that case the app safely falls back to its local-storage mode.
try {
  if (url && anonKey) supabase = createClient(url, anonKey)
} catch (error) {
  console.warn('LookLiP Finance: Supabase indisponível; usando modo local.', error)
  supabase = null
}

export { supabase }

export function hasSupabaseConfig() {
  return Boolean(supabase)
}
