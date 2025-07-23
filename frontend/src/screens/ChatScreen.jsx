import { useState, useRef, useEffect } from 'react'
import { useAuth } from '../hooks/useAuth'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Send, SofaIcon } from 'lucide-react'
import axios from 'axios'

const ChatScreen = () => {
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: 'Hello! How can I help you today?',
      sender: 'ai',
      timestamp: new Date(Date.now() - 3600000),
    }
  ])
  const scrollRef = useRef(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  const handleSubmit = (e) => {
    e.preventDefault()

    // Set Message user
    const userMessage = {
      id: messages.length + 1,
      text: message,
      sender: 'user',
      timestamp: new Date(Date.now() - 3600000),
    }
    setMessages((prevArray) => [...prevArray, userMessage])
    setMessage("");


    // Send message to AI
    axios.post('http://localhost:8000/chat/ask', { message: message, unit_name: localStorage.getItem('unitname') })  // Send message object if API expects it that way
      .then((response) => {
        const AiMessage = {
          id: messages.length + 2,  // Increment ID by 1 more than user message
          text: response.data.text,  // Assuming response contains the text field
          sender: 'ai',
          timestamp: new Date(Date.now() - 3600000),
        }
        setMessages((prevArray) => [...prevArray, AiMessage]) // Append AI response to messages
      })
      .catch((e) => {
        const ErrorMessage = {
          id: messages.length + 2, // Increment ID by 1 more than user message
          text: "Failed to get response from AI",
          sender: 'ai',
          timestamp: new Date(Date.now() - 3600000),
        }
        setMessages((prevArray) => [...prevArray, ErrorMessage])
      })
  }

  return (
    <div className="flex h-[calc(100vh-4rem)] flex-col">
      <div className="flex-1 overflow-hidden">
        <ScrollArea ref={scrollRef} className="h-full px-4">
          <div className="space-y-4 py-4">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'
                  }`}
              >
                <div
                  className={`max-w-[70%] rounded-lg px-4 py-2 ${msg.sender === 'user'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted'
                    }`}
                >
                  <p className="text-sm">{msg.text}</p>
                  <p className="mt-1 text-xs opacity-70">
                    {msg.timestamp.toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>
      </div>

      <div className="border-t p-4">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <Input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Type your message..."
            className="flex-1"
          />
          <Button type="submit" size="icon">
            <Send className="h-4 w-4" />
          </Button>
        </form>
      </div>
    </div>
  )
}

export default ChatScreen
