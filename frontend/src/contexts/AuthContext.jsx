import { createContext, useState, useEffect } from 'react'
import { setTokens, clearTokens } from '../services/tokenStorage'
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

  const fetchCurrentUser = async () => {
    setLoading(true)
    try {
      const u = await authService.getCurrentUser()
      const userData = {
        username: u.data.username,
        email: u.data.email,
        role: u.data.role
      }
      setUser(userData)
      return userData
    } catch (err) {
      return null
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    // Only fetch if user is not already set (lazy load)
    if (fetch) {
      fetchCurrentUser()
    } else {
      setLoading(false)
    }
  }, [fetch])



  // -------------------------- Login --------------------------------->

  // const login = (username, password) => {
  //   setLoading(true)
  //   setError('')

  //   return authService.login(username, password)
  //     .then(u => {
  //       const loggedInUser = {
  //         username: u.data.username,
  //         email: u.data.email,
  //         role: u.data.role
  //       }
  //       setUser(loggedInUser)
  //       return loggedInUser
  //     })
  //     .catch(err => {
  //       setError(err.response?.data?.detail || err.message)
  //       return null
  //     })
  //     .finally(() => {
  //       setLoading(false)
  //     })
  // }

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

  // const logout = () => {
  //   setLoading(true);
  //   setError('');

  //   authService.logout()
  //     .then(() => {
  //       setUser({ username: "", email: "", role: "" })
  //     })
  //     .catch(err => {
  //       setError(err.response?.data?.detail || err.message)
  //     })
  //     .finally(() => {
  //       setLoading(false)
  //     })
  // }

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
      value={{ user, loading, error, login, signup, logout, setFetching, fetchCurrentUser }}
    >
      {children}
    </AuthContext.Provider>
  )
}
