import apiClient from './api-client'

// -------------------------- Login request ------------------------------------->

export function loginRequest(username, password) {
  return apiClient.post('/users/login', { username, password })
}

// -------------------------- Register request ------------------------------------->

export function registerRequest(username, name, email, password, role) {
  return apiClient.post('/users/register',
    { username, name, email, password, role }
  )
}

// -------------------------- Logout request ------------------------------------->

export function logoutRequest() {
  return apiClient.post('/users/logout')
}

// -------------------------- Get current user request ------------------------------------->

export function getCurrentUserRequest() {
  return apiClient.get('/auth/me')
}