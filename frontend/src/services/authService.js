// src/services/authService.js
import { loginRequest, registerRequest } from '../api/authApi'
import { setToken, clearToken, setUser, getToken, getUser } from '../utils/tokens'

export function login(username, password) {
    return loginRequest(username, password)
        .then(({ data }) => {
            // assuming your API returns { access_token, user }
            setToken(data.access_token)
            setUser(data.user)
            return data.user
        })
    // let callers handle errors
}

export function signup(username, name, email, password, role) {
    return registerRequest(username, name, email, password, role)
        .then(({ data }) => {
            setToken(data.access_token)
            setUser(data.user)
            return data.user
        })
}

export function logout() {
    clearToken()
}

export function rehydrate() {
    const token = getToken()
    const user = getUser()
    return { token, user }
}
