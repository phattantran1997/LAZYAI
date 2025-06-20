const TOKEN_KEY = 'token'
const USER_KEY = 'user'

// ------------------- Token Management ------------------->

export const getToken = () => localStorage.getItem(TOKEN_KEY)
export const setToken = (t) => localStorage.setItem(TOKEN_KEY, t)
export const clearToken = () => {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
}

// ------------------- User Management ------------------->

export const getUser = () => {
    const u = localStorage.getItem(USER_KEY)
    return u ? JSON.parse(u) : null
}
export const setUser = (u) => localStorage.setItem(USER_KEY, JSON.stringify(u))
