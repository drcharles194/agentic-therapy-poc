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
      <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
        isUser 
          ? 'bg-blue-600 text-white' 
          : 'bg-gray-200 text-gray-800'
      }`}>
        <p className="text-sm">{message.content}</p>
        <p className={`text-xs mt-1 ${
          isUser ? 'text-blue-100' : 'text-gray-500'
        }`}>
          {format(message.timestamp, 'h:mm a')}
        </p>
      </div>
    </div>
  )
}

export default MessageBubble 