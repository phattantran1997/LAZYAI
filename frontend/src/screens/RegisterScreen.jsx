import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { getAccessToken } from '../services/tokenStorage'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { LogIn } from 'lucide-react'

const RegisterScreen = () => {
    const [username, setUsername] = useState('')
    const [name, setName] = useState('')
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [repassword, setRepassword] = useState('')
    const [role, setRole] = useState('Students')
    const [localError, setLocalError] = useState('')

    const { loading, error, signup, user } = useAuth()
    const navigate = useNavigate()

    // Check if user is already authenticated
    useEffect(() => {
        const checkAuth = async () => {
            const accessToken = getAccessToken()
            if (accessToken && user.username) {
                // User is already logged in, redirect to appropriate dashboard
                if (user.role === 'Teachers') {
                    navigate('/teacher')
                } else if (user.role === 'Students') {
                    navigate('/student')
                }
            }
        }
        
        checkAuth()
    }, [user, navigate])

    // Validation logic
    const isUsernameValid = username.length >= 3 && username.length <= 50
    const isNameValid = name.length >= 2 && name.length <= 50
    const isEmailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
    const isPasswordValid = password.length >= 8 && password.length <= 100
    const isRePasswordValid = repassword === password && repassword.length > 0
    const isFormValid = isUsernameValid && isNameValid && isEmailValid && isPasswordValid && isRePasswordValid

    const handleSubmit = async (e) => {
        e.preventDefault()
        setLocalError('')
        if (!isFormValid) {
            setLocalError('Please fill all fields correctly.')
            return
        }
        const result = await signup(username, name, email, password, role)
        if (result && !error) {
            navigate('/login')
        }
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-background p-4">
            <Card className="w-full max-w-md">

                <CardHeader className="space-y-1">
                    <CardTitle className="text-2xl font-bold text-center">Welcome</CardTitle>
                    <CardDescription className="text-center">
                        Enter your credentials to register your account
                    </CardDescription>
                </CardHeader>

                <form onSubmit={handleSubmit}>
                    <CardContent className="space-y-4">
                        <div className="space-y-2">
                            <label htmlFor="username" className="text-sm font-medium">Username</label>
                            <Input
                                id="username"
                                type="text"
                                placeholder="Enter your username"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                required
                                minLength={3}
                                maxLength={50}
                            />
                            {!isUsernameValid && username.length > 0 && (
                                <div className="text-red-500 text-xs">Username must be 3-50 characters.</div>
                            )}
                        </div>
                        <div className="space-y-2">
                            <label htmlFor="name" className="text-sm font-medium">Full name</label>
                            <Input
                                id="name"
                                type="text"
                                placeholder="Enter your name"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                required
                                minLength={2}
                                maxLength={50}
                            />
                            {!isNameValid && name.length > 0 && (
                                <div className="text-red-500 text-xs">Name must be 2-50 characters.</div>
                            )}
                        </div>
                        <div className="space-y-2">
                            <label htmlFor="email" className="text-sm font-medium">Email</label>
                            <Input
                                id="email"
                                type="email"
                                placeholder="Enter your email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                            />
                            {!isEmailValid && email.length > 0 && (
                                <div className="text-red-500 text-xs">Enter a valid email address.</div>
                            )}
                        </div>
                        <div className="space-y-2">
                            <label htmlFor="password" className="text-sm font-medium">Password</label>
                            <div className="relative">
                                <Input
                                    id="password"
                                    type="password"
                                    placeholder="Enter your password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required
                                    minLength={8}
                                    maxLength={100}
                                />
                            </div>
                            {!isPasswordValid && password.length > 0 && (
                                <div className="text-red-500 text-xs">Password must be 8-100 characters.</div>
                            )}
                        </div>
                        <div className="space-y-2">
                            <label htmlFor="repassword" className="text-sm font-medium">Re-enter the password</label>
                            <div className="relative">
                                <Input
                                    id="repassword"
                                    type="password"
                                    placeholder="Re-enter your password"
                                    value={repassword}
                                    onChange={(e) => setRepassword(e.target.value)}
                                    required
                                />
                            </div>
                            {!isRePasswordValid && repassword.length > 0 && (
                                <div className="text-red-500 text-xs">Passwords do not match.</div>
                            )}
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Choose your role</label>
                            <select
                                className="w-full h-9 rounded-md border border-input text-sm font-medium pl-4"
                                onChange={(e) => setRole(e.target.value)}
                                value={role}
                            >
                                <option>Students</option>
                                <option>Teachers</option>
                            </select>
                        </div>
                    </CardContent>

                    <CardFooter className="flex flex-col">
                        <Button type="submit" className="w-full" disabled={loading || !isFormValid}>
                            <LogIn className="mr-2 h-4 w-4" />
                            {loading ? 'Register...' : 'Register'}
                        </Button>
                        {(localError || error) && (
                            <div className="text-red-500 text-sm mb-2">
                                {localError || error}
                            </div>
                        )}
                    </CardFooter>
                </form>

                <CardFooter className="items-center justify-center">
                    <label className="text-sm font-medium">
                        Already got an account ?
                    </label>
                    <a
                        href="/login"
                        className="text-sm font-medium underline text-blue-500 leading-none pl-3 hover:cursor-pointer"
                    >
                        Sign in
                    </a>
                </CardFooter>

            </Card>
        </div>
    )
}

export default RegisterScreen