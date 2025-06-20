import { createContext, useContext, useState, useEffect } from 'react'
import { loginUser, registerUser } from '@/api/api'

const AuthContext = createContext(null)

export const useAuth = () => useContext(AuthContext)

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    const storedUser = localStorage.getItem('user')
    const storedToken = localStorage.getItem('token')
    if (storedUser && storedToken) {
      setUser(JSON.parse(storedUser))
      setToken(storedToken)
    }
  }, [])

  const register = async (username, name, email, password, role) => {
    setLoading(true)
    setError('')
    try {
      const data = await registerUser(username, name, email, password, role)
      setUser(data.user)
      setToken(data.access_token)
      localStorage.setItem('user', JSON.stringify(data.user))
      localStorage.setItem('token', data.access_token)
      return { user: data.user, token: data.access_token }
    } catch (err) {
      setError(err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }

  const login = async (username, password) => {
    setLoading(true)
    setError('')
    try {
      const data = await loginUser(username, password)
      setUser(data.user)
      setToken(data.access_token)
      localStorage.setItem('user', JSON.stringify(data.user))
      localStorage.setItem('token', data.access_token)
      return { user: data.user, token: data.access_token }
    } catch (err) {
      setError(err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }

  const logout = () => {
    setUser(null)
    setToken(null)
    localStorage.removeItem('user')
    localStorage.removeItem('token')
  }

  const value = {
    user,
    token,
    register,
    login,
    logout,
    loading,
    error,
    setError,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
} 