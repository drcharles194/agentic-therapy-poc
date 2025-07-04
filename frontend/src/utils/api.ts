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
    reflections: Array<{
      id: string
      content: string
      timestamp: string
    }>
    emotions: Array<{
      label: string
      intensity: number
      timestamp: string
    }>
    self_kindness_events: Array<{
      description: string
      timestamp: string
    }>
    contradictions: Array<{
      summary: string
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