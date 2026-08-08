import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'

describe('apiFetch', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
    localStorage.clear()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('adjunta Bearer token en headers', async () => {
    localStorage.setItem('boxingclub_session', JSON.stringify({ user: { role: 'ADMIN' }, token: 'test-token' }))
    vi.spyOn(global, 'fetch').mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({}) })

    const { apiFetch } = await import('./client')
    await apiFetch('/alumnos')

    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/alumnos',
      expect.objectContaining({
        headers: expect.objectContaining({ Authorization: 'Bearer test-token' }),
      })
    )
  })

  it('cierra sesion en 401', async () => {
    localStorage.setItem('boxingclub_session', JSON.stringify({ user: { role: 'ADMIN' }, token: 'test-token' }))
    vi.spyOn(global, 'fetch').mockResolvedValueOnce({ ok: false, status: 401, json: async () => ({}) })

    const { apiFetch } = await import('./client')
    const res = await apiFetch('/alumnos')

    expect(res.status).toBe(401)
  })

  it('NO cierra sesion en 403', async () => {
    localStorage.setItem('boxingclub_session', JSON.stringify({ user: { role: 'ADMIN' }, token: 'test-token' }))
    vi.spyOn(global, 'fetch').mockResolvedValueOnce({ ok: false, status: 403, json: async () => ({}) })

    const { apiFetch } = await import('./client')
    const res = await apiFetch('/alumnos')

    expect(res.status).toBe(403)
    expect(localStorage.getItem('boxingclub_session')).toBeTruthy()
  })
})
