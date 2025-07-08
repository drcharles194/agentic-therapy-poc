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
  user_name?: string
  sage: {
    moments: Array<any>
    emotions: Array<any>
    reflections: Array<any>
    values: Array<any>
    patterns: Array<any>
    notes: Array<any>
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

export interface User {
  user_id: string
  name: string
  created_at: string
  last_active: string
  moment_count: number
}

export interface CreateUserRequest {
  name?: string
}

export interface UpdateUserRequest {
  name: string
}

export interface TherapistQueryRequest {
  query: string
  context?: Record<string, any>
}

export interface TherapistQueryResponse {
  query: string
  user_id: string
  user_name: string
  response: string
  confidence: number
  data_sources: string[]
  timestamp: string
}

export interface GraphRAGComparisonResult {
  implementation: string
  response: string
  confidence: number
  data_sources: string[]
  processing_time_ms: number
  indexes_used: string[]
  retrieval_method: string
  error?: string
}

export interface GraphRAGComparisonResponse {
  query: string
  user_id: string
  user_name: string
  custom_result: GraphRAGComparisonResult
  official_result: GraphRAGComparisonResult
  total_processing_time_ms: number
  timestamp: string
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
  },

  // User Management API Methods
  createUser: async (request: CreateUserRequest = {}): Promise<User> => {
    const response = await api.post<User>('/users/', request)
    return response.data
  },

  getAllUsers: async (): Promise<{ users: User[] }> => {
    const response = await api.get<{ users: User[] }>('/users/')
    return response.data
  },

  getUser: async (userId: string): Promise<User> => {
    const response = await api.get<User>(`/users/${userId}`)
    return response.data
  },

  updateUser: async (userId: string, request: UpdateUserRequest): Promise<User> => {
    const response = await api.put<User>(`/users/${userId}`, request)
    return response.data
  },

  // Therapist GraphRAG Query API Method
  queryUserData: async (userId: string, request: TherapistQueryRequest): Promise<TherapistQueryResponse> => {
    const response = await api.post<TherapistQueryResponse>(`/users/${userId}/query`, request)
    return response.data
  },

  // GraphRAG Comparison API Method
  compareGraphRAG: async (userId: string, request: TherapistQueryRequest): Promise<GraphRAGComparisonResponse> => {
    const response = await api.post<GraphRAGComparisonResponse>(`/users/${userId}/query/compare`, request)
    return response.data
  }
}

export default apiClient 