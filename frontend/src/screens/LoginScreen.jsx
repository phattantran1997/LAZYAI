import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { LogIn, Eye, EyeOff } from 'lucide-react'

const LoginScreen = () => {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [formError, setFormError] = useState('')
  const { loading, error, login, fetchCurrentUser } = useAuth()

  const navigate = useNavigate()

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const currentUser = await fetchCurrentUser();
        if (currentUser?.role === 'Teachers') {
          navigate('/teacher')
        } else if (currentUser?.role === 'Students') {
          navigate('/student')
        }
      } catch (error) {
        setFormError(error.message)
      }
    }
    checkAuth()
  }, [])

  // Validation logic
  const isUsernameValid = username.length >= 3 && username.length <= 50
  const isPasswordValid = password.length >= 8 && password.length <= 100
  const isFormValid = isUsernameValid && isPasswordValid

  const handleSubmit = async (e) => {
    e.preventDefault()
    setFormError('')
    if (!isFormValid) {
      setFormError('Please enter a valid username and password.')
      return
    }
    const loggedInUser = await login(username, password)
    if (loggedInUser?.role === 'Teachers') {
      navigate('/teacher')
    } else if (loggedInUser?.role === 'Students') {
      navigate('/student')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <Card className="w-full max-w-md">

        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl font-bold text-center">Welcome back</CardTitle>
          <CardDescription className="text-center">
            Enter your credentials to access your account
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
                minLength={3}
                maxLength={50}
              />
              {!isUsernameValid && username.length > 0 && (
                <div className="text-red-500 text-xs">Username must be 3-50 characters.</div>
              )}
            </div>
            <div className="space-y-2">
              <label htmlFor="password" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                Password
              </label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  minLength={8}
                  maxLength={100}
                />
                <button
                  type="button"
                  className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-500"
                  onClick={() => setShowPassword((prev) => !prev)}
                  tabIndex={-1}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
              {!isPasswordValid && password.length > 0 && (
                <div className="text-red-500 text-xs">Password must be 8-100 characters.</div>
              )}
            </div>
          </CardContent>

          <CardFooter className="flex flex-col space-y-2">
            <Button type="submit" className="w-full" disabled={loading || !isFormValid}>
              <LogIn className="mr-2 h-4 w-4" />
              {loading ? 'Signing In...' : 'Sign In'}
            </Button>
            {(formError || error) && <div className="text-red-500 text-sm mb-2">{formError || error}</div>}
          </CardFooter>

        </form>

        <CardFooter className="items-center justify-center">
          <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
            Haven't got an account?
          </label>
          <a
            href="/signup"
            className="text-sm font-medium underline text-blue-500 leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 pl-3 hover:cursor-pointer"
          >
            Sign up
          </a>
        </CardFooter>

      </Card>
    </div>
  )
}

export default LoginScreen