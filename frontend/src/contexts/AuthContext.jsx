import { createContext, useState, useEffect } from 'react'
import * as authService from '../services/authService'

export const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  // Information about the current user
  const [user, setUser] = useState({ "username": "", "email": "", "role": "" })

  // User object and loading state
  const [fetch, setFetching] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')


  // -------------------------- Get current user ------------------------------------->

  useEffect(() => {
    // Only fetch if user is not already set (lazy load)
    if (fetch) {
      setLoading(true)
      setError("")

      authService.getCurrentUser()
        .then(u => {
          setUser({
            username: u.data.username,
            email: u.data.email,
            role: u.data.role
          })
        })
        .catch(err => {
          setError(err.response?.data?.detail || err.message)
        })
        .finally(() => {
          setLoading(false)
        })
    } else {
      setLoading(false)
    }
  }, [fetch])


  // -------------------------- Login --------------------------------->

  const login = (username, password) => {
    setLoading(true)
    setError('')

    return authService.login(username, password)
      .then(u => {
        const loggedInUser = {
          username: u.data.username,
          email: u.data.email,
          role: u.data.role
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

    const skip = ['/login', '/signup'];
    const path = typeof window !== 'undefined'
      ? window.location.pathname
      : '';

    if (skip.includes(path)) {
      setLoading(false);
      return;
    }

    setLoading(true)
    setError('')

    authService.signup(username, name, email, password, role)
      .catch(err => {
        setError(err.response?.data?.detail || err.message)
      })
      .finally(() => {
        setLoading(false)
      })
  }

  // -------------------------- Logout --------------------------------->

  const logout = () => {
    setLoading(true);
    setError('');

    authService.logout()
      .then(() => {
        setUser({ username: "", email: "", role: "" })
      })
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
      value={{ user, loading, error, login, signup, logout, setFetching }}
    >
      {children}
    </AuthContext.Provider>
  )
}
