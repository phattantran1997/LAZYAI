import axios from 'axios'
import { getAccessToken, getRefreshToken, setTokens, clearTokens } from '../services/tokenStorage'

const apiClient = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
})

// Attach access token to every request
apiClient.interceptors.request.use(config => {
    const token = getAccessToken()
    if (token) config.headers.Authorization = `Bearer ${token}`
    return config
})

// // Refresh logic
// let isRefreshing = false
// let pendingRequests = []

// apiClient.interceptors.response.use(
//     res => res,
//     err => {
//         const { config, response } = err
//         if (!response || response.status !== 401 || config._retry) {
//             return Promise.reject(err)
//         }
//         // Prevent infinite refresh attempts
//         if (config._refreshTried) {
//             clearTokens()
//             window.location.href = '/login'
//             return Promise.reject(err)
//         }
//         config._retry = true
//         config._refreshTried = true

//         if (!isRefreshing) {
//             isRefreshing = true
//             const refreshToken = getRefreshToken()
//             return apiClient.post('/auth/refresh', { token: refreshToken })
//                 .then(({ data }) => {
//                     setTokens(data)
//                     isRefreshing = false
//                     pendingRequests.forEach(cb => cb(data.accessToken))
//                     pendingRequests = []
//                     config.headers.Authorization = `Bearer ${data.accessToken}`
//                     return apiClient(config)
//                 })
//                 .catch(fail => {
//                     clearTokens()
//                     window.location.href = '/login'
//                     return Promise.reject(fail)
//                 })
//         }

//         // Queue requests while refreshing
//         return new Promise(resolve => {
//             pendingRequests.push((newAccessToken) => {
//                 config.headers.Authorization = `Bearer ${newAccessToken}`
//                 resolve(apiClient(config))
//             })
//         })
//     }
// )

export default apiClient