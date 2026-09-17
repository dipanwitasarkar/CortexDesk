import { useState, useEffect } from 'react'
import ChatInterface from './components/ChatInterface'
import Sidebar from './components/Sidebar'
import ObservabilityDashboard from './components/ObservabilityDashboard'
import DocumentManager from './components/DocumentManager'
import MCPManager from './components/MCPManager'
import LLMManager from './components/LLMManager'
import { ToastProvider } from './components/ToastContainer'
import { Chat } from './types'
import { Activity, MessageSquare, Info, X, Bot, Code, Shield, Cpu, FileText, Plug, Settings } from 'lucide-react'
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts'
import { useAccessibility } from './hooks/useAccessibility'

// API URL configuration
const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [chats, setChats] = useState<Chat[]>([])
  const [currentChat, setCurrentChat] = useState<Chat | null>(null)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [showDashboard, setShowDashboard] = useState(false)
  const [showAbout, setShowAbout] = useState(false)
  const [showDocuments, setShowDocuments] = useState(false)
  const [showMCP, setShowMCP] = useState(false)
  const [showLLM, setShowLLM] = useState(false)
  const [loadingChats, setLoadingChats] = useState(true)

  useEffect(() => {
    // Load chats from API
    loadChats()
  }, [])

  const loadChats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/chats?user_id=1`)
      if (response.ok) {
        const data = await response.json()
        setChats(data)
      }
    } catch (error) {
      console.error('Failed to load chats:', error)
    } finally {
      setLoadingChats(false)
    }
  }

  const createNewChat = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/chats`, {
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

  // Keyboard shortcuts
  useKeyboardShortcuts([
    {
      key: 'n',
      ctrlKey: true,
      handler: createNewChat,
      description: 'New Chat'
    },
    {
      key: 'd',
      ctrlKey: true,
      handler: () => setShowDocuments(!showDocuments),
      description: 'Toggle Documents'
    },
    {
      key: 'o',
      ctrlKey: true,
      handler: () => setShowDashboard(!showDashboard),
      description: 'Toggle Observability'
    },
    {
      key: 'm',
      ctrlKey: true,
      handler: () => setShowMCP(!showMCP),
      description: 'Toggle MCP Manager'
    },
    {
      key: 'l',
      ctrlKey: true,
      handler: () => setShowLLM(!showLLM),
      description: 'Toggle LLM Configuration'
    },
    {
      key: '?',
      handler: () => setShowAbout(!showAbout),
      description: 'Show About'
    }
  ])

  // Accessibility features
  const { announceToScreenReader } = useAccessibility()

  // Announce important events to screen readers
  useEffect(() => {
    if (currentChat) {
      announceToScreenReader(`Opened chat: ${currentChat.title}`)
    }
  }, [currentChat, announceToScreenReader])

  return (
    <ToastProvider>
      <a href="#main-content" className="skip-to-content">
        Skip to main content
      </a>
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
          loading={loadingChats}
        />
      )}

      {/* Main Content */}
      <div id="main-content" className="flex-1 flex flex-col overflow-hidden" role="main">
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
              <h1 className="text-xl font-semibold">CortexDesk</h1>
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
                onClick={() => setShowMCP(true)}
                className="flex items-center gap-2 px-3 py-2 rounded-lg bg-gray-700 text-gray-300 hover:bg-gray-600 transition-colors"
                title="MCP Integrations"
              >
                <Plug className="w-4 h-4" />
                <span className="text-sm">MCP</span>
              </button>
              <button
                onClick={() => setShowLLM(true)}
                className="flex items-center gap-2 px-3 py-2 rounded-lg bg-gray-700 text-gray-300 hover:bg-gray-600 transition-colors"
                title="LLM Configuration"
              >
                <Settings className="w-4 h-4" />
                <span className="text-sm">LLM</span>
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
                <h2 className="text-xl font-bold">About CortexDesk</h2>
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
                    CortexDesk is a multi-agent AI system designed to help you with various tasks 
                    including code assistance, knowledge retrieval, productivity management, and Windows automation.
                  </p>
                  <p>
                    The system uses local models for complete offline capability: GPT-2 for text generation 
                    and sentence-transformers/all-MiniLM-L6-v2 for embeddings, with PostgreSQL for persistent storage, 
                    Redis for runtime state, and Qdrant v1.12.0 for vector search and RAG.
                  </p>
                  <p className="mt-2">
                    LLM providers are configurable via UI - switch between local GPT-2 and cloud providers 
                    (Groq, RunPod, OpenAI, Anthropic, Azure, Custom) without restarting the backend.
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
                        <li>• <span className="text-white">Supervisor</span> - Orchestrates other agents with full logging</li>
                        <li>• <span className="text-white">Knowledge</span> - Retrieves information with RAG</li>
                        <li>• <span className="text-white">Code</span> - Code assistance and analysis</li>
                        <li>• <span className="text-white">Windows</span> - Windows automation</li>
                        <li>• <span className="text-white">System</span> - System operations</li>
                        <li>• <span className="text-white">Productivity</span> - Task management</li>
                      </ul>
                    </div>
                    <div>
                      <h4 className="font-semibold text-green-400 mb-2">Infrastructure</h4>
                      <ul className="space-y-1 text-gray-400">
                        <li>• <span className="text-white">PostgreSQL</span> - Business data + observability</li>
                        <li>• <span className="text-white">Redis</span> - Runtime state (2GB, allkeys-lru)</li>
                        <li>• <span className="text-white">Qdrant v1.12.0</span> - Vector database (384-dim)</li>
                        <li>• <span className="text-white">FastAPI</span> - Backend API</li>
                        <li>• <span className="text-white">React</span> - Frontend UI with modern UX</li>
                        <li>• <span className="text-white">GPT-2</span> - Local generation (124M params)</li>
                        <li>• <span className="text-white">sentence-transformers</span> - Local embeddings (384-dim)</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>

              {/* Features */}
              <div>
                <h3 className="text-lg font-semibold mb-3 text-gray-300 flex items-center gap-2">
                  <Cpu className="w-5 h-5" />
                  Key Features
                </h3>
                <div className="bg-gray-900 rounded p-4 text-sm text-gray-300">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <h4 className="font-semibold text-yellow-400 mb-2">User Experience</h4>
                      <ul className="space-y-1 text-gray-400">
                        <li>• Toast notifications for feedback</li>
                        <li>• Keyboard shortcuts (Ctrl+N, D, O, M, L)</li>
                        <li>• Loading states with skeleton loaders</li>
                        <li>• Accessibility features (screen reader)</li>
                        <li>• Real-time updates with auto-refresh</li>
                        <li>• Data filtering and search</li>
                      </ul>
                    </div>
                    <div>
                      <h4 className="font-semibold text-pink-400 mb-2">Observability</h4>
                      <ul className="space-y-1 text-gray-400">
                        <li>• Real-time performance monitoring</li>
                        <li>• Detailed agent execution logs</li>
                        <li>• Request traces with timing</li>
                        <li>• Database statistics</li>
                        <li>• Qdrant vector database view</li>
                        <li>• Data purge management</li>
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
                      <h4 className="font-semibold text-purple-400 mb-2">AI Models</h4>
                      <ul className="space-y-1 text-gray-400">
                        <li>• <span className="text-white">Generation:</span> GPT-2 (124M parameters)</li>
                        <li>• <span className="text-white">Embeddings:</span> sentence-transformers/all-MiniLM-L6-v2</li>
                        <li>• <span className="text-white">Location:</span> 100% local</li>
                        <li>• <span className="text-white">Cost:</span> Free</li>
                        <li>• <span className="text-white">Privacy:</span> Complete offline capability</li>
                        <li>• <span className="text-white">RAG:</span> Full semantic search support</li>
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

      {/* MCP Modal */}
      {showMCP && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-800 rounded-lg max-w-6xl w-full max-h-[90vh] overflow-y-auto border border-gray-700">
            {/* Modal Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-700">
              <div className="flex items-center gap-3">
                <Plug className="w-6 h-6 text-purple-400" />
                <h2 className="text-xl font-bold">MCP Integrations</h2>
              </div>
              <button
                onClick={() => setShowMCP(false)}
                className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Content */}
            <div className="p-6">
              <MCPManager />
            </div>
          </div>
        </div>
      )}

      {/* LLM Modal */}
      {showLLM && (
        <LLMManager onClose={() => setShowLLM(false)} />
      )}
    </div>
    </ToastProvider>
  )
}

export default App
