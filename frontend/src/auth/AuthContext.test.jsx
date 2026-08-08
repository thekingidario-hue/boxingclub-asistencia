import { render, screen, waitFor, act } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { AuthProvider, useAuth } from './AuthContext'

const API = 'http://localhost:8000'

describe('AuthContext', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
    localStorage.clear()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('inicializa como no autenticado', () => {
    let ctx
    function TestComponent() {
      ctx = useAuth()
      return null
    }
    render(<AuthProvider><TestComponent /></AuthProvider>)
    expect(ctx.isAuthenticated).toBe(false)
    expect(ctx.currentUser).toBe(null)
    expect(ctx.token).toBe(null)
  })

  it('login almacena token y usuario', async () => {
    const mockUser = { id: 1, email: 'admin@test.local', nombre_completo: 'Admin', role: 'ADMIN', activo: true }
    const mockToken = 'mock-jwt-token'
    vi.spyOn(global, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => ({ access_token: mockToken, token_type: 'bearer', user: mockUser }),
    })

    let ctx
    function TestComponent() {
      ctx = useAuth()
      return null
    }
    render(<AuthProvider><TestComponent /></AuthProvider>)
    await act(async () => {
      await ctx.login('admin@test.local', 'password123')
    })
    expect(ctx.token).toBe(mockToken)
    expect(ctx.currentUser.email).toBe('admin@test.local')
    const session = JSON.parse(localStorage.getItem('boxingclub_session'))
    expect(session.user.email).toBe('admin@test.local')
    expect(session.token).toBe(mockToken)
  })

  it('logout limpia la sesion', async () => {
    const mockUser = { id: 1, email: 'admin@test.local', nombre_completo: 'Admin', role: 'ADMIN', activo: true }
    const mockToken = 'mock-jwt-token'
    localStorage.setItem('boxingclub_session', JSON.stringify({ user: mockUser, token: mockToken }))

    let ctx
    function TestComponent() {
      ctx = useAuth()
      return null
    }
    render(<AuthProvider><TestComponent /></AuthProvider>)

    await waitFor(() => expect(ctx.isAuthenticated).toBe(true))
    act(() => {
      ctx.logout()
    })
    expect(ctx.isAuthenticated).toBe(false)
    expect(localStorage.getItem('boxingclub_session')).toBeNull()
  })

  it('mantiene rol de usuario', async () => {
    const mockUser = { id: 1, email: 'coach@test.local', nombre_completo: 'Coach', role: 'COACH', activo: true }
    const mockToken = 'mock-jwt-token'
    localStorage.setItem('boxingclub_session', JSON.stringify({ user: mockUser, token: mockToken }))

    let ctx
    function TestComponent() {
      ctx = useAuth()
      return null
    }
    render(<AuthProvider><TestComponent /></AuthProvider>)
    await waitFor(() => expect(ctx.isAuthenticated).toBe(true))
    expect(ctx.currentUser.role).toBe('COACH')
  })
})
