import { useState } from 'react'
import './App.css'
import ChatPage from './pages/ChatPage'
import TherapistPortal from './pages/TherapistPortal'
import { ViewMode } from './types/views'

function App() {
  const [currentView, setCurrentView] = useState<ViewMode>(ViewMode.USER)

  const switchView = () => {
    setCurrentView(currentView === ViewMode.USER ? ViewMode.THERAPIST : ViewMode.USER)
  }

  return (
    <div className="relative">
      {/* View Toggle Button */}
      <div className="fixed top-3 md:top-4 right-3 md:right-4 z-50">
        <button
          onClick={switchView}
          className="button-accent shadow-lg hover:shadow-xl transition-all duration-200 font-medium text-xs md:text-sm px-3 md:px-4 py-2"
        >
          <span className="hidden sm:inline">
            {currentView === ViewMode.USER ? '👨‍⚕️ Switch to Therapist View' : '👤 Switch to User View'}
          </span>
          <span className="sm:hidden">
            {currentView === ViewMode.USER ? '👨‍⚕️ Therapist' : '👤 User'}
          </span>
        </button>
      </div>

      {/* Main Content based on current view */}
      {currentView === ViewMode.USER ? <ChatPage /> : <TherapistPortal />}
    </div>
  )
}

export default App 