import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
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
    const navigate = useNavigate()
    const { signup, loading, error, setError } = useAuth()

    const handleSubmit = async (e) => {
        e.preventDefault()
        setError('')
        try {
            if (password !== repassword) {
                setError('Passwords do not match')
                return
            }
            await signup(username, name, email, password, role)
            navigate('/login')
        } catch (err) {
            // error is already set in context
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
                            <label htmlFor="username" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                                Username
                            </label>
                            <Input
                                id="username"
                                type="text"
                                placeholder="Enter your username"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                required
                            />
                        </div>
                        <div className="space-y-2">
                            <label htmlFor="username" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                                Full name
                            </label>
                            <Input
                                id="username"
                                type="text"
                                placeholder="Enter your name"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                required
                            />
                        </div>
                        <div className="space-y-2">
                            <label htmlFor="username" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                                Email
                            </label>
                            <Input
                                id="username"
                                type="text"
                                placeholder="Enter your email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                            />
                        </div>
                        <div className="space-y-2">
                            <label htmlFor="password" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                                Password
                            </label>
                            <Input
                                id="password"
                                type="password"
                                placeholder="Enter your password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />
                        </div>
                        <div className="space-y-2">
                            <label htmlFor="repassword" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                                Re-enter the password
                            </label>
                            <Input
                                id="repassword"
                                type="password"
                                placeholder="Re-enter your password"
                                value={repassword}
                                onChange={(e) => setRepassword(e.target.value)}
                                required
                            />
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                                Choose your role
                            </label>
                            <select
                                className="w-full h-9 rounded-md border border-input text-sm font-medium pl-4"
                                onChange={(e) => setRole(e.target.value)}
                            >
                                <option>
                                    Students
                                </option>
                                <option>
                                    Teachers
                                </option>
                            </select>
                        </div>
                    </CardContent>

                    <CardFooter>
                        {error && <div className="text-red-500 text-sm mb-2">{error}</div>}
                        <Button type="submit" className="w-full" disabled={loading}>
                            <LogIn className="mr-2 h-4 w-4" />
                            {loading ? 'Register...' : 'Register'}
                        </Button>
                    </CardFooter>

                </form>

                <CardFooter className="items-center justify-center">
                    <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                        Already got an account ?
                    </label>
                    <a
                        href="/login"
                        className="text-sm font-medium underline text-blue-500 leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 pl-3 hover:cursor-pointer"
                    >
                        Sign in
                    </a>
                </CardFooter>

            </Card>
        </div>
    )
}

export default RegisterScreen