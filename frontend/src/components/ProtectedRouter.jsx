import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { getAccessToken, getRefreshToken, setTokens, clearTokens } from '../services/tokenStorage'
import { getCurrentUserRequest } from '../api/authApi'
import apiClient from '../api/api-client'

const ProtectedRouter = ({ children, requiredRole }) => {
  const { user, setUser, setLoading, setError } = useAuth()
  const [isLoading, setIsLoading] = useState(true)
  const navigate = useNavigate()

  const handleAuthentication = async () => {
    setLoading(true)
    
    const accessToken = getAccessToken()
    const refreshToken = getRefreshToken()

    // If no access token, try refreshing with the refresh token
    if (!accessToken && refreshToken) {
      try {
        const response = await apiClient.post('/auth/refresh', {}, { headers: { 'x-refresh-token': refreshToken } })
        const newAccessToken = response.data.access_token
        setTokens({ accessToken: newAccessToken, refreshToken })
        
        const userResponse = await getCurrentUserRequest()
        setUser(userResponse.data)
        return
      } catch (err) {
        clearTokens()
        setUser(null)
        navigate('/login')
        return
      }
    }

    // If no tokens, redirect to login
    if (!accessToken) {
      clearTokens()
      setUser(null)
      navigate('/login')
      return
    }

    // Validate and refresh tokens if needed
    try {
      const userResponse = await getCurrentUserRequest()
      setUser(userResponse.data)
    } catch (error) {
      if (error.response?.status === 401) {
        const refreshResponse = await apiClient.post('/auth/refresh', {}, { headers: { 'x-refresh-token': refreshToken } })
        const newAccessToken = refreshResponse.data.access_token
        setTokens({ accessToken: newAccessToken, refreshToken })
        const userResponse = await getCurrentUserRequest()
        setUser(userResponse.data)
      } else {
        clearTokens()
        setUser(null)
        navigate('/login')
      }
    }
  }

  useEffect(() => {
    handleAuthentication()
      .catch((err) => {
        console.error('Authentication error:', err)
        setError(err.message)
        setUser(null)
        clearTokens()
        navigate('/login')
      })
      .finally(() => setIsLoading(false))
  }, [navigate, setUser, setLoading, setError])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-gray-900"></div>
      </div>
    )
  }

  if (!user) return null
  if (requiredRole && user.role !== requiredRole) {
    navigate(user.role === 'Teachers' ? '/teacher' : '/student')
    return null
  }

  // Render children if user is authenticated and has correct role
  return children
}

export default ProtectedRouter
