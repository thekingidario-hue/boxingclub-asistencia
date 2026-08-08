import { useAuth } from './AuthContext'
import Login from './Login'

export default function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth()

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen text-white text-xl">
        Cargando...
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Login />
  }

  return children
}
