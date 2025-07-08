import React, { useState, useEffect } from 'react'
import { PersonaPanel, MessageBubble, MemorySidebar } from '../components'
import { apiClient, type MemoryData, type User } from '../utils/api'

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
  
  // User management state
  const [currentUser, setCurrentUser] = useState<User | null>(null)
  const [allUsers, setAllUsers] = useState<User[]>([])
  const [isCreatingUser, setIsCreatingUser] = useState(false)
  const [showUserDropdown, setShowUserDropdown] = useState(false)
  const [editingName, setEditingName] = useState(false)
  const [editNameValue, setEditNameValue] = useState('')

  const sagePersona = {
    name: 'Sage',
    role: 'The Nurturer',
    description: 'A compassionate guide offering gentle wisdom and therapeutic support'
  }

  // Initialize user on component mount
  useEffect(() => {
    initializeUser()
  }, [])

  // Load memory when current user changes
  useEffect(() => {
    if (currentUser) {
      loadMemoryForUser(currentUser.user_id)
    }
  }, [currentUser])

  const initializeUser = async () => {
    try {
      // Try to load existing users first
      const usersResponse = await apiClient.getAllUsers()
      setAllUsers(usersResponse.users)

      // If there are existing users, use the most recent one
      if (usersResponse.users.length > 0) {
        setCurrentUser(usersResponse.users[0]) // Already sorted by last_active
      } else {
        // Create first user with auto-generated friendly name
        await createNewUser()
      }
    } catch (error) {
      console.error('Error initializing user:', error)
      setError('Failed to initialize user. Please refresh the page.')
    }
  }

  const createNewUser = async (customName?: string) => {
    setIsCreatingUser(true)
    try {
      const newUser = await apiClient.createUser({ name: customName })
      setCurrentUser(newUser)
      
      // Refresh users list
      const usersResponse = await apiClient.getAllUsers()
      setAllUsers(usersResponse.users)
      
      // Clear any existing messages for fresh start
      setMessages([])
      setMemoryData(null)
      
    } catch (error) {
      console.error('Error creating user:', error)
      setError('Failed to create new user. Please try again.')
    } finally {
      setIsCreatingUser(false)
    }
  }

  const switchToUser = async (userId: string) => {
    const user = allUsers.find(u => u.user_id === userId)
    if (user) {
      setCurrentUser(user)
      setMessages([]) // Clear current conversation
      setShowUserDropdown(false)
    }
  }

  const loadMemoryForUser = async (userId: string) => {
    try {
      const memory = await apiClient.getMemory(userId)
      setMemoryData(memory)
    } catch (error) {
      console.log('No memory found for user:', userId)
      setMemoryData(null)
    }
  }

  const handleUpdateUserName = async () => {
    if (!currentUser || !editNameValue.trim()) return

    try {
      const updatedUser = await apiClient.updateUser(currentUser.user_id, { 
        name: editNameValue.trim() 
      })
      setCurrentUser(updatedUser)
      
      // Update in users list
      setAllUsers(prev => prev.map(u => 
        u.user_id === updatedUser.user_id ? updatedUser : u
      ))
      
      setEditingName(false)
      setEditNameValue('')
    } catch (error: any) {
      console.error('Error updating user name:', error)
      const errorMessage = error.message || 'Failed to update name'
      setError(errorMessage)
    }
  }

  const startEditingName = () => {
    if (currentUser) {
      setEditNameValue(currentUser.name)
      setEditingName(true)
    }
  }

  const cancelEditingName = () => {
    setEditingName(false)
    setEditNameValue('')
  }

  const handleSendMessage = async (content: string) => {
    if (isLoading || !currentUser) return
    
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
        user_id: currentUser.user_id
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
      await loadMemoryForUser(currentUser.user_id)

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
    if (!currentUser) return

    // Only fetch memory if we don't already have it
    if (!memoryData) {
      await loadMemoryForUser(currentUser.user_id)
    }
    setIsMemorySidebarOpen(true)
  }

  if (!currentUser && !isCreatingUser) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-collaborative-background">
      {/* Main Content */}
      <div className="w-full max-w-4xl xl:max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex-1 flex flex-col min-w-0">
          {/* Header */}
          <header className="bg-collaborative-surface shadow-sm border-b border-pastel-purple-100 p-3 md:p-4 rounded-t-lg">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <div className="flex flex-col sm:flex-row items-start sm:items-center space-y-2 sm:space-y-0 sm:space-x-4 min-w-0 flex-1">
                {/* Logo */}
                <div className="flex items-center flex-shrink-0">
                  <img 
                    src="/assets/collaborative-logo.png" 
                    alt="Collaborative Solutions" 
                    className="h-8 md:h-10 w-auto"
                  />
                </div>
                
                {/* User Info & Controls */}
                {currentUser && (
                  <div className="flex items-center space-x-2 min-w-0">
                    <span className="text-collaborative-text-light flex-shrink-0 text-sm">Hello,</span>
                    {editingName ? (
                      <div className="flex items-center space-x-2 min-w-0">
                        <input
                          type="text"
                          value={editNameValue}
                          onChange={(e) => setEditNameValue(e.target.value)}
                          className="px-2 py-1 input-pastel text-sm min-w-0 w-20 sm:w-28"
                          onKeyDown={(e) => e.key === 'Enter' && handleUpdateUserName()}
                          autoFocus
                        />
                        <button
                          onClick={handleUpdateUserName}
                          className="text-collaborative-success hover:text-pastel-mint-400 text-sm transition-colors flex-shrink-0"
                        >
                          ✓
                        </button>
                        <button
                          onClick={cancelEditingName}
                          className="text-collaborative-error hover:opacity-80 text-sm transition-colors flex-shrink-0"
                        >
                          ✗
                        </button>
                      </div>
                    ) : (
                      <button
                        onClick={startEditingName}
                        className="text-brand font-medium hover:text-brand-dark transition-colors truncate max-w-28 sm:max-w-40 text-sm"
                      >
                        {currentUser.name}
                      </button>
                    )}
                  </div>
                )}
              </div>

              <div className="flex items-center space-x-2 w-full sm:w-auto">
                {/* User Dropdown */}
                <div className="relative flex-1 sm:flex-initial">
                  <button
                    onClick={() => setShowUserDropdown(!showUserDropdown)}
                    className="button-secondary text-xs font-medium w-full sm:w-auto whitespace-nowrap px-2 sm:px-3 py-2"
                  >
                    <span className="hidden sm:inline">Switch User ({allUsers.length})</span>
                    <span className="sm:hidden">Users ({allUsers.length})</span>
                  </button>
                  
                  {showUserDropdown && (
                    <div className="absolute right-0 mt-2 w-full sm:w-60 card-pastel shadow-lg z-10">
                      <div className="p-2">
                        <button
                          onClick={() => { createNewUser(); setShowUserDropdown(false); }}
                          className="w-full text-left px-3 py-2 text-sm text-brand hover:bg-pastel-purple-50 rounded transition-colors"
                          disabled={isCreatingUser}
                        >
                          + Create New User
                        </button>
                        
                        {allUsers.length > 0 && (
                          <div className="border-t border-pastel-purple-100 mt-2 pt-2">
                            {allUsers.map(user => (
                              <button
                                key={user.user_id}
                                onClick={() => switchToUser(user.user_id)}
                                className={`w-full text-left px-3 py-2 text-sm rounded transition-colors hover:bg-pastel-purple-50 ${
                                  currentUser?.user_id === user.user_id 
                                    ? 'bg-pastel-purple-100 text-brand border border-pastel-purple-200' 
                                    : 'text-collaborative-text'
                                }`}
                              >
                                <div className="font-medium truncate">{user.name}</div>
                                <div className="text-xs text-collaborative-text-light truncate">
                                  {user.moment_count} conversations
                                </div>
                              </button>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>

                <button
                  onClick={handleViewMemory}
                  className="button-primary disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0 px-2 sm:px-4 py-2 text-xs"
                  disabled={isLoading || !currentUser}
                >
                  <span className="hidden sm:inline">View Memory</span>
                  <span className="sm:hidden">Memory</span>
                </button>
              </div>
            </div>
          </header>

          {/* Error Message */}
          {error && (
            <div className="mt-4 p-3 bg-pastel-peach-50 border border-pastel-peach-200 text-collaborative-error rounded-lg">
              <div className="flex items-start justify-between">
                <span className="flex-1 text-sm pr-2">{error}</span>
                <button
                  onClick={() => setError(null)}
                  className="text-collaborative-error hover:opacity-80 transition-opacity flex-shrink-0"
                >
                  ×
                </button>
              </div>
            </div>
          )}

          {/* Persona Panel */}
          <div className="mt-4">
            <PersonaPanel persona={sagePersona} />
          </div>

          {/* Chat Area */}
          <div className="flex-1 flex flex-col min-h-0 mt-4">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-collaborative-surface rounded-lg border border-pastel-purple-100">
              {messages.length === 0 ? (
                <div className="text-center text-collaborative-text-light mt-8">
                  <p className="heading-sm text-collaborative-text">Start a conversation with Sage</p>
                  <p className="text-sm mt-2">Welcome to your therapeutic journey</p>
                  <div className="mt-4 inline-block px-4 py-2 bg-pastel-purple-50 rounded-full text-xs text-brand">
                    ✨ Powered by Collaborative Solutions
                  </div>
                </div>
              ) : (
                messages.map((message) => (
                  <MessageBubble key={message.id} message={message} />
                ))
              )}
              
              {/* Loading indicator */}
              {isLoading && (
                <div className="flex justify-start mb-4">
                  <div className="bg-pastel-purple-100 text-collaborative-text px-4 py-3 rounded-lg border border-pastel-purple-200">
                    <div className="flex items-center space-x-3">
                      <div className="animate-pulse-soft rounded-full h-4 w-4 bg-collaborative-primary"></div>
                      <span className="text-sm font-medium">Sage is thinking...</span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Message Input */}
            <div className="border-t border-pastel-purple-100 bg-collaborative-surface p-4 rounded-b-lg">
              <MessageInput 
                onSendMessage={handleSendMessage} 
                disabled={isLoading || !currentUser} 
              />
            </div>
          </div>
        </div>
      </div>

      {/* Memory Sidebar - Outside main content flow */}
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
    <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-4">
      <input
        type="text"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder={disabled ? "Please wait..." : "Type your message..."}
        disabled={disabled}
        className="flex-1 p-3 input-pastel disabled:opacity-50 disabled:cursor-not-allowed text-sm md:text-base"
      />
      <button
        type="submit"
        disabled={disabled || !message.trim()}
        className="button-primary disabled:opacity-50 disabled:cursor-not-allowed px-6 py-3 w-full sm:w-auto"
      >
        Send
      </button>
    </form>
  )
}

export default ChatPage 