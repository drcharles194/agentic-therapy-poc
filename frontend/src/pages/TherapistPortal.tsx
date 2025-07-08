import React, { useState, useEffect } from 'react'
import { 
  apiClient, 
  type User, 
  type TherapistQueryResponse, 
  type GraphRAGComparisonResponse,
  type GraphRAGComparisonResult 
} from '../utils/api'

interface AnalysisResult extends TherapistQueryResponse {
  id: string
  isExpanded: boolean
}

interface ComparisonResult extends GraphRAGComparisonResponse {
  id: string
  isExpanded: boolean
}

type ResultType = AnalysisResult | ComparisonResult

interface ParsedSection {
  title: string
  content: string
  metadata?: string
}

const TherapistPortal: React.FC = () => {
  const [allUsers, setAllUsers] = useState<User[]>([])
  const [selectedUser, setSelectedUser] = useState<User | null>(null)
  const [showUserDropdown, setShowUserDropdown] = useState(false)
  const [query, setQuery] = useState('')
  const [analysisResults, setAnalysisResults] = useState<ResultType[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [comparisonMode, setComparisonMode] = useState(false)

  // Load users on component mount
  useEffect(() => {
    loadUsers()
  }, [])

  // Type guard functions
  const isAnalysisResult = (result: ResultType): result is AnalysisResult => {
    return 'response' in result && 'confidence' in result && 'data_sources' in result
  }

  const isComparisonResult = (result: ResultType): result is ComparisonResult => {
    return 'custom_result' in result && 'official_result' in result
  }

  const loadUsers = async () => {
    try {
      const usersResponse = await apiClient.getAllUsers()
      setAllUsers(usersResponse.users)
      
      // Auto-select first user if available
      if (usersResponse.users.length > 0) {
        setSelectedUser(usersResponse.users[0])
      }
    } catch (error) {
      console.error('Error loading users:', error)
      setError('Failed to load users. Please refresh the page.')
    }
  }

  const handleUserSelect = (userId: string) => {
    const user = allUsers.find(u => u.user_id === userId)
    if (user) {
      setSelectedUser(user)
      setShowUserDropdown(false)
      setAnalysisResults([]) // Clear previous results when switching users
    }
  }

  const handleQuery = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim() || !selectedUser || isLoading) return

    setIsLoading(true)
    setError(null)

    try {
      if (comparisonMode) {
        // Use comparison endpoint
        const result = await apiClient.compareGraphRAG(selectedUser.user_id, {
          query: query.trim()
        })
        
        const newComparisonResult: ComparisonResult = {
          ...result,
          id: `comparison_${Date.now()}`,
          isExpanded: true
        }
        
        setAnalysisResults(prevResults => [newComparisonResult, ...prevResults])
      } else {
        // Use regular GraphRAG endpoint
        const result = await apiClient.queryUserData(selectedUser.user_id, {
          query: query.trim()
        })
        
        const newAnalysisResult: AnalysisResult = {
          ...result,
          id: `analysis_${Date.now()}`,
          isExpanded: true
        }
        
        setAnalysisResults(prevResults => [newAnalysisResult, ...prevResults])
      }
      
      setQuery('') // Clear the query input after successful submission
      
    } catch (error: any) {
      console.error('Error processing GraphRAG query:', error)
      const errorMessage = error.response?.data?.detail || 'Failed to process query. Please try again.'
      setError(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  const toggleAnalysisExpansion = (id: string) => {
    setAnalysisResults(prevResults =>
      prevResults.map(result =>
        result.id === id ? { ...result, isExpanded: !result.isExpanded } : result
      )
    )
  }

  const removeAnalysisResult = (id: string) => {
    setAnalysisResults(prevResults => prevResults.filter(result => result.id !== id))
  }

  const clearAllResults = () => {
    setAnalysisResults([])
  }

  const parseStructuredResponse = (response: string): ParsedSection[] => {
    const sections: ParsedSection[] = []
    
    // Check if this is a new unified response (no markdown headers)
    if (!response.includes('##') && !response.includes('###')) {
      // Handle unified response format - look for "Analysis Summary:" footer
      const analysisMatch = response.match(/^(.*?)\n\nAnalysis Summary:(.*)$/s)
      
      if (analysisMatch) {
        // Main content and metadata footer
        const mainContent = analysisMatch[1].trim()
        const footer = `Analysis Summary:${analysisMatch[2].trim()}`
        
        sections.push({
          title: 'Therapeutic Analysis',
          content: cleanMarkdownForDisplay(mainContent)
        })
        
        sections.push({
          title: 'Analysis Details',
          content: cleanMarkdownForDisplay(footer)
        })
      } else {
        // Single unified response without footer
        sections.push({
          title: 'Analysis Results',
          content: cleanMarkdownForDisplay(response.trim())
        })
      }
      
      return sections
    }
    
    // Legacy parsing for structured responses with markdown headers
    const lines = response.split('\n')
    let currentSection: ParsedSection | null = null
    let currentContent: string[] = []
    
    for (const line of lines) {
      // Check for section headers (## or ###)
      if (line.startsWith('## ') || line.startsWith('### ')) {
        // Save previous section if exists
        if (currentSection) {
          currentSection.content = cleanMarkdownForDisplay(currentContent.join('\n').trim())
          sections.push(currentSection)
        }
        
        // Start new section
        const title = line.replace(/^#{2,3}\s*/, '').replace(/\*\*/g, '')
        currentSection = { title, content: '' }
        currentContent = []
      } else if (line.startsWith('*Based on ') && line.includes('entries*')) {
        // Extract metadata
        if (currentSection) {
          currentSection.metadata = line.replace(/^\*|\*$/g, '')
        }
      } else if (line.trim() && currentSection) {
        // Add content to current section
        currentContent.push(line)
      }
    }
    
    // Save final section
    if (currentSection) {
      currentSection.content = cleanMarkdownForDisplay(currentContent.join('\n').trim())
      sections.push(currentSection)
    }
    
    return sections.filter(section => section.content.trim())
  }

  const cleanMarkdownForDisplay = (text: string): string => {
    return text
      // Remove markdown headers
      .replace(/^#{1,6}\s+/gm, '')
      // Convert **bold** to just the text (since we'll style it differently)
      .replace(/\*\*(.*?)\*\*/g, '$1')
      // Convert *italic* to just the text
      .replace(/\*(.*?)\*/g, '$1')
      // Clean up bullet points
      .replace(/^[-*+]\s+/gm, '• ')
      // Clean up numbered lists
      .replace(/^\d+\.\s+/gm, '• ')
      // Remove extra line breaks
      .replace(/\n{3,}/g, '\n\n')
      .trim()
  }

  const formatConfidence = (confidence: number): string => {
    const percentage = Math.round(confidence * 100)
    if (percentage >= 80) return `${percentage}% (High)`
    if (percentage >= 60) return `${percentage}% (Medium)`
    return `${percentage}% (Low)`
  }

  const getConfidenceColor = (confidence: number): string => {
    if (confidence >= 0.8) return 'text-collaborative-success'
    if (confidence >= 0.6) return 'text-collaborative-text'
    return 'text-collaborative-error'
  }

  return (
    <div className="min-h-screen bg-collaborative-background">
      {/* Main Content */}
      <div className="w-full max-w-5xl xl:max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <header className="bg-collaborative-surface shadow-sm border-b border-pastel-purple-100 p-3 md:p-4 rounded-t-lg">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex flex-col sm:flex-row items-start sm:items-center space-y-2 sm:space-y-0 sm:space-x-4">
              {/* Logo */}
              <div className="flex items-center">
                <img 
                  src="/assets/collaborative-logo.png" 
                  alt="Collaborative Solutions" 
                  className="h-8 md:h-10 w-auto"
                />
              </div>
              
              {/* Therapist Portal Title */}
              <div className="flex items-center space-x-2">
                <span className="text-collaborative-primary font-semibold text-sm md:text-base">Therapist Portal</span>
                <span className="text-xs bg-pastel-mint-100 text-collaborative-text px-2 py-1 rounded-full whitespace-nowrap">
                  GraphRAG Powered
                </span>
              </div>
            </div>

            <div className="flex items-center space-x-2 w-full sm:w-auto">
              {/* User Selection Dropdown */}
              <div className="relative w-full sm:w-auto">
                <button
                  onClick={() => setShowUserDropdown(!showUserDropdown)}
                  className="button-secondary text-xs font-medium w-full sm:w-auto sm:min-w-44 truncate px-2 sm:px-3 py-2"
                  disabled={allUsers.length === 0}
                >
                  {selectedUser ? (
                    <span className="truncate">
                      <span className="hidden sm:inline">{selectedUser.name} ({selectedUser.moment_count} sessions)</span>
                      <span className="sm:hidden">{selectedUser.name}</span>
                    </span>
                  ) : (
                    'Select User'
                  )}
                </button>
                
                {showUserDropdown && (
                  <div className="absolute right-0 mt-2 w-full sm:w-64 card-pastel shadow-lg z-10">
                    <div className="p-2">
                      <div className="text-xs text-collaborative-text-light p-2 border-b border-pastel-purple-100 mb-2">
                        Select a user to query their data
                      </div>
                      
                      {allUsers.length > 0 ? (
                        allUsers.map(user => (
                          <button
                            key={user.user_id}
                            onClick={() => handleUserSelect(user.user_id)}
                            className={`w-full text-left px-3 py-2 text-sm rounded transition-colors hover:bg-pastel-purple-50 ${
                              selectedUser?.user_id === user.user_id 
                                ? 'bg-pastel-purple-100 text-brand border border-pastel-purple-200' 
                                : 'text-collaborative-text'
                            }`}
                          >
                            <div className="font-medium truncate">{user.name}</div>
                            <div className="text-xs text-collaborative-text-light truncate">
                              {user.moment_count} sessions • Last active: {new Date(user.last_active).toLocaleDateString()}
                            </div>
                          </button>
                        ))
                      ) : (
                        <div className="text-xs text-collaborative-text-light p-2 text-center">
                          No users found
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
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

        {/* Main Content */}
        <div className="flex-1 flex flex-col mt-4 space-y-4">
          {/* Instructions */}
          <div className="card-pastel p-4 md:p-6">
            <h2 className="heading-md text-collaborative-text mb-3">
              Query User Data with GraphRAG
            </h2>
            <p className="text-collaborative-text-light mb-4 text-sm md:text-base">
              Ask intelligent questions about your selected user's therapy sessions, emotional patterns, 
              reflections, and progress. The system will search through their conversation history and 
              stored memories to provide comprehensive insights with confidence scoring.
            </p>
            {selectedUser && (
              <div className="bg-pastel-purple-50 p-3 rounded border border-pastel-purple-200">
                <div className="text-sm flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-2">
                  <span className="font-medium text-collaborative-text">Currently selected:</span>
                  <span className="text-brand font-medium">{selectedUser.name}</span>
                  <span className="text-collaborative-text-light">
                    • {selectedUser.moment_count} conversation sessions
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Query Interface */}
          <div className="card-pastel p-4 md:p-6">
            <form onSubmit={handleQuery} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-collaborative-text mb-2">
                  Ask a question about {selectedUser?.name || 'the selected user'}:
                </label>
                <textarea
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder={selectedUser 
                    ? `What patterns do you see in ${selectedUser.name}'s emotional expressions?`
                    : "Please select a user first..."
                  }
                  disabled={!selectedUser || isLoading}
                  rows={3}
                  className="w-full p-3 input-pastel disabled:opacity-50 disabled:cursor-not-allowed resize-none text-sm md:text-base"
                />
              </div>
              
              {/* Comparison Mode Toggle */}
              <div className="flex items-center space-x-3 p-3 bg-pastel-purple-50 rounded border border-pastel-purple-200">
                <input
                  type="checkbox"
                  id="comparisonMode"
                  checked={comparisonMode}
                  onChange={(e) => setComparisonMode(e.target.checked)}
                  className="rounded"
                />
                <label htmlFor="comparisonMode" className="text-sm text-collaborative-text">
                  <span className="font-medium">Comparison Mode</span>
                  <span className="text-collaborative-text-light block text-xs">
                    Run both Custom and Official Neo4j GraphRAG implementations side-by-side
                  </span>
                </label>
              </div>
              
              <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 sm:gap-4">
                <button
                  type="submit"
                  disabled={!selectedUser || !query.trim() || isLoading}
                  className="button-primary disabled:opacity-50 disabled:cursor-not-allowed w-full sm:w-auto"
                >
                  {isLoading 
                    ? (comparisonMode ? 'Running Comparison...' : 'Analyzing Data...') 
                    : (comparisonMode ? 'Compare GraphRAG' : 'Query User Data')
                  }
                </button>
                
                {analysisResults.length > 0 && (
                  <button
                    type="button"
                    onClick={clearAllResults}
                    className="button-secondary text-sm w-full sm:w-auto"
                  >
                    Clear All Results ({analysisResults.length})
                  </button>
                )}
              </div>
            </form>
          </div>

          {/* Loading indicator */}
          {isLoading && (
            <div className="flex justify-center">
              <div className="bg-pastel-purple-100 text-collaborative-text px-4 py-3 rounded-lg border border-pastel-purple-200">
                <div className="flex items-center space-x-3">
                  <div className="animate-pulse-soft rounded-full h-4 w-4 bg-collaborative-primary"></div>
                  <span className="text-sm font-medium">Processing GraphRAG query...</span>
                </div>
              </div>
            </div>
          )}

          {/* Analysis Results Accordion */}
          {analysisResults.length > 0 && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="heading-md text-collaborative-text">Analysis History</h3>
                <span className="text-xs text-collaborative-text-light">
                  {analysisResults.length} analysis {analysisResults.length === 1 ? 'result' : 'results'}
                </span>
              </div>
              
              {analysisResults.map((result) => {
                // Handle different result types
                if (isComparisonResult(result)) {
                  // Render comparison result
                  return (
                    <div key={result.id} className="card-pastel border border-pastel-purple-200">
                      {/* Comparison Accordion Header */}
                      <div className="p-4 border-b border-pastel-purple-100">
                        <div className="flex items-start justify-between">
                          <button
                            onClick={() => toggleAnalysisExpansion(result.id)}
                            className="flex-1 text-left"
                          >
                            <div className="flex items-center space-x-2">
                              <span className={`transform transition-transform duration-200 ${result.isExpanded ? 'rotate-90' : ''}`}>
                                ▶
                              </span>
                              <div className="flex-1">
                                <div className="text-sm font-medium text-collaborative-text truncate">
                                  "📊 COMPARISON: {result.query}"
                                </div>
                                <div className="flex flex-wrap items-center gap-2 mt-1 text-xs">
                                  <span className="text-collaborative-text-light bg-pastel-mint-100 px-2 py-1 rounded">
                                    {result.total_processing_time_ms.toFixed(0)}ms total
                                  </span>
                                  <span className="text-collaborative-text-light">
                                    {new Date(result.timestamp).toLocaleString()}
                                  </span>
                                </div>
                              </div>
                            </div>
                          </button>
                          
                          <button
                            onClick={() => removeAnalysisResult(result.id)}
                            className="ml-2 text-collaborative-text-light hover:text-collaborative-error transition-colors"
                            title="Remove this comparison"
                          >
                            ×
                          </button>
                        </div>
                      </div>
                      
                      {/* Comparison Content */}
                      {result.isExpanded && (
                        <div className="p-4 space-y-4">
                          {/* Query Summary */}
                          <div className="bg-pastel-purple-50 p-3 rounded border border-pastel-purple-200">
                            <div className="text-sm space-y-1">
                              <div className="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-2">
                                <span className="font-medium text-collaborative-text flex-shrink-0">User:</span>
                                <span className="text-brand font-medium">{result.user_name}</span>
                              </div>
                            </div>
                          </div>
                          
                          {/* Side-by-side comparison */}
                          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                            {/* Custom Implementation */}
                            <div className="bg-collaborative-background p-4 rounded border border-pastel-purple-100">
                              <div className="flex items-center justify-between mb-2">
                                <h4 className="text-sm font-medium text-collaborative-text">
                                  {result.custom_result.implementation}
                                </h4>
                                <div className="flex items-center gap-2">
                                  <span className={`text-xs font-medium ${getConfidenceColor(result.custom_result.confidence)}`}>
                                    {formatConfidence(result.custom_result.confidence)}
                                  </span>
                                  <span className="text-xs text-collaborative-text-light">
                                    {result.custom_result.processing_time_ms.toFixed(0)}ms
                                  </span>
                                </div>
                              </div>
                              
                              {result.custom_result.error ? (
                                <div className="text-sm text-collaborative-error bg-pastel-peach-50 p-2 rounded">
                                  Error: {result.custom_result.error}
                                </div>
                              ) : (
                                <div className="text-sm text-collaborative-text whitespace-pre-wrap leading-relaxed">
                                  {result.custom_result.response}
                                </div>
                              )}
                              
                              {/* Custom Data Sources */}
                              {result.custom_result.data_sources && result.custom_result.data_sources.length > 0 && (
                                <div className="mt-3 pt-3 border-t border-pastel-purple-100">
                                  <div className="text-xs text-collaborative-text-light mb-1">Data Sources:</div>
                                  <div className="flex flex-wrap gap-1">
                                    {result.custom_result.data_sources.map((source, index) => (
                                      <span
                                        key={index}
                                        className="text-xs bg-pastel-mint-100 text-collaborative-text px-2 py-1 rounded-full"
                                      >
                                        {source}
                                      </span>
                                    ))}
                                  </div>
                                </div>
                              )}
                            </div>
                            
                            {/* Official Implementation */}
                            <div className="bg-collaborative-background p-4 rounded border border-pastel-purple-100">
                              <div className="flex items-center justify-between mb-2">
                                <h4 className="text-sm font-medium text-collaborative-text">
                                  {result.official_result.implementation}
                                </h4>
                                <div className="flex items-center gap-2">
                                  <span className={`text-xs font-medium ${getConfidenceColor(result.official_result.confidence)}`}>
                                    {formatConfidence(result.official_result.confidence)}
                                  </span>
                                  <span className="text-xs text-collaborative-text-light">
                                    {result.official_result.processing_time_ms.toFixed(0)}ms
                                  </span>
                                </div>
                              </div>
                              
                              {result.official_result.error ? (
                                <div className="text-sm text-collaborative-error bg-pastel-peach-50 p-2 rounded">
                                  Error: {result.official_result.error}
                                </div>
                              ) : (
                                <div className="text-sm text-collaborative-text whitespace-pre-wrap leading-relaxed">
                                  {result.official_result.response}
                                </div>
                              )}
                              
                              {/* Official Data Sources */}
                              {result.official_result.data_sources && result.official_result.data_sources.length > 0 && (
                                <div className="mt-3 pt-3 border-t border-pastel-purple-100">
                                  <div className="text-xs text-collaborative-text-light mb-1">Data Sources:</div>
                                  <div className="flex flex-wrap gap-1">
                                    {result.official_result.data_sources.map((source, index) => (
                                      <span
                                        key={index}
                                        className="text-xs bg-pastel-mint-100 text-collaborative-text px-2 py-1 rounded-full"
                                      >
                                        {source}
                                      </span>
                                    ))}
                                  </div>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  )
                } else if (isAnalysisResult(result)) {
                  // Render regular analysis result
                  const parsedSections = parseStructuredResponse(result.response)
                  
                  return (
                    <div key={result.id} className="card-pastel border border-pastel-purple-200">
                      {/* Regular Accordion Header */}
                      <div className="p-4 border-b border-pastel-purple-100">
                        <div className="flex items-start justify-between">
                          <button
                            onClick={() => toggleAnalysisExpansion(result.id)}
                            className="flex-1 text-left"
                          >
                            <div className="flex items-center space-x-2">
                              <span className={`transform transition-transform duration-200 ${result.isExpanded ? 'rotate-90' : ''}`}>
                                ▶
                              </span>
                              <div className="flex-1">
                                <div className="text-sm font-medium text-collaborative-text truncate">
                                  "{result.query}"
                                </div>
                                <div className="flex flex-wrap items-center gap-2 mt-1 text-xs">
                                  <span className={`font-medium ${getConfidenceColor(result.confidence)}`}>
                                    {formatConfidence(result.confidence)}
                                  </span>
                                  <span className="text-collaborative-text-light">
                                    {new Date(result.timestamp).toLocaleString()}
                                  </span>
                                  {result.data_sources && result.data_sources.length > 0 && (
                                    <span className="text-collaborative-text-light">
                                      • {result.data_sources.length} sources
                                    </span>
                                  )}
                                </div>
                              </div>
                            </div>
                          </button>
                          
                          <button
                            onClick={() => removeAnalysisResult(result.id)}
                            className="ml-2 text-collaborative-text-light hover:text-collaborative-error transition-colors"
                            title="Remove this analysis"
                          >
                            ×
                          </button>
                        </div>
                      </div>
                      
                      {/* Regular Accordion Content */}
                      {result.isExpanded && (
                        <div className="p-4 space-y-4">
                          {/* Query Summary */}
                          <div className="bg-pastel-purple-50 p-3 rounded border border-pastel-purple-200">
                            <div className="text-sm space-y-1">
                              <div className="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-2">
                                <span className="font-medium text-collaborative-text flex-shrink-0">User:</span>
                                <span className="text-brand font-medium">{result.user_name}</span>
                              </div>
                            </div>
                          </div>
                          
                          {/* Structured Content */}
                          {parsedSections.length > 0 ? (
                            <div className="space-y-4">
                              {parsedSections.map((section, index) => (
                                <div key={index} className="bg-collaborative-background p-4 rounded border border-pastel-purple-100">
                                  <div className="flex items-center justify-between mb-2">
                                    <h4 className="text-sm font-medium text-collaborative-text">
                                      {section.title}
                                    </h4>
                                    {section.metadata && (
                                      <span className="text-xs text-collaborative-text-light italic">
                                        {section.metadata}
                                      </span>
                                    )}
                                  </div>
                                  <div className="text-sm text-collaborative-text whitespace-pre-wrap leading-relaxed">
                                    {section.content}
                                  </div>
                                </div>
                              ))}
                            </div>
                          ) : (
                            // Fallback for unstructured responses
                            <div className="bg-collaborative-background p-4 rounded border border-pastel-purple-100">
                              <div className="text-sm text-collaborative-text whitespace-pre-wrap leading-relaxed">
                                {result.response}
                              </div>
                            </div>
                          )}
                          
                          {/* Data Sources */}
                          {result.data_sources && result.data_sources.length > 0 && (
                            <div className="border-t border-pastel-purple-100 pt-4">
                              <h4 className="text-xs font-medium text-collaborative-text mb-2">Data Sources Used:</h4>
                              <div className="flex flex-wrap gap-2">
                                {result.data_sources.map((source, index) => (
                                  <span
                                    key={index}
                                    className="text-xs bg-pastel-mint-100 text-collaborative-text px-2 py-1 rounded-full"
                                  >
                                    {source}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )
                }
                
                return null // Should never reach here
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default TherapistPortal 