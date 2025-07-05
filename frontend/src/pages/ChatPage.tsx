import React, { useState, useEffect } from 'react'
import { PersonaPanel, MessageBubble, MemorySidebar } from '../components'
import { apiClient, type MemoryData } from '../utils/api'

const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<Array<{
    id: string
    content: string
    sender: 'user' | 'sage'
    timestamp: Date
  }>>([])
  const [isMemorySidebarOpen, setIsMemorySidebarOpen] = useState(false)
  const [memoryData, setMemoryData] = useState<MemoryData | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [userId] = useState(() => `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`)

  const sagePersona = {
    name: 'Sage',
    role: 'The Nurturer',
    description: 'A compassionate guide offering gentle wisdom and therapeutic support'
  }

  // Load memory data when the component mounts
  useEffect(() => {
    const loadMemory = async () => {
      console.log('Loading initial memory for user:', userId)
      try {
        const memory = await apiClient.getMemory(userId)
        setMemoryData(memory)
        console.log('Initial memory loaded successfully for user:', userId)
      } catch (error) {
        console.log('Memory not found for new user:', userId)
        // This is expected for new users, so we don't set an error
      }
    }
    loadMemory()
  }, [userId])

  const handleSendMessage = async (content: string) => {
    if (isLoading) return
    
    setError(null)
    setIsLoading(true)

    // Add user message immediately
    const userMessage = {
      id: Date.now().toString(),
      content,
      sender: 'user' as const,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, userMessage])

    try {
      // Call the backend API
      const response = await apiClient.sendMessage({
        message: content,
        user_id: userId
      })

      // Add Sage response
      const sageResponse = {
        id: (Date.now() + 1).toString(),
        content: response.persona_response,
        sender: 'sage' as const,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, sageResponse])

      // Refresh memory data after the conversation
      try {
        console.log('Refreshing memory after message for user:', userId)
        const updatedMemory = await apiClient.getMemory(userId)
        setMemoryData(updatedMemory)
        console.log('Memory refreshed successfully after message for user:', userId)
      } catch (memoryError) {
        console.log('Could not update memory:', memoryError)
      }

    } catch (error) {
      setError('Failed to send message. Please try again.')
      console.error('Error sending message:', error)
      
      // Remove the user message on error
      setMessages(prev => prev.filter(msg => msg.id !== userMessage.id))
    } finally {
      setIsLoading(false)
    }
  }

  const handleViewMemory = async () => {
    // Only fetch memory if we don't already have it
    if (!memoryData) {
      try {
        const memory = await apiClient.getMemory(userId)
        setMemoryData(memory)
      } catch (error) {
        console.error('Error loading memory:', error)
        setError('Failed to load memory data')
        return
      }
    }
    setIsMemorySidebarOpen(true)
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
              onClick={handleViewMemory}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
              disabled={isLoading}
            >
              View Memory
            </button>
          </div>
        </header>

        {/* Error Message */}
        {error && (
          <div className="mx-4 mt-4 p-3 bg-red-100 border border-red-300 text-red-700 rounded-md">
            {error}
            <button
              onClick={() => setError(null)}
              className="ml-2 text-red-500 hover:text-red-700"
            >
              ×
            </button>
          </div>
        )}

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
                <p className="text-sm mt-2">Your unique ID: {userId}</p>
              </div>
            ) : (
              messages.map((message) => (
                <MessageBubble key={message.id} message={message} />
              ))
            )}
            
            {/* Loading indicator */}
            {isLoading && (
              <div className="flex justify-start mb-4">
                <div className="bg-gray-200 text-gray-800 px-4 py-2 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                    <span className="text-sm">Sage is thinking...</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Message Input */}
          <div className="border-t bg-white p-4">
            <MessageInput onSendMessage={handleSendMessage} disabled={isLoading} />
          </div>
        </div>
      </div>

      {/* Memory Sidebar */}
      <MemorySidebar
        memoryData={memoryData}
        isOpen={isMemorySidebarOpen}
        onClose={() => setIsMemorySidebarOpen(false)}
      />
    </div>
  )
}

// Message Input Component
const MessageInput: React.FC<{ 
  onSendMessage: (message: string) => void
  disabled?: boolean
}> = ({ onSendMessage, disabled = false }) => {
  const [message, setMessage] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (message.trim() && !disabled) {
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
        className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
        disabled={disabled}
      />
      <button
        type="submit"
        className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
        disabled={disabled || !message.trim()}
      >
        Send
      </button>
    </form>
  )
}

export default ChatPage 