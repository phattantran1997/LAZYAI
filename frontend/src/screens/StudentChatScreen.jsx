import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import StudentNameModal from '../components/StudentNameModal'
import { Button } from '@/components/ui/button'
import { LogOut } from 'lucide-react'

const StudentChatScreen = () => {
  const { teacherId } = useParams()
  const [studentName, setStudentName] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState([])

  // ---------------------- Ask for students' name --------------------------->

  useEffect(() => {
    // Check if user is logged in
    const user = JSON.parse(localStorage.getItem('user'))
    if (user) {
      setStudentName(user.username)
    }

    // Check if student name is already stored
    else {
      const storedName = localStorage.getItem('studentName')
      if (!storedName) {
        setShowModal(true)
      } else {
        setStudentName(storedName)
      }
    }

  }, [])

  // ---------------- Submit name if it has not been stored ---------------------->

  const handleNameSubmit = (name) => {
    setStudentName(name)
    localStorage.setItem('studentName', name)
    setShowModal(false)

    // // Simulate logging student
    // fetch('/api/log-student', {
    //   method: 'POST',
    //   headers: {
    //     'Content-Type': 'application/json',
    //   },
    //   body: JSON.stringify({
    //     studentName: name,
    //     teacherId,
    //   }),
    // }).catch(console.error)
  }

  // ---------------- Handle message submission --------------------------->

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!message.trim()) return

    // Add user message
    const newMessage = {
      id: messages.length + 1,
      text: message,
      sender: 'user',
      timestamp: new Date(),
    }
    setMessages([...messages, newMessage])
    setMessage('')

    // Simulate AI response
    setTimeout(() => {
      const aiResponse = {
        id: messages.length + 2,
        text: 'Thank you for your question. Let me help you with that.',
        sender: 'ai',
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, aiResponse])
    }, 1000)
  }

  // ---------------- Logout function --------------------------->

  const handleLogout = () => {
    if (window.confirm('Are you sure you want to logout? This will clear all your data.')) {
      // Clear specific localStorage items
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('studentName')
      localStorage.removeItem('user')
      
      alert('Logged out successfully! You will be redirected to login.')
      window.location.href = '/login'
    }
  }

  // ---------------- Render the chat screen --------------------------->

  if (showModal) {
    return <StudentNameModal onSubmit={handleNameSubmit} />
  }

  return (
    <div className="max-w-4xl mx-auto h-screen flex flex-col p-8">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-bold">Chat with {teacherId}</h1>
        <div className="flex items-center gap-4">
          <div className="text-sm text-gray-600">
            Logged in as: {studentName}
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={handleLogout}
            className="flex items-center gap-2"
          >
            <LogOut className="h-4 w-4" />
            Logout
          </Button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto mb-4 space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'
              }`}
          >
            <div
              className={`max-w-[70%] rounded-lg p-4 ${msg.sender === 'user'
                ? 'bg-primary text-white'
                : 'bg-gray-200 text-gray-800'
                }`}
            >
              <p>{msg.text}</p>
              <p className="text-xs mt-2 opacity-70">
                {msg.timestamp.toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="flex space-x-4">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type your message..."
          className="flex-1 p-2 border rounded-md"
        />
        <button
          type="submit"
          className="px-6 py-2 bg-primary text-white rounded-md hover:bg-primary-dark"
        >
          Send
        </button>
      </form>
    </div>
  )
}

export default StudentChatScreen 