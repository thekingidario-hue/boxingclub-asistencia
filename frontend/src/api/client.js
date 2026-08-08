const API = 'http://localhost:8000'

function getToken() {
  try {
    const raw = localStorage.getItem('boxingclub_session')
    if (!raw) return null
    const session = JSON.parse(raw)
    return session.token || null
  } catch {
    return null
  }
}

export function clearAuth() {
  localStorage.removeItem('boxingclub_session')
}

export async function apiFetch(path, options = {}) {
  const token = getToken()
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  const res = await fetch(`${API}${path}`, {
    ...options,
    headers,
  })
   return res
}

export function getRole() {
  try {
    const raw = localStorage.getItem('boxingclub_session')
    if (!raw) return null
    const session = JSON.parse(raw)
    return session.user?.role || null
  } catch {
    return null
  }
}

export function isAdmin() {
  return getRole() === 'ADMIN'
}

export function isCoach() {
  return getRole() === 'COACH'
}

export default API
