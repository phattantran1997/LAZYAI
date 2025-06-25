// src/services/authService.js
import { loginRequest, registerRequest, logoutRequest, getCurrentUserRequest } from '../api/authApi'

// -------------------------- Login --------------------------------------->

export function login(username, password) {
    return loginRequest(username, password)
}

// -------------------------- Sign up --------------------------------------->

export function signup(username, name, email, password, role) {
    return registerRequest(username, name, email, password, role)
}

// -------------------------- Logout --------------------------------------->

export function logout() {
    return logoutRequest()
}

// ----------------------- Get current user -------------------------------->

export function getCurrentUser() {
    return getCurrentUserRequest()
}

