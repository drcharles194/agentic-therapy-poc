import React, { useState } from 'react'
import { PersonaPanel, MessageBubble, MemorySidebar } from '../components'

const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<Array<{
    id: string
    content: string
    sender: 'user' | 'sage'
    timestamp: Date
  }>>([])
  const [isMemorySidebarOpen, setIsMemorySidebarOpen] = useState(false)

  const sagePersona = {
    name: 'Sage',
    role: 'The Nurturer',
    description: 'A compassionate guide offering gentle wisdom and therapeutic support'
  }

  const handleSendMessage = (content: string) => {
    // Add user message
    const newMessage = {
      id: Date.now().toString(),
      content,
      sender: 'user' as const,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, newMessage])
    
    // Simulate Sage response (will be replaced with actual API call)
    setTimeout(() => {
      const sageResponse = {
        id: (Date.now() + 1).toString(),
        content: `I hear you saying: "${content}". That sounds like something that carries weight for you. Would you like to explore what's beneath the surface?`,
        sender: 'sage' as const,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, sageResponse])
    }, 1000)
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <div className="flex-1 flex flex-col max-w-4xl mx-auto">
        {/* Header */}
        <header className="bg-white shadow-sm border-b p-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-900">
              Agentic Therapy
            </h1>
            <button
              onClick={() => setIsMemorySidebarOpen(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              View Memory
            </button>
          </div>
        </header>

        {/* Persona Panel */}
        <div className="p-4">
          <PersonaPanel persona={sagePersona} />
        </div>

        {/* Chat Area */}
        <div className="flex-1 flex flex-col">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 ? (
              <div className="text-center text-gray-500 mt-8">
                <p>Start a conversation with Sage</p>
              </div>
            ) : (
              messages.map((message) => (
                <MessageBubble key={message.id} message={message} />
              ))
            )}
          </div>

          {/* Message Input */}
          <div className="border-t bg-white p-4">
            <MessageInput onSendMessage={handleSendMessage} />
          </div>
        </div>
      </div>

      {/* Memory Sidebar */}
      <MemorySidebar
        isOpen={isMemorySidebarOpen}
        onClose={() => setIsMemorySidebarOpen(false)}
      />
    </div>
  )
}

// Message Input Component
const MessageInput: React.FC<{ onSendMessage: (message: string) => void }> = ({ onSendMessage }) => {
  const [message, setMessage] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (message.trim()) {
      onSendMessage(message)
      setMessage('')
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex space-x-2">
      <input
        type="text"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Type your message..."
        className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <button
        type="submit"
        className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        Send
      </button>
    </form>
  )
}

export default ChatPage 