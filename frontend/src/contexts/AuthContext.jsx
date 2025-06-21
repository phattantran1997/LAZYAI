// src/contexts/AuthContext.jsx
import { createContext, useState, useEffect } from 'react'
import * as authService from '../services/authService'

export const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // on mount, rehydrate from localStorage
  useEffect(() => {
    const { user: u } = authService.rehydrate()
    setUser(u)
    setLoading(false)
  }, [])

  const login = (username, password) => {
    setLoading(true)
    setError('')

    return authService
      .login(username, password)          // returns a Promise<user>
      .then(u => {
        setUser(u)
        return u
      })
      .catch(err => {
        setError(err.response?.data?.detail || err.message)
        return Promise.reject(err)
      })
      .finally(() => {
        setLoading(false)
      })
  }

  const signup = (username, name, email, password, role) => {
    setLoading(true)
    setError('')

    return authService
      .signup(username, name, email, password, role)  // Promise<user>
      .then(u => {
        setUser(u)
        return u
      })
      .catch(err => {
        setError(err.response?.data?.detail || err.message)
        return Promise.reject(err)
      })
      .finally(() => {
        setLoading(false)
      })
  }

  const logout = () => {
    authService.logout()
    setUser(null)
  }

  return (
    <AuthContext.Provider
      value={{ user, loading, error, setError, login, signup, logout }}
    >
      {children}
    </AuthContext.Provider>
  )
}
