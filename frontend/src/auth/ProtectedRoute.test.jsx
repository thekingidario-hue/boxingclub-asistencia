import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import ProtectedRoute from './ProtectedRoute'
import { AuthProvider, useAuth } from './AuthContext'
import Login from './Login'

describe('ProtectedRoute', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
    localStorage.clear()
  })

  it('muestra Login cuando no esta autenticado', () => {
    render(
      <AuthProvider>
        <ProtectedRoute>
          <div data-testid="protected-content">Contenido protegido</div>
        </ProtectedRoute>
      </AuthProvider>
    )
    expect(screen.getByText('Iniciar Sesión')).toBeTruthy()
    expect(screen.queryByTestId('protected-content')).toBeNull()
  })

  it('muestra children cuando esta autenticado', () => {
    const mockUser = { id: 1, email: 'admin@test.local', nombre_completo: 'Admin', role: 'ADMIN', activo: true }
    const mockToken = 'mock-jwt-token'
    localStorage.setItem('boxingclub_session', JSON.stringify({ user: mockUser, token: mockToken }))

    render(
      <AuthProvider>
        <ProtectedRoute>
          <div data-testid="protected-content">Contenido protegido</div>
        </ProtectedRoute>
      </AuthProvider>
    )

    expect(screen.queryByTestId('protected-content')).toBeTruthy()
    expect(screen.queryByText('Iniciar Sesión')).toBeNull()
  })
})
