import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface ChatMessage {
  message: string
  user_id: string
}

export interface ChatResponse {
  persona_response: string
}

export interface MemoryData {
  user_id: string
  user_name: string
  sage: {
    moments: Array<{
      id: string
      timestamp: string
      context: string
      session_id: string
    }>
    emotions: Array<{
      id: string
      label: string
      intensity: number
      nuance?: string
      bodily_sensation?: string
    }>
    reflections: Array<{
      id: string
      content: string
      insight_type: string
      depth_level: number
      confidence: number
    }>
    values: Array<{
      id: string
      name: string
      description: string
      importance: number
    }>
    patterns: Array<{
      id: string
      description: string
      pattern_type: string
      frequency: string
    }>
    notes: Array<{
      id: string
      persona: string
      note_type: string
      content: string
      created_at: string
    }>
  }
}

export interface HealthResponse {
  status: string
  timestamp: string
  version: string
  services: {
    neo4j: string
    anthropic: string
  }
}

export const apiClient = {
  // Chat endpoint
  sendMessage: async (chatData: ChatMessage): Promise<ChatResponse> => {
    const response = await api.post<ChatResponse>('/chat/', chatData)
    return response.data
  },

  // Memory endpoint
  getMemory: async (userId: string): Promise<MemoryData> => {
    const response = await api.get<MemoryData>(`/memory/${userId}`)
    return response.data
  },

  // Health check endpoint
  healthCheck: async (): Promise<HealthResponse> => {
    const response = await api.post<HealthResponse>('/healthcheck')
    return response.data
  }
}

export default apiClient 