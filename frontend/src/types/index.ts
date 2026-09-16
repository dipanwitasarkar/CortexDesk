export interface Chat {
  id: number
  user_id: number
  title: string
  status: string
  context?: Record<string, any>
  metadata?: Record<string, any>
  created_at: string
  updated_at: string
}

export interface Message {
  id: number
  chat_id: number
  role: 'user' | 'assistant' | 'system'
  content: string
  agent_used?: string
  tool_calls?: any[]
  metadata?: Record<string, any>
  created_at: string
}

export interface AssistantRequest {
  message: string
  user_id: number
  chat_id?: number
  context?: Record<string, any>
  stream?: boolean
}

export interface AssistantResponse {
  response: string
  agents_used: string[]
  agent_results?: any[]
  execution_plan?: Record<string, any>
  chat_id: number
  message_id: number
}
