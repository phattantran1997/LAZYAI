import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

const AuthRedirect = () => {
    const { error, fetchCurrentUser } = useAuth()
    const navigate = useNavigate()

    useEffect(() => {
        (async () => {
            const currentUser = await fetchCurrentUser()
            if (!currentUser || error) {
                navigate('/login', { replace: true })
            } else if (currentUser.role === 'Teachers') {
                navigate('/teacher', { replace: true })
            } else if (currentUser.role === 'Students') {
                navigate('/student', { replace: true })
            }
        })()
    }, [fetchCurrentUser, error, navigate])

    return null
}

export default AuthRedirect