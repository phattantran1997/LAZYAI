import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import {
  Upload,
  MessageSquare,
  FileCheck,
  ChevronLeft,
  ChevronRight,
  LogOut,
  User,
} from 'lucide-react'

const Sidebar = () => {
  const [isCollapsed, setIsCollapsed] = useState(false)
  const { user, logout } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()

  const teacherMenuItems = [
    { path: '/teacher/upload', label: 'Upload Material', icon: Upload },
    { path: '/teacher/chat', label: 'Chat with AI', icon: MessageSquare },
    { path: '/teacher/mark', label: 'Mark Assignment', icon: FileCheck },
  ]

  const studentMenuItems = [
    { path: '/student/chat', label: 'Chat with AI', icon: MessageSquare },
    { path: '/student/assignments', label: 'My Assignments', icon: FileCheck },
  ]

  const menuItems = user?.isTeacher ? teacherMenuItems : studentMenuItems

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div
      className={`relative h-screen bg-card border-r transition-all duration-300 ${isCollapsed ? 'w-16' : 'w-64'
        }`}
    >
      <div className="flex h-14 items-center border-b px-4">
        {!isCollapsed && <h1 className="text-lg font-semibold">LAZYAI</h1>}
        <Button
          variant="ghost"
          size="icon"
          className="ml-auto"
          onClick={() => setIsCollapsed(!isCollapsed)}
        >
          {isCollapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </Button>
      </div>

      <ScrollArea className="h-[calc(100vh-8rem)]">
        <nav className="grid gap-1 p-2">
          {menuItems.map((item) => {
            const Icon = item.icon
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors ${location.pathname === item.path
                    ? 'bg-accent text-accent-foreground'
                    : 'hover:bg-accent hover:text-accent-foreground'
                  }`}
              >
                <Icon className="h-4 w-4" />
                {!isCollapsed && <span>{item.label}</span>}
              </Link>
            )
          })}
        </nav>
      </ScrollArea>

      <div className="absolute bottom-0 w-full border-t p-4">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10">
            <User className="h-4 w-4 text-primary" />
          </div>
          {!isCollapsed && (
            <div className="flex-1">
              <p className="text-sm font-medium">{user?.username}</p>
              <p className="text-xs text-muted-foreground">
                {user?.isTeacher ? 'Teacher' : 'Student'}
              </p>
            </div>
          )}
        </div>
        <Button
          variant="ghost"
          size="sm"
          className="mt-4 w-full justify-start"
          onClick={handleLogout}
        >
          <LogOut className="mr-2 h-4 w-4" />
          {!isCollapsed && 'Logout'}
        </Button>
      </div>
    </div>
  )
}

export default Sidebar 