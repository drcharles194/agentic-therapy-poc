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
    <div className="card-pastel p-6 mb-6">
      <div className="flex items-center mb-4">
        <div className="w-12 h-12 bg-pastel-purple-100 rounded-full flex items-center justify-center border-2 border-pastel-purple-200">
          <span className="text-brand font-semibold text-lg">
            {persona.name.charAt(0)}
          </span>
        </div>
        <div className="ml-4">
          <h3 className="heading-md text-collaborative-text">
            {persona.name}
          </h3>
          <p className="text-sm text-collaborative-text-light font-medium">{persona.role}</p>
        </div>
      </div>
      <p className="text-collaborative-text leading-relaxed">{persona.description}</p>
    </div>
  )
}

export default PersonaPanel 