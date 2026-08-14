import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { apiFetch, clearAuth } from '../api/client'

const AuthContext = createContext(null)

function getStoredSession() {
  try {
    const raw = localStorage.getItem('boxingclub_session')
    if (!raw) return null
    return JSON.parse(raw)
  } catch {
    return null
  }
}

function storeSession(session) {
  localStorage.setItem('boxingclub_session', JSON.stringify(session))
}

function clearSession() {
  localStorage.removeItem('boxingclub_session')
}

export function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(() => getStoredSession()?.user || null)
  const [token, setToken] = useState(() => getStoredSession()?.token || null)
  const [loading, setLoading] = useState(false)

  const isAuthenticated = !!token && !!currentUser

  const login = useCallback(async (email, password) => {
    setLoading(true)
    try {
      const res = await apiFetch('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Error al iniciar sesión' }))
        throw new Error(err.detail || 'Credenciales incorrectas')
      }
      const data = await res.json()
      const session = { user: data.user, token: data.access_token }
      setCurrentUser(data.user)
      setToken(data.access_token)
      storeSession(session)
      return data.user
    } finally {
      setLoading(false)
    }
  }, [])

  const logout = useCallback(() => {
    setCurrentUser(null)
    setToken(null)
    clearSession()
  }, [])

  const refreshMe = useCallback(async () => {
    if (!token) return
    try {
      const res = await apiFetch('/auth/users/me')
      if (!res.ok) {
        logout()
        return
      }
      const user = await res.json()
      setCurrentUser(user)
      storeSession({ user, token })
    } catch {
      logout()
    }
  }, [token, logout])

  useEffect(() => {
    if (token && currentUser) {
      refreshMe()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, refreshMe])

  const value = {
    currentUser,
    token,
    isAuthenticated,
    loading,
    login,
    logout,
    refreshMe,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth debe usarse dentro de AuthProvider')
  return ctx
}
