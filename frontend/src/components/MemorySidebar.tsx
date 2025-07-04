import React from 'react'
import { type MemoryData } from '../utils/api'

interface MemorySidebarProps {
  memoryData?: MemoryData | null
  isOpen: boolean
  onClose: () => void
}

const MemorySidebar: React.FC<MemorySidebarProps> = ({ memoryData, isOpen, onClose }) => {
  if (!isOpen) return null

  return (
    <div className="fixed inset-y-0 right-0 w-80 bg-white shadow-xl z-50 overflow-y-auto">
      <div className="p-4">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-800">Memory</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            ×
          </button>
        </div>
        
        {memoryData ? (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-gray-700 mb-2">
                {memoryData.user_name}
              </h3>
              <p className="text-sm text-gray-500">ID: {memoryData.user_id}</p>
            </div>
            
            <div>
              <h4 className="font-medium text-gray-700 mb-2">Recent Reflections</h4>
              <div className="space-y-2">
                {memoryData.sage.reflections.slice(0, 3).map((reflection) => (
                  <div key={reflection.id} className="p-2 bg-gray-50 rounded text-sm">
                    <p className="text-gray-700">{reflection.content}</p>
                  </div>
                ))}
              </div>
            </div>
            
            <div>
              <h4 className="font-medium text-gray-700 mb-2">Emotions</h4>
              <div className="space-y-2">
                {memoryData.sage.emotions.map((emotion, index) => (
                  <div key={index} className="flex justify-between items-center">
                    <span className="text-sm text-gray-700">{emotion.label}</span>
                    <span className="text-sm text-gray-500">
                      {Math.round(emotion.intensity * 100)}%
                    </span>
                  </div>
                ))}
              </div>
            </div>
            
            <div>
              <h4 className="font-medium text-gray-700 mb-2">Self-Kindness</h4>
              <div className="space-y-2">
                {memoryData.sage.self_kindness_events.map((event, index) => (
                  <div key={index} className="p-2 bg-green-50 rounded text-sm">
                    <p className="text-gray-700">{event.description}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center text-gray-500">
            <p>No memory data available</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default MemorySidebar 