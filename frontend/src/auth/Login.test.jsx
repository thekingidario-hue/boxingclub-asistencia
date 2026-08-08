import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import Login from './Login'
import { AuthProvider, useAuth } from './AuthContext'

const API = 'http://localhost:8000'

function renderWithAuth(ui) {
  return render(<AuthProvider>{ui}</AuthProvider>)
}

describe('Login', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
    localStorage.clear()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('renderiza el formulario de login', () => {
    renderWithAuth(<Login />)
    expect(screen.getByText('Iniciar Sesión')).toBeTruthy()
    expect(screen.getByPlaceholderText('correo@boxingclub.local')).toBeTruthy()
    expect(screen.getByPlaceholderText('••••••••')).toBeTruthy()
  })

  it('envía credenciales y almacena session en localStorage', async () => {
    const mockUser = { id: 1, email: 'admin@boxingclub.local', nombre_completo: 'Admin', role: 'ADMIN', activo: true }
    const mockToken = 'mock-jwt-token'
    vi.spyOn(global, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => ({ access_token: mockToken, token_type: 'bearer', user: mockUser }),
    })

    renderWithAuth(<Login />)
    await fireEvent.change(screen.getByPlaceholderText('correo@boxingclub.local'), { target: { value: 'admin@boxingclub.local' } })
    await fireEvent.change(screen.getByPlaceholderText('••••••••'), { target: { value: 'password123' } })
    await fireEvent.click(screen.getByText('INICIAR SESIÓN'))

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(`${API}/auth/login`, expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ email: 'admin@boxingclub.local', password: 'password123' }),
      }))
    })

    const session = localStorage.getItem('boxingclub_session')
    expect(session).toBeTruthy()
    const parsed = JSON.parse(session)
    expect(parsed.user.email).toBe('admin@boxingclub.local')
    expect(parsed.token).toBe(mockToken)
  })

  it('muestra error en credenciales incorrectas', async () => {
    vi.spyOn(global, 'fetch').mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: 'Credenciales incorrectas' }),
    })

    renderWithAuth(<Login />)
    await fireEvent.change(screen.getByPlaceholderText('correo@boxingclub.local'), { target: { value: 'bad@email.com' } })
    await fireEvent.change(screen.getByPlaceholderText('••••••••'), { target: { value: 'wrongpassword' } })
    await fireEvent.click(screen.getByText('INICIAR SESIÓN'))

    await waitFor(() => {
      expect(screen.getByText('Credenciales incorrectas')).toBeTruthy()
    })
  })
})
