import React, { useState, useRef, useEffect, useCallback } from 'react'
import { Message } from '../types'
import { Send, Loader2 } from 'lucide-react'
import { useToast } from './ToastContainer'
import { API_BASE_URL } from '../config'

interface ChatInterfaceProps {
  chat: any
  onNewChat: () => void
  onChatUpdated?: () => void
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ chat, onNewChat, onChatUpdated }) => {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const { success, error } = useToast()

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const loadMessages = useCallback(async () => {
    if (!chat) return;
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/chats/${chat.id}`)
      if (response.ok) {
        const data = await response.json()
        setMessages(data.messages || [])
      } else {
        error('Failed to load messages')
      }
    } catch (err) {
      console.error('Failed to load messages:', err)
      error('Failed to load messages')
    }
  }, [chat?.id])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    loadMessages()
  }, [loadMessages])

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now(),
      chat_id: chat?.id || 0,
      role: 'user',
      content: input,
      created_at: new Date().toISOString()
    }

    setMessages([...messages, userMessage])
    setInput('')
    setIsLoading(true)
    setIsTyping(true)

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/assistant`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: input,
          user_id: 1,
          chat_id: chat?.id
        })
      })
      
      if (response.ok) {
        const data = await response.json()
        const assistantMessage: Message = {
          id: Date.now() + 1,
          chat_id: chat?.id || 0,
          role: 'assistant',
          content: data.response || data.message || 'No response',
          agent_used: data.agent_used || 'supervisor',
          created_at: new Date().toISOString()
        }
        
        setMessages(prev => [...prev, assistantMessage])
        
        // Notify parent that chat was updated (title may have changed)
        if (onChatUpdated) {
          onChatUpdated()
        }
      } else {
        const errorData = await response.json()
        error(errorData.detail || 'Failed to get response')
        setMessages(prev => prev.slice(0, -1)) // Remove user message on failure
      }
    } catch (err) {
      console.error('Failed to send message:', err)
      error('Failed to send message')
      setMessages(prev => prev.slice(0, -1)) // Remove user message on failure
    } finally {
      setIsLoading(false)
      setIsTyping(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  if (!chat) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-semibold mb-4">Welcome to CortexDesk</h2>
          <p className="text-gray-400 mb-6">Start a new conversation to get started</p>
          <button
            onClick={onNewChat}
            className="btn-primary"
          >
            New Chat
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-gray-400 mt-20">
            <p>Start a conversation with your AI assistant</p>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[70%] rounded-lg p-3 ${
                    message.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-800 text-gray-100 border border-gray-700'
                  }`}
                >
                  <div className="text-sm">{message.content}</div>
                  {message.agent_used && (
                    <div className="text-xs mt-1 opacity-70">
                      Agent: {message.agent_used}
                    </div>
                  )}
                </div>
              </div>
            ))}
            {isTyping && (
              <div className="flex justify-start">
                <div className="bg-gray-800 text-gray-100 border border-gray-700 rounded-lg p-3">
                  <div className="flex items-center gap-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                  </div>
                </div>
              </div>
            )}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-700 p-4">
        <div className="flex gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            className="flex-1 input-field resize-none"
            rows={1}
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            className="btn-primary flex items-center gap-2"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
            Send
          </button>
        </div>
      </div>
    </div>
  )
}

export default ChatInterface
