import axios from 'axios'

// -------------------------- API URL ------------------------------------->

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// -------------------------- Login request ------------------------------------->

export function loginRequest(username, password) {
  return axios.post(`${API_URL}/users/login`, { username, password })
}

// -------------------------- Register request ------------------------------------->

export function registerRequest(username, name, email, password, role) {
  return axios.post(`${API_URL}/users/register`,
    { username, name, email, password, role }
  )
}