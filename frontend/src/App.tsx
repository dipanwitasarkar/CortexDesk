import React, { useState, useEffect } from 'react'
import ChatInterface from './components/ChatInterface'
import Sidebar from './components/Sidebar'
import ObservabilityDashboard from './components/ObservabilityDashboard'
import DocumentManager from './components/DocumentManager'
import { Chat } from './types'
import { Activity, MessageSquare, Info, X, Bot, Code, Shield, Cpu, FileText } from 'lucide-react'

function App() {
  const [chats, setChats] = useState<Chat[]>([])
  const [currentChat, setCurrentChat] = useState<Chat | null>(null)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [showDashboard, setShowDashboard] = useState(false)
  const [showAbout, setShowAbout] = useState(false)
  const [showDocuments, setShowDocuments] = useState(false)

  useEffect(() => {
    // Load chats from API
    loadChats()
  }, [])

  const loadChats = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/chats?user_id=1')
      if (response.ok) {
        const data = await response.json()
        setChats(data)
      }
    } catch (error) {
      console.error('Failed to load chats:', error)
    }
  }

  const createNewChat = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/chats', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: 1, title: 'New conversation' })
      })
      if (response.ok) {
        const newChat = await response.json()
        setChats([newChat, ...chats])
        setCurrentChat(newChat)
      }
    } catch (error) {
      console.error('Failed to create chat:', error)
    }
  }

  const deleteChat = async (chatId: number) => {
    try {
      // Remove from local state
      setChats(chats.filter(chat => chat.id !== chatId))
      
      // If the deleted chat was current, clear it
      if (currentChat?.id === chatId) {
        setCurrentChat(null)
      }
    } catch (error) {
      console.error('Failed to delete chat:', error)
    }
  }

  const handleChatUpdated = () => {
    // Reload chats to get updated titles
    loadChats()
  }

  return (
    <div className="flex h-screen bg-gray-900">
      {/* Sidebar */}
      {sidebarOpen && (
        <Sidebar
          chats={chats}
          currentChat={currentChat}
          onSelectChat={setCurrentChat}
          onNewChat={createNewChat}
          onClose={() => setSidebarOpen(false)}
          onDeleteChat={deleteChat}
        />
      )}

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-gray-800 border-b border-gray-700 p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              {!sidebarOpen && (
                <button
                  onClick={() => setSidebarOpen(true)}
                  className="text-gray-400 hover:text-white"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                  </svg>
                </button>
              )}
              <h1 className="text-xl font-semibold">Windows AI Assistant</h1>
            </div>
            <div className="flex items-center gap-4">
              <button
                onClick={() => setShowDocuments(true)}
                className="flex items-center gap-2 px-3 py-2 rounded-lg bg-gray-700 text-gray-300 hover:bg-gray-600 transition-colors"
                title="Documents"
              >
                <FileText className="w-4 h-4" />
                <span className="text-sm">Documents</span>
              </button>
              <button
                onClick={() => setShowAbout(true)}
                className="flex items-center gap-2 px-3 py-2 rounded-lg bg-gray-700 text-gray-300 hover:bg-gray-600 transition-colors"
                title="About"
              >
                <Info className="w-4 h-4" />
                <span className="text-sm">About</span>
              </button>
              <button
                onClick={() => setShowDashboard(!showDashboard)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                  showDashboard
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                {showDashboard ? (
                  <MessageSquare className="w-4 h-4" />
                ) : (
                  <Activity className="w-4 h-4" />
                )}
                <span className="text-sm">{showDashboard ? 'Chat' : 'Dashboard'}</span>
              </button>
              <span className="text-sm text-gray-400">Multi-Agent System</span>
            </div>
          </div>
        </header>

        {/* Chat Interface or Dashboard */}
        {showDashboard ? (
          <ObservabilityDashboard />
        ) : (
          <ChatInterface
            key={currentChat?.id}  // Force re-render when chat changes
            chat={currentChat}
            onNewChat={createNewChat}
            onChatUpdated={handleChatUpdated}
          />
        )}
      </div>

      {/* About Modal */}
      {showAbout && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-800 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-gray-700">
            {/* Modal Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-700">
              <div className="flex items-center gap-3">
                <Info className="w-6 h-6 text-blue-400" />
                <h2 className="text-xl font-bold">About Windows AI Assistant</h2>
              </div>
              <button
                onClick={() => setShowAbout(false)}
                className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Content */}
            <div className="p-6 space-y-6">
              {/* Overview */}
              <div>
                <h3 className="text-lg font-semibold mb-3 text-gray-300 flex items-center gap-2">
                  <Bot className="w-5 h-5" />
                  System Overview
                </h3>
                <div className="bg-gray-900 rounded p-4 text-sm text-gray-300">
                  <p className="mb-3">
                    Windows AI Assistant is a multi-agent AI system designed to help you with various tasks 
                    including code assistance, knowledge retrieval, productivity management, and Windows automation.
                  </p>
                  <p>
                    The system uses a local LLM (currently gpt2) for text generation and integrates with 
                    PostgreSQL for persistent storage, Redis for caching, and Qdrant for vector search.
                  </p>
                </div>
              </div>

              {/* Architecture */}
              <div>
                <h3 className="text-lg font-semibold mb-3 text-gray-300 flex items-center gap-2">
                  <Code className="w-5 h-5" />
                  Architecture
                </h3>
                <div className="bg-gray-900 rounded p-4 text-sm text-gray-300">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <h4 className="font-semibold text-blue-400 mb-2">Agents</h4>
                      <ul className="space-y-1 text-gray-400">
                        <li>• <span className="text-white">Supervisor</span> - Orchestrates other agents</li>
                        <li>• <span className="text-white">Knowledge</span> - Retrieves information</li>
                        <li>• <span className="text-white">Code</span> - Code assistance</li>
                        <li>• <span className="text-white">Windows</span> - Windows automation</li>
                        <li>• <span className="text-white">System</span> - System operations</li>
                        <li>• <span className="text-white">Productivity</span> - Task management</li>
                      </ul>
                    </div>
                    <div>
                      <h4 className="font-semibold text-green-400 mb-2">Infrastructure</h4>
                      <ul className="space-y-1 text-gray-400">
                        <li>• <span className="text-white">PostgreSQL</span> - Persistent database</li>
                        <li>• <span className="text-white">Redis</span> - Cache layer</li>
                        <li>• <span className="text-white">Qdrant</span> - Vector database</li>
                        <li>• <span className="text-white">FastAPI</span> - Backend API</li>
                        <li>• <span className="text-white">React</span> - Frontend UI</li>
                        <li>• <span className="text-white">gpt2</span> - Local LLM</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>

              {/* Current Configuration */}
              <div>
                <h3 className="text-lg font-semibold mb-3 text-gray-300 flex items-center gap-2">
                  <Shield className="w-5 h-5" />
                  Current Configuration
                </h3>
                <div className="bg-gray-900 rounded p-4 text-sm text-gray-300">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <h4 className="font-semibold text-purple-400 mb-2">LLM Configuration</h4>
                      <ul className="space-y-1 text-gray-400">
                        <li>• <span className="text-white">Model:</span> gpt2 (124M parameters)</li>
                        <li>• <span className="text-white">Location:</span> Local (cached)</li>
                        <li>• <span className="text-white">Cost:</span> Free</li>
                        <li>• <span className="text-white">Privacy:</span> 100% local</li>
                      </ul>
                    </div>
                    <div>
                      <h4 className="font-semibold text-yellow-400 mb-2">System Status</h4>
                      <ul className="space-y-1 text-gray-400">
                        <li>• <span className="text-white">Backend:</span> Running on port 8000</li>
                        <li>• <span className="text-white">Frontend:</span> Running on port 5173</li>
                        <li>• <span className="text-white">Database:</span> PostgreSQL connected</li>
                        <li>• <span className="text-white">Cache:</span> Redis connected</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>

              {/* Upgrade Options */}
              <div>
                <h3 className="text-lg font-semibold mb-3 text-gray-300 flex items-center gap-2">
                  <Cpu className="w-5 h-5" />
                  Upgrade Options
                </h3>
                <div className="bg-gray-900 rounded p-4 text-sm text-gray-300">
                  <p className="mb-3">
                    The current gpt2 model has limited capabilities. For better performance, consider upgrading to:
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-gray-800 rounded p-3 border border-gray-700">
                      <h4 className="font-semibold text-green-400 mb-2">Groq (Free)</h4>
                      <ul className="space-y-1 text-gray-400 text-xs">
                        <li>• Llama 3.1 8B model</li>
                        <li>• Ultra-fast (500 tokens/s)</li>
                        <li>• Completely free</li>
                        <li>• Better quality responses</li>
                      </ul>
                    </div>
                    <div className="bg-gray-800 rounded p-3 border border-gray-700">
                      <h4 className="font-semibold text-blue-400 mb-2">RunPod ($10/1M tokens)</h4>
                      <ul className="space-y-1 text-gray-400 text-xs">
                        <li>• Qwen 32B model</li>
                        <li>• Excellent quality</li>
                        <li>• Affordable pricing</li>
                        <li>• Advanced capabilities</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>

              {/* Support */}
              <div>
                <h3 className="text-lg font-semibold mb-3 text-gray-300">Support & Documentation</h3>
                <div className="bg-gray-900 rounded p-4 text-sm text-gray-300">
                  <p>
                    For more information, check the project documentation or contact support for assistance 
                    with configuration, troubleshooting, or feature requests.
                  </p>
                </div>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="p-6 border-t border-gray-700">
              <button
                onClick={() => setShowAbout(false)}
                className="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Documents Modal */}
      {showDocuments && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-800 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto border border-gray-700">
            {/* Modal Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-700">
              <div className="flex items-center gap-3">
                <FileText className="w-6 h-6 text-blue-400" />
                <h2 className="text-xl font-bold">Document Manager</h2>
              </div>
              <button
                onClick={() => setShowDocuments(false)}
                className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Content */}
            <div className="p-6">
              <DocumentManager />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
