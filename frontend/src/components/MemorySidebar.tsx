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
    if (intensity >= 0.7) return 'bg-pastel-peach-100 text-collaborative-error border border-pastel-peach-200'
    if (intensity >= 0.4) return 'bg-pastel-cream-100 text-collaborative-warning border border-pastel-cream-200'
    return 'bg-pastel-mint-100 text-collaborative-success border border-pastel-mint-200'
  }

  const getDepthColor = (depth: number) => {
    if (depth >= 3) return 'bg-pastel-purple-200 text-brand border border-pastel-purple-300'
    if (depth >= 2) return 'bg-pastel-lavender-100 text-collaborative-primary border border-pastel-lavender-200'
    return 'bg-pastel-purple-100 text-collaborative-text-light border border-pastel-purple-200'
  }

  const renderMoments = () => (
    <div className="space-y-4">
      {!memoryData?.sage?.moments || memoryData.sage.moments.length === 0 ? (
        <p className="text-collaborative-text-light text-sm">No moments recorded yet</p>
      ) : (
        memoryData.sage.moments.map((moment) => (
          <div key={moment.id} className="card-pastel p-3">
            <div className="flex justify-between items-start mb-2">
              <h5 className="heading-xs text-collaborative-text">
                {moment.context || 'Conversation moment'}
              </h5>
              <span className="text-xs text-collaborative-text-light">
                {formatDate(moment.timestamp)}
              </span>
            </div>
            
            <div className="text-xs text-collaborative-text-light">
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
        <p className="text-collaborative-text-light text-sm">No emotions identified yet</p>
      ) : (
        memoryData.sage.emotions.map((emotion) => (
          <div key={emotion.id} className="card-pastel p-3">
            <div className="flex justify-between items-center mb-2">
              <h5 className="heading-xs text-collaborative-text">{emotion.label}</h5>
              <span className={`px-2 py-1 rounded text-xs ${getIntensityColor(emotion.intensity)}`}>
                {Math.round(emotion.intensity * 100)}%
              </span>
            </div>
            
            {emotion.nuance && (
              <p className="text-xs text-collaborative-text-light mb-2">Nuance: {emotion.nuance}</p>
            )}
            
            {emotion.bodily_sensation && (
              <p className="text-xs text-collaborative-text-light">Physical: {emotion.bodily_sensation}</p>
            )}
          </div>
        ))
      )}
    </div>
  )

  const renderReflections = () => (
    <div className="space-y-4">
      {!memoryData?.sage?.reflections || memoryData.sage.reflections.length === 0 ? (
        <p className="text-collaborative-text-light text-sm">No reflections recorded yet</p>
      ) : (
        memoryData.sage.reflections.map((reflection) => (
          <div key={reflection.id} className="card-pastel p-3">
            <div className="flex justify-between items-start mb-2">
              <div className="flex items-center gap-2">
                <span className={`px-2 py-1 rounded text-xs ${getDepthColor(reflection.depth_level)}`}>
                  Depth {reflection.depth_level}
                </span>
                <span className="px-2 py-1 bg-pastel-lavender-100 text-collaborative-text rounded text-xs border border-pastel-lavender-200">
                  {reflection.insight_type}
                </span>
              </div>
              <span className="text-xs text-collaborative-text-light">
                {Math.round(reflection.confidence * 100)}% confidence
              </span>
            </div>
            
            <p className="text-sm text-collaborative-text mb-2 leading-relaxed">
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
        <p className="text-collaborative-text-light text-sm">No values identified yet</p>
      ) : (
        memoryData.sage.values.map((value) => (
          <div key={value.id} className="card-pastel p-3">
            <div className="flex justify-between items-start mb-2">
              <h5 className="heading-xs text-collaborative-text">{value.name}</h5>
              <span className="px-2 py-1 bg-pastel-mint-100 text-collaborative-success rounded text-xs border border-pastel-mint-200">
                {Math.round(value.importance * 100)}% important
              </span>
            </div>
            
            {value.description && (
              <p className="text-sm text-collaborative-text-light mb-2">{value.description}</p>
            )}
          </div>
        ))
      )}
    </div>
  )

  const renderPatterns = () => (
    <div className="space-y-4">
      {!memoryData?.sage?.patterns || memoryData.sage.patterns.length === 0 ? (
        <p className="text-collaborative-text-light text-sm">No patterns identified yet</p>
      ) : (
        memoryData.sage.patterns.map((pattern) => (
          <div key={pattern.id} className="card-pastel p-3">
            <div className="flex justify-between items-start mb-2">
              <h5 className="heading-xs text-collaborative-text">{pattern.pattern_type}</h5>
              <span className="px-2 py-1 bg-pastel-lavender-100 text-collaborative-text rounded text-xs border border-pastel-lavender-200">
                {pattern.frequency}
              </span>
            </div>
            
            <p className="text-sm text-collaborative-text-light mb-2">{pattern.description}</p>
          </div>
        ))
      )}
    </div>
  )

  const renderNotes = () => (
    <div className="space-y-4">
      {!memoryData?.sage?.notes || memoryData.sage.notes.length === 0 ? (
        <p className="text-collaborative-text-light text-sm">No therapeutic notes yet</p>
      ) : (
        memoryData.sage.notes.map((note) => (
          <div key={note.id} className="card-pastel p-3">
            <div className="flex justify-between items-start mb-2">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="px-2 py-1 bg-collaborative-primary text-white rounded text-xs">
                  {note.persona}
                </span>
                <span className="px-2 py-1 bg-pastel-purple-100 text-collaborative-text rounded text-xs border border-pastel-purple-200">
                  {note.note_type}
                </span>
              </div>
              <span className="text-xs text-collaborative-text-light whitespace-nowrap">
                {formatDate(note.created_at)}
              </span>
            </div>
            
            <p className="text-sm text-collaborative-text">{note.content}</p>
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
    <>
      {/* Mobile/Tablet Overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 xl:hidden"
          onClick={onClose}
        />
      )}
      
      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 right-0 
        w-full sm:w-80 xl:w-96 
        bg-collaborative-surface shadow-xl z-50 
        flex flex-col border-l border-pastel-purple-200
        transform transition-transform duration-300 ease-in-out
        ${isOpen ? 'translate-x-0' : 'translate-x-full'}
      `}>
        <div className="p-3 md:p-4 border-b border-pastel-purple-100 sidebar-gradient">
          <div className="flex items-center justify-between mb-4">
            <h2 className="heading-md text-collaborative-text">Memory</h2>
            <button
              onClick={onClose}
              className="text-collaborative-text-light hover:text-collaborative-text text-xl transition-colors p-1 hover:bg-pastel-purple-100 rounded-full"
            >
              ×
            </button>
          </div>
          
          {memoryData && (
            <div className="mb-4">
              <h3 className="heading-sm text-brand truncate">
                {memoryData.user_name || 'Anonymous'}
              </h3>
            </div>
          )}
          
          <div className="grid grid-cols-2 sm:grid-cols-3 xl:grid-cols-2 gap-1">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-2 py-2 rounded text-xs transition-colors text-center ${
                  activeTab === tab.id
                    ? 'bg-collaborative-primary text-white shadow-sm'
                    : 'bg-pastel-purple-100 text-collaborative-text hover:bg-pastel-purple-200 border border-pastel-purple-200'
                }`}
              >
                <div className="flex flex-col items-center space-y-1">
                  <span>{tab.icon}</span>
                  <span className="truncate">{tab.label}</span>
                </div>
              </button>
            ))}
          </div>
        </div>
        
        <div className="flex-1 p-3 md:p-4 overflow-y-auto bg-collaborative-background">
          {memoryData ? renderTabContent() : (
            <div className="text-center text-collaborative-text-light">
              <p>No memory data available</p>
            </div>
          )}
        </div>
      </div>
    </>
  )
}

export default MemorySidebar 