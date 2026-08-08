import { useState } from 'react'
import { useAuth } from './AuthContext'

export default function Login() {
  const { login, loading } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      await login(email, password)
    } catch (err) {
      setError(err.message || 'Credenciales incorrectas')
    }
  }

  return (
    <div className="min-h-screen bg-boxing-dark text-white flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold tracking-tight">BoxingClub Los Andes</h1>
          <p className="text-gray-400 text-sm mt-2">Control de Asistencia</p>
        </div>
        <form onSubmit={handleSubmit} className="bg-boxing-gray border border-gray-700 rounded-xl p-6 space-y-4">
          <h2 className="text-lg font-bold text-center">Iniciar Sesión</h2>
          {error && (
            <div className="bg-red-900/50 border border-red-700 text-red-300 text-sm rounded-lg px-4 py-3">
              {error}
            </div>
          )}
          <div className="space-y-2">
            <label className="block text-sm text-gray-300 font-medium">Correo</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full bg-boxing-dark border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-boxing-red"
              placeholder="correo@boxingclub.local"
            />
          </div>
          <div className="space-y-2">
            <label className="block text-sm text-gray-300 font-medium">Contraseña</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full bg-boxing-dark border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-boxing-red"
              placeholder="••••••••"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-boxing-red py-3 rounded-lg font-bold disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Ingresando...' : 'INICIAR SESIÓN'}
          </button>
        </form>
      </div>
    </div>
  )
}
