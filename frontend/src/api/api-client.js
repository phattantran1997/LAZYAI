import axios from 'axios'
import { getAccessToken, getRefreshToken, setTokens } from '../services/tokenStorage'

const apiClient = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
})

// Attach access token to every request
apiClient.interceptors.request.use(config => {
    const token = getAccessToken()
    if (token) config.headers.Authorization = `Bearer ${token}`
    return config
})

// Handle Refresh token
apiClient.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;
        if (error.response.status === 401
            && !originalRequest._retry) {
            originalRequest._retry = true;
            try {
                const refreshToken = getRefreshToken()
                const response = await apiClient.post('/auth/refresh', {}, {
                    headers: { 'x-refresh-token': refreshToken }
                });
                const newAccessToken = response.data.access_token;
                setTokens({ accessToken: newAccessToken, refreshToken })
                originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
                return apiClient(originalRequest);
            } catch (refreshError) {

                console.error('Refresh token failed:', refreshError);

            }
        }
        return Promise.reject(error);
    }
);

export default apiClient