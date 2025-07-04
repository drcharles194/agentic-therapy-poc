import React from 'react'

interface PersonaPanelProps {
  persona: {
    name: string
    role: string
    description: string
    avatar?: string
  }
}

const PersonaPanel: React.FC<PersonaPanelProps> = ({ persona }) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <div className="flex items-center mb-4">
        <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
          <span className="text-blue-600 font-semibold text-lg">
            {persona.name.charAt(0)}
          </span>
        </div>
        <div className="ml-4">
          <h3 className="text-xl font-semibold text-gray-800">
            {persona.name}
          </h3>
          <p className="text-sm text-gray-600">{persona.role}</p>
        </div>
      </div>
      <p className="text-gray-700">{persona.description}</p>
    </div>
  )
}

export default PersonaPanel 