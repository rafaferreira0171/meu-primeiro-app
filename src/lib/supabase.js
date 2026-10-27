import { createClient } from '@supabase/supabase-js'

const url = import.meta.env.VITE_SUPABASE_URL
const anonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

// Some WebKit environments can expose crypto.getRandomValues without randomUUID.
// The app uses randomUUID for local recurring records, so install a safe fallback
// before the React entrypoint is evaluated. This also avoids depending on the
// inline HTML compatibility script when a cached document is involved.
try {
  const cryptoApi = globalThis.crypto
  if (cryptoApi && typeof cryptoApi.randomUUID !== 'function' && typeof cryptoApi.getRandomValues === 'function') {
    Object.defineProperty(cryptoApi, 'randomUUID', {
      configurable: true,
      value: () => {
        const bytes = new Uint8Array(16)
        cryptoApi.getRandomValues(bytes)
        bytes[6] = (bytes[6] & 15) | 64
        bytes[8] = (bytes[8] & 63) | 128
        const hex = Array.from(bytes, byte => byte.toString(16).padStart(2, '0')).join('')
        return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`
      },
    })
  }
} catch {
  // If WebKit refuses the property definition, the normal browser API is used.
}

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
