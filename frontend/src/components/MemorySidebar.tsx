import React, { useState } from 'react'
import { type MemoryData } from '../utils/api'

interface MemorySidebarProps {
  memoryData?: MemoryData | null
  isOpen: boolean
  onClose: () => void
}

const MemorySidebar: React.FC<MemorySidebarProps> = ({ memoryData, isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState<string>('moments')
  
  if (!isOpen) return null

  const tabs = [
    { id: 'moments', label: 'Moments', icon: '🕐' },
    { id: 'emotions', label: 'Emotions', icon: '💭' },
    { id: 'reflections', label: 'Reflections', icon: '🔍' },
    { id: 'values', label: 'Values', icon: '⭐' },
    { id: 'patterns', label: 'Patterns', icon: '🔄' },
    { id: 'notes', label: 'Notes', icon: '📝' }
  ]

  const formatDate = (timestamp: string) => {
    try {
      return new Date(timestamp).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    } catch {
      return 'Unknown'
    }
  }

  const getIntensityColor = (intensity: number) => {
    if (intensity >= 0.7) return 'bg-red-100 text-red-800'
    if (intensity >= 0.4) return 'bg-yellow-100 text-yellow-800'
    return 'bg-green-100 text-green-800'
  }

  const getDepthColor = (depth: number) => {
    if (depth >= 3) return 'bg-purple-100 text-purple-800'
    if (depth >= 2) return 'bg-blue-100 text-blue-800'
    return 'bg-gray-100 text-gray-800'
  }

  const renderMoments = () => (
    <div className="space-y-4">
      {!memoryData?.sage?.moments || memoryData.sage.moments.length === 0 ? (
        <p className="text-gray-500 text-sm">No moments recorded yet</p>
      ) : (
        memoryData.sage.moments.map((moment) => (
          <div key={moment.id} className="border rounded-lg p-3 bg-gray-50">
            <div className="flex justify-between items-start mb-2">
              <h5 className="font-medium text-gray-800">
                {moment.context || 'Conversation moment'}
              </h5>
              <span className="text-xs text-gray-500">
                {formatDate(moment.timestamp)}
              </span>
            </div>
            
            <div className="text-xs text-gray-600">
              Session: {moment.session_id}
            </div>
          </div>
        ))
      )}
    </div>
  )

  const renderEmotions = () => (
    <div className="space-y-4">
      {!memoryData?.sage?.emotions || memoryData.sage.emotions.length === 0 ? (
        <p className="text-gray-500 text-sm">No emotions identified yet</p>
      ) : (
        memoryData.sage.emotions.map((emotion) => (
          <div key={emotion.id} className="border rounded-lg p-3 bg-gray-50">
            <div className="flex justify-between items-center mb-2">
              <h5 className="font-medium text-gray-800">{emotion.label}</h5>
              <span className={`px-2 py-1 rounded text-xs ${getIntensityColor(emotion.intensity)}`}>
                {Math.round(emotion.intensity * 100)}%
              </span>
            </div>
            
            {emotion.nuance && (
              <p className="text-xs text-gray-600 mb-2">Nuance: {emotion.nuance}</p>
            )}
            
            {emotion.bodily_sensation && (
              <p className="text-xs text-gray-600">Physical: {emotion.bodily_sensation}</p>
            )}
          </div>
        ))
      )}
    </div>
  )

  const renderReflections = () => (
    <div className="space-y-4">
      {!memoryData?.sage?.reflections || memoryData.sage.reflections.length === 0 ? (
        <p className="text-gray-500 text-sm">No reflections recorded yet</p>
      ) : (
        memoryData.sage.reflections.map((reflection) => (
          <div key={reflection.id} className="border rounded-lg p-3 bg-gray-50">
            <div className="flex justify-between items-start mb-2">
              <div className="flex items-center gap-2">
                <span className={`px-2 py-1 rounded text-xs ${getDepthColor(reflection.depth_level)}`}>
                  Depth {reflection.depth_level}
                </span>
                <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">
                  {reflection.insight_type}
                </span>
              </div>
              <span className="text-xs text-gray-500">
                {Math.round(reflection.confidence * 100)}% confidence
              </span>
            </div>
            
            <p className="text-sm text-gray-700 mb-2">
              {reflection.content}
            </p>
          </div>
        ))
      )}
    </div>
  )

  const renderValues = () => (
    <div className="space-y-4">
      {!memoryData?.sage?.values || memoryData.sage.values.length === 0 ? (
        <p className="text-gray-500 text-sm">No values identified yet</p>
      ) : (
        memoryData.sage.values.map((value) => (
          <div key={value.id} className="border rounded-lg p-3 bg-gray-50">
            <div className="flex justify-between items-start mb-2">
              <h5 className="font-medium text-gray-800">{value.name}</h5>
              <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
                {Math.round(value.importance * 100)}% important
              </span>
            </div>
            
            {value.description && (
              <p className="text-sm text-gray-700 mb-2">{value.description}</p>
            )}
          </div>
        ))
      )}
    </div>
  )

  const renderPatterns = () => (
    <div className="space-y-4">
      {!memoryData?.sage?.patterns || memoryData.sage.patterns.length === 0 ? (
        <p className="text-gray-500 text-sm">No patterns identified yet</p>
      ) : (
        memoryData.sage.patterns.map((pattern) => (
          <div key={pattern.id} className="border rounded-lg p-3 bg-gray-50">
            <div className="flex justify-between items-start mb-2">
              <h5 className="font-medium text-gray-800">{pattern.pattern_type}</h5>
              <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">
                {pattern.frequency}
              </span>
            </div>
            
            <p className="text-sm text-gray-700 mb-2">{pattern.description}</p>
          </div>
        ))
      )}
    </div>
  )

  const renderNotes = () => (
    <div className="space-y-4">
      {!memoryData?.sage?.notes || memoryData.sage.notes.length === 0 ? (
        <p className="text-gray-500 text-sm">No therapeutic notes yet</p>
      ) : (
        memoryData.sage.notes.map((note) => (
          <div key={note.id} className="border rounded-lg p-3 bg-gray-50">
            <div className="flex justify-between items-start mb-2">
              <div className="flex items-center gap-2">
                <span className="px-2 py-1 bg-indigo-100 text-indigo-800 rounded text-xs">
                  {note.persona}
                </span>
                <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">
                  {note.note_type}
                </span>
              </div>
              <span className="text-xs text-gray-500">
                {formatDate(note.created_at)}
              </span>
            </div>
            
            <p className="text-sm text-gray-700">{note.content}</p>
          </div>
        ))
      )}
    </div>
  )

  const renderTabContent = () => {
    switch (activeTab) {
      case 'moments': return renderMoments()
      case 'emotions': return renderEmotions()
      case 'reflections': return renderReflections()
      case 'values': return renderValues()
      case 'patterns': return renderPatterns()
      case 'notes': return renderNotes()
      default: return null
    }
  }

  return (
    <div className="fixed inset-y-0 right-0 w-96 bg-white shadow-xl z-50 flex flex-col">
      <div className="p-4 border-b">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-800">Memory</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-xl"
          >
            ×
          </button>
        </div>
        
        {memoryData && (
          <div className="mb-4">
            <h3 className="text-lg font-medium text-gray-700">
              {memoryData.user_name || 'Anonymous'}
            </h3>
            <p className="text-sm text-gray-500">ID: {memoryData.user_id}</p>
          </div>
        )}
        
        <div className="flex flex-wrap gap-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-3 py-1 rounded text-sm transition-colors ${
                activeTab === tab.id
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {tab.icon} {tab.label}
            </button>
          ))}
        </div>
      </div>
      
      <div className="flex-1 p-4 overflow-y-auto">
        {memoryData ? renderTabContent() : (
          <div className="text-center text-gray-500">
            <p>No memory data available</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default MemorySidebar 