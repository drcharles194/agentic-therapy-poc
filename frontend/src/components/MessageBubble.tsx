import React from 'react'
import { format } from 'date-fns'

interface MessageBubbleProps {
  message: {
    id: string
    content: string
    sender: 'user' | 'sage'
    timestamp: Date
  }
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.sender === 'user'
  
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-xs lg:max-w-md px-4 py-3 rounded-lg shadow-sm ${
        isUser 
          ? 'bg-collaborative-primary text-white' 
          : 'bg-pastel-purple-100 text-collaborative-text border border-pastel-purple-200'
      }`}>
        <p className="text-sm leading-relaxed">{message.content}</p>
        <p className={`text-xs mt-1 ${
          isUser ? 'text-purple-100' : 'text-collaborative-text-light'
        }`}>
          {format(message.timestamp, 'h:mm a')}
        </p>
      </div>
    </div>
  )
}

export default MessageBubble 