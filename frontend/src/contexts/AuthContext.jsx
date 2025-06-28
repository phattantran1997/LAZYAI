import { createContext, useState, useEffect } from 'react'
import { setTokens, clearTokens } from '../services/tokenStorage'
import * as authService from '../services/authService'

export const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  // Information about the current user
  const [user, setUser] = useState({ "username": "", "email": "", "role": "" })

  // User object and loading state
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Initialize loading state
  useEffect(() => {
    setLoading(false)
  }, [])

  // -------------------------- Login --------------------------------->

  const login = (username, password) => {
    setLoading(true)
    setError('')

    return authService.login(username, password)
      .then(res => {
        // Extract tokens from headers
        const accessToken = res.data.access_token
        const refreshToken = res.data.refresh_token
        setTokens({ accessToken, refreshToken })

        // Set user state
        const u = res.data.user
        const loggedInUser = {
          username: u.username,
          email: u.email,
          role: u.role
        }
        setUser(loggedInUser)

        return loggedInUser
      })
      .catch(err => {
        setError(err.response?.data?.detail || err.message)
        return null
      })
      .finally(() => {
        setLoading(false)
      })
  }

  // -------------------------- Sign up --------------------------------->

  const signup = (username, name, email, password, role) => {
    setLoading(true)
    setError('')
    return authService.signup(username, name, email, password, role)
      .catch(err => {
        setError(err.response?.data?.detail || err.message)
        return null
      })
      .finally(() => {
        setLoading(false)
      })
  }

  // -------------------------- Logout --------------------------------->

  const logout = () => {
    setLoading(true)
    setError('')

    clearTokens()
    setUser({ username: "", email: "", role: "" })

    authService.logout()
      .catch(err => {
        setError(err.response?.data?.detail || err.message)
      })
      .finally(() => {
        setLoading(false)
      })
  }

  // ------------------------------------------------------------------>

  return (
    <AuthContext.Provider
      value={{ user, loading, error, login, signup, logout, setUser, setLoading, setError }}
    >
      {children}
    </AuthContext.Provider>
  )
}
