# CortexDesk Low-Level Design (LLD) - Part 5: Frontend Architecture

## Document Overview

This document provides detailed specifications for the React frontend architecture, including component structure, state management, custom hooks, API integration, styling, performance optimization, accessibility, and testing.

**Document Parts:**
- Part 1: Architecture & System Design
- Part 2: Data Models & Database Schema
- Part 3: API Specifications
- Part 4: Agent Implementation Details
- Part 5: Frontend Architecture (This document)
- Part 6: Deployment & Infrastructure

---

## 1. Frontend Overview

### 1.1 Technology Stack

**Framework:** React 18.2.0
**Language:** TypeScript 5.3.3
**Build Tool:** Vite 5.4.21
**Styling:** Tailwind CSS 3.4.0
**Icons:** Lucide React 0.303.0
**HTTP Client:** Fetch API with Vite proxy

### 1.2 Project Structure

```
frontend/
├── public/
│   └── vite.svg
├── src/
│   ├── components/
│   │   ├── App.tsx
│   │   ├── ChatInterface.tsx
│   │   ├── Sidebar.tsx
│   │   ├── ObservabilityDashboard.tsx
│   │   ├── DocumentManager.tsx
│   │   ├── MCPManager.tsx
│   │   ├── LLMManager.tsx
│   │   ├── Toast.tsx
│   │   └── ToastContainer.tsx
│   ├── hooks/
│   │   ├── useKeyboardShortcuts.ts
│   │   ├── useAccessibility.ts
│   │   ├── useWebSocket.ts
│   │   └── useRetry.ts
│   ├── types/
│   │   └── index.ts
│   ├── App.tsx
│   ├── main.tsx
│   └── vite-env.d.ts
├── index.html
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── vite.config.ts
```

### 1.3 Component Hierarchy

```
App (Main Application)
├── Header (Navigation)
│   ├── Logo
│   ├── Navigation Buttons
│   └── MCP Button
├── Sidebar (Chat List)
│   ├── New Chat Button
│   ├── Chat List Items
│   └── Delete Chat Button
├── ChatInterface (Main Chat Area)
│   ├── Message List
│   ├── Message Input
│   └── Typing Indicator
├── DocumentManager (Modal)
│   ├── Document List
│   ├── Upload Button
│   └── Search Input
├── ObservabilityDashboard (Modal)
│   ├── Overview Tab
│   ├── Logs Tab
│   ├── Traces Tab
│   ├── Database Tab
│   ├── Runtime State Tab
│   └── Qdrant Tab
├── MCPManager (Modal)
│   ├── Integration List
│   ├── Add Integration Form
│   └── Test Connection Button
├── LLMManager (Modal)
│   ├── Configuration List
│   ├── Add Configuration Form
│   ├── Provider Selection
│   └── Test Connection Button
├── About Modal
│   ├── System Overview
│   ├── Architecture
│   ├── Features
│   └── Configuration
└── ToastContainer (Notifications)
    └── Toast Components
```

---

## 2. Core Components

### 2.1 App Component

**File:** `frontend/src/App.tsx`

**Purpose:** Main application component with routing and modal management.

**State:**
```typescript
interface AppState {
  showDocuments: boolean;
  showObservability: boolean;
  showMCP: boolean;
  showAbout: boolean;
  selectedChat: number | null;
  chats: Chat[];
  messages: Message[];
  loading: boolean;
}
```

**Key Features:**
- Modal management (documents, observability, MCP, about)
- Chat selection and management
- Keyboard shortcut handling
- Accessibility features
- Toast notification integration

**Example:**
```typescript
function App() {
  const [showDocuments, setShowDocuments] = useState(false);
  const [showObservability, setShowObservability] = useState(false);
  const [showMCP, setShowMCP] = useState(false);
  const [showAbout, setShowAbout] = useState(false);
  const [selectedChat, setSelectedChat] = useState<number | null>(null);
  const [chats, setChats] = useState<Chat[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  
  // Keyboard shortcuts
  useKeyboardShortcuts({
    'Ctrl+N': () => handleNewChat(),
    'Ctrl+D': () => setShowDocuments(!showDocuments),
    'Ctrl+O': () => setShowObservability(!showObservability),
    'Ctrl+M': () => setShowMCP(!showMCP),
    '?': () => setShowAbout(true),
    'Escape': () => {
      setShowDocuments(false);
      setShowObservability(false);
      setShowMCP(false);
      setShowAbout(false);
    }
  });
  
  // Render UI
  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <Header />
      
      {/* Main Content */}
      <div className="flex">
        <Sidebar />
        <ChatInterface />
      </div>
      
      {/* Modals */}
      {showDocuments && <DocumentManager />}
      {showObservability && <ObservabilityDashboard />}
      {showMCP && <MCPManager />}
      {showAbout && <AboutModal />}
      
      {/* Toast Container */}
      <ToastContainer />
    </div>
  );
}
```

---

### 2.2 ChatInterface Component

**File:** `frontend/src/components/ChatInterface.tsx`

**Purpose:** Main chat interface with message display and input.

**State:**
```typescript
interface ChatInterfaceState {
  messages: Message[];
  input: string;
  loading: boolean;
  typing: boolean;
}
```

**Key Features:**
- Message list with role-based styling
- Message input with auto-resize
- Typing indicator
- Streaming response support (future)
- Message edit/delete (future)

**Example:**
```typescript
function ChatInterface({ selectedChat }: { selectedChat: number | null }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [typing, setTyping] = useState(false);
  const { success, error } = useToast();
  
  const handleSendMessage = async () => {
    if (!input.trim() || loading) return;
    
    setLoading(true);
    setTyping(true);
    
    try {
      // Add user message
      const userMessage: Message = {
        id: Date.now(),
        role: 'user',
        content: input,
        created_at: new Date().toISOString()
      };
      setMessages(prev => [...prev, userMessage]);
      
      // Send to backend
      const response = await fetch('/api/v1/assistant', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: input,
          user_id: 1,
          chat_id: selectedChat
        })
      });
      
      const data = await response.json();
      
      // Add assistant message
      const assistantMessage: Message = {
        id: Date.now() + 1,
        role: 'assistant',
        content: data.response,
        agent_used: data.agents_used[0],
        created_at: new Date().toISOString()
      };
      setMessages(prev => [...prev, assistantMessage]);
      
      success('Message sent successfully');
      setInput('');
      
    } catch (err) {
      error('Failed to send message');
    } finally {
      setLoading(false);
      setTyping(false);
    }
  };
  
  return (
    <div className="flex-1 flex flex-col">
      {/* Message List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        {typing && <TypingIndicator />}
      </div>
      
      {/* Input Area */}
      <div className="p-4 border-t border-gray-700">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSendMessage();
            }
          }}
          placeholder="Type your message..."
          className="w-full bg-gray-800 text-white rounded-lg p-3 resize-none"
          rows={3}
        />
        <button
          onClick={handleSendMessage}
          disabled={loading || !input.trim()}
          className="mt-2 px-4 py-2 bg-blue-600 rounded-lg disabled:opacity-50"
        >
          {loading ? 'Sending...' : 'Send'}
        </button>
      </div>
    </div>
  );
}
```

---

### 2.3 Sidebar Component

**File:** `frontend/src/components/Sidebar.tsx`

**Purpose:** Chat list with new chat and delete functionality.

**State:**
```typescript
interface SidebarState {
  chats: Chat[];
  loading: boolean;
}
```

**Key Features:**
- Chat list with titles
- New chat button
- Delete chat button
- Active chat highlighting
- Skeleton loaders

**Example:**
```typescript
function Sidebar({ selectedChat, onSelectChat }: SidebarProps) {
  const [chats, setChats] = useState<Chat[]>([]);
  const [loading, setLoading] = useState(true);
  const { success, error } = useToast();
  
  useEffect(() => {
    loadChats();
  }, []);
  
  const loadChats = async () => {
    try {
      const response = await fetch('/api/v1/chats?user_id=1');
      const data = await response.json();
      setChats(data);
    } catch (err) {
      error('Failed to load chats');
    } finally {
      setLoading(false);
    }
  };
  
  const handleNewChat = async () => {
    try {
      const response = await fetch('/api/v1/chats', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: 1 })
      });
      const data = await response.json();
      setChats(prev => [data, ...prev]);
      success('New chat created');
    } catch (err) {
      error('Failed to create chat');
    }
  };
  
  const handleDeleteChat = async (chatId: number) => {
    try {
      await fetch(`/api/v1/chats/${chatId}`, { method: 'DELETE' });
      setChats(prev => prev.filter(chat => chat.id !== chatId));
      success('Chat deleted');
    } catch (err) {
      error('Failed to delete chat');
    }
  };
  
  return (
    <div className="w-64 bg-gray-800 border-r border-gray-700 p-4">
      <button
        onClick={handleNewChat}
        className="w-full px-4 py-2 bg-blue-600 rounded-lg mb-4"
      >
        New Chat
      </button>
      
      {loading ? (
        <SkeletonLoader count={5} />
      ) : (
        <div className="space-y-2">
          {chats.map((chat) => (
            <div
              key={chat.id}
              onClick={() => onSelectChat(chat.id)}
              className={`p-3 rounded-lg cursor-pointer ${
                selectedChat === chat.id ? 'bg-blue-600' : 'bg-gray-700 hover:bg-gray-600'
              }`}
            >
              <div className="flex justify-between items-center">
                <span className="text-sm">{chat.title}</span>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDeleteChat(chat.id);
                  }}
                  className="text-red-400 hover:text-red-300"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

---

### 2.4 ObservabilityDashboard Component

**File:** `frontend/src/components/ObservabilityDashboard.tsx`

**Purpose:** System monitoring dashboard with real-time data.

**State:**
```typescript
interface ObservabilityState {
  performance: PerformanceData | null;
  errors: ErrorData | null;
  health: HealthData | null;
  logs: LogsData | null;
  traces: TracesData | null;
  database: DatabaseData | null;
  runtimeState: RuntimeStateData | null;
  qdrant: QdrantData | null;
  loading: boolean;
  autoRefresh: boolean;
  refreshInterval: number;
  activeTab: TabType;
  logFilter: string;
  traceFilter: string;
}
```

**Key Features:**
- Real-time performance monitoring
- Logs and traces display
- Database statistics
- Runtime state monitoring
- Qdrant vector database view
- Auto-refresh with configurable intervals
- Data filtering
- Purge functionality

**Example:**
```typescript
function ObservabilityDashboard() {
  const [performance, setPerformance] = useState<PerformanceData | null>(null);
  const [logs, setLogs] = useState<LogsData | null>(null);
  const [traces, setTraces] = useState<TracesData | null>(null);
  const [loading, setLoading] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [refreshInterval, setRefreshInterval] = useState(5);
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const { success, error } = useToast();
  
  const fetchData = async () => {
    setLoading(true);
    try {
      const [perfRes, logsRes, tracesRes] = await Promise.all([
        fetch('/api/v1/observability/performance'),
        fetch('/api/v1/observability/logs'),
        fetch('/api/v1/observability/traces')
      ]);
      
      const [perfData, logsData, tracesData] = await Promise.all([
        perfRes.json(),
        logsRes.json(),
        tracesRes.json()
      ]);
      
      setPerformance(perfData);
      setLogs(logsData);
      setTraces(tracesData);
      
      success('Observability data refreshed');
    } catch (err) {
      error('Failed to fetch observability data');
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    fetchData();
  }, []);
  
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (autoRefresh) {
      interval = setInterval(fetchData, refreshInterval * 1000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh, refreshInterval]);
  
  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Observability Dashboard</h1>
        <div className="flex items-center gap-2">
          <select
            value={refreshInterval}
            onChange={(e) => setRefreshInterval(Number(e.target.value))}
            className="bg-gray-700 text-white rounded px-3 py-1"
          >
            <option value={5}>5s</option>
            <option value={10}>10s</option>
            <option value={30}>30s</option>
            <option value={60}>1m</option>
          </select>
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`px-3 py-1 rounded ${autoRefresh ? 'bg-green-600' : 'bg-gray-700'}`}
          >
            {autoRefresh ? 'Auto-refreshing' : 'Auto-refresh'}
          </button>
          <button onClick={fetchData} disabled={loading}>
            <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>
      
      {/* Tabs */}
      <div className="flex gap-2">
        {['overview', 'logs', 'traces', 'database', 'runtime-state', 'qdrant'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab as TabType)}
            className={`px-4 py-2 rounded ${activeTab === tab ? 'bg-blue-600' : 'bg-gray-700'}`}
          >
            {tab}
          </button>
        ))}
      </div>
      
      {/* Tab Content */}
      {activeTab === 'overview' && <OverviewTab performance={performance} />}
      {activeTab === 'logs' && <LogsTab logs={logs} />}
      {activeTab === 'traces' && <TracesTab traces={traces} />}
      {/* ... other tabs */}
    </div>
  );
}
```

---

### 2.5 DocumentManager Component

**File:** `frontend/src/components/DocumentManager.tsx`

**Purpose:** Document upload and management with drag-and-drop.

**State:**
```typescript
interface DocumentManagerState {
  documents: Document[];
  loading: boolean;
  uploading: boolean;
  uploadProgress: number;
  searchQuery: string;
}
```

**Key Features:**
- Document list with status
- Drag-and-drop file upload
- Upload progress indicator
- Document search
- Document deletion
- Toast notifications

**Example:**
```typescript
function DocumentManager() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const { success, error } = useToast();
  
  const loadDocuments = async () => {
    try {
      const response = await fetch('/api/v1/documents?user_id=1');
      const data = await response.json();
      setDocuments(data);
    } catch (err) {
      error('Failed to load documents');
    } finally {
      setLoading(false);
    }
  };
  
  const handleFileUpload = async (file: File) => {
    setUploading(true);
    setUploadProgress(0);
    
    try {
      const content = await file.text();
      
      // Simulate upload progress
      for (let i = 0; i <= 100; i += 10) {
        setUploadProgress(i);
        await new Promise(resolve => setTimeout(resolve, 100));
      }
      
      const response = await fetch('/api/v1/documents', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 1,
          title: file.name,
          content: content,
          file_name: file.name,
          file_type: file.type
        })
      });
      
      const data = await response.json();
      setDocuments(prev => [data, ...prev]);
      success('Document uploaded successfully');
      
    } catch (err) {
      error('Failed to upload document');
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };
  
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) {
      handleFileUpload(file);
    }
  };
  
  const filteredDocuments = documents.filter(doc =>
    doc.title.toLowerCase().includes(searchQuery.toLowerCase())
  );
  
  return (
    <div className="p-6">
      <div
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
        className="border-2 border-dashed border-gray-600 rounded-lg p-8 text-center mb-4"
      >
        <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
        <p className="text-gray-400">Drag and drop files here or click to upload</p>
        <input
          type="file"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) handleFileUpload(file);
          }}
          className="hidden"
          id="file-upload"
        />
        <label
          htmlFor="file-upload"
          className="mt-4 px-4 py-2 bg-blue-600 rounded-lg cursor-pointer"
        >
          Select File
        </label>
      </div>
      
      {uploading && (
        <div className="mb-4">
          <div className="flex justify-between mb-2">
            <span>Uploading...</span>
            <span>{uploadProgress}%</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
        </div>
      )}
      
      <input
        type="text"
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        placeholder="Search documents..."
        className="w-full bg-gray-800 text-white rounded-lg p-3 mb-4"
      />
      
      {loading ? (
        <SkeletonLoader count={5} />
      ) : (
        <div className="space-y-2">
          {filteredDocuments.map((doc) => (
            <div key={doc.id} className="bg-gray-800 rounded-lg p-4">
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="font-semibold">{doc.title}</h3>
                  <p className="text-sm text-gray-400">
                    Status: {doc.embedding_status}
                  </p>
                </div>
                <button
                  onClick={() => handleDeleteDocument(doc.id)}
                  className="text-red-400 hover:text-red-300"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

---

### 2.6 MCPManager Component

**File:** `frontend/src/components/MCPManager.tsx`

**Purpose:** MCP integration management with status indicators.

**State:**
```typescript
interface MCPManagerState {
  integrations: MCPIntegration[];
  availableTypes: MCPType[];
  loading: boolean;
  showAddForm: boolean;
  selectedType: string;
  config: Record<string, string>;
}
```

**Key Features:**
- Integration list with status
- Add new integration
- Edit existing integration
- Delete integration
- Test connection
- Status indicators

**Example:**
```typescript
function MCPManager() {
  const [integrations, setIntegrations] = useState<MCPIntegration[]>([]);
  const [availableTypes, setAvailableTypes] = useState<MCPType[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [selectedType, setSelectedType] = useState('');
  const [config, setConfig] = useState<Record<string, string>>({});
  const { success, error } = useToast();
  
  const loadIntegrations = async () => {
    try {
      const [intRes, typesRes] = await Promise.all([
        fetch('/api/v1/mcp/integrations'),
        fetch('/api/v1/mcp/types')
      ]);
      
      const [intData, typesData] = await Promise.all([
        intRes.json(),
        typesRes.json()
      ]);
      
      setIntegrations(intData);
      setAvailableTypes(typesData.types);
    } catch (err) {
      error('Failed to load MCP integrations');
    } finally {
      setLoading(false);
    }
  };
  
  const handleCreateIntegration = async () => {
    try {
      const response = await fetch('/api/v1/mcp/integrations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: `${selectedType}-integration`,
          type: selectedType,
          config: config
        })
      });
      
      const data = await response.json();
      setIntegrations(prev => [...prev, data]);
      setShowAddForm(false);
      success('Integration created successfully');
    } catch (err) {
      error('Failed to create integration');
    }
  };
  
  const handleTestConnection = async (integrationId: number) => {
    try {
      const response = await fetch(`/api/v1/mcp/integrations/${integrationId}/test`, {
        method: 'POST'
      });
      const data = await response.json();
      
      if (data.success) {
        success('Connection test successful');
      } else {
        error('Connection test failed');
      }
    } catch (err) {
      error('Failed to test connection');
    }
  };
  
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'connected':
        return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'error':
        return <XCircle className="w-5 h-5 text-red-400" />;
      case 'connecting':
        return <RefreshCw className="w-5 h-5 text-yellow-400 animate-spin" />;
      default:
        return <AlertCircle className="w-5 h-5 text-gray-400" />;
    }
  };
  
  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold">MCP Integrations</h2>
        <button
          onClick={() => setShowAddForm(true)}
          className="px-4 py-2 bg-blue-600 rounded-lg"
        >
          Add Integration
        </button>
      </div>
      
      {loading ? (
        <SkeletonLoader count={5} />
      ) : (
        <div className="space-y-4">
          {integrations.map((integration) => (
            <div key={integration.id} className="bg-gray-800 rounded-lg p-4">
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-3">
                  {getStatusIcon(integration.status)}
                  <div>
                    <h3 className="font-semibold">{integration.name}</h3>
                    <p className="text-sm text-gray-400">{integration.type}</p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleTestConnection(integration.id)}
                    className="px-3 py-1 bg-gray-700 rounded"
                  >
                    Test
                  </button>
                  <button
                    onClick={() => handleDeleteIntegration(integration.id)}
                    className="px-3 py-1 bg-red-600 rounded"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
      
      {showAddForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center">
          <div className="bg-gray-800 rounded-lg p-6 max-w-md w-full">
            <h3 className="text-lg font-bold mb-4">Add Integration</h3>
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="w-full bg-gray-700 text-white rounded p-2 mb-4"
            >
              <option value="">Select type</option>
              {availableTypes.map((type) => (
                <option key={type.type} value={type.type}>
                  {type.name}
                </option>
              ))}
            </select>
            
            {selectedType && (
              <div className="space-y-2 mb-4">
                {Object.entries(
                  availableTypes.find(t => t.type === selectedType)?.config_schema?.properties || {}
                ).map(([key, prop]: [string, any]) => (
                  <div key={key}>
                    <label className="block text-sm mb-1">{prop.description}</label>
                    <input
                      type="text"
                      value={config[key] || ''}
                      onChange={(e) => setConfig({ ...config, [key]: e.target.value })}
                      className="w-full bg-gray-700 text-white rounded p-2"
                    />
                  </div>
                ))}
              </div>
            )}
            
            <div className="flex gap-2">
              <button
                onClick={() => setShowAddForm(false)}
                className="flex-1 px-4 py-2 bg-gray-700 rounded"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateIntegration}
                className="flex-1 px-4 py-2 bg-blue-600 rounded"
              >
                Create
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
```

---

### 2.7 Toast Components

**File:** `frontend/src/components/Toast.tsx`

**Purpose:** Toast notification system for user feedback.

**Components:**
- `ToastComponent`: Individual toast notification
- `ToastContainer`: Container for all toasts

**Toast Types:**
- Success (green)
- Error (red)
- Warning (yellow)
- Info (blue)

**Example:**
```typescript
// Toast.tsx
interface ToastProps {
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  onClose: () => void;
}

export function ToastComponent({ type, message, onClose }: ToastProps) {
  const icons = {
    success: <CheckCircle className="w-5 h-5" />,
    error: <XCircle className="w-5 h-5" />,
    warning: <AlertCircle className="w-5 h-5" />,
    info: <Info className="w-5 h-5" />
  };
  
  const colors = {
    success: 'bg-green-600',
    error: 'bg-red-600',
    warning: 'bg-yellow-600',
    info: 'bg-blue-600'
  };
  
  return (
    <div className={`${colors[type]} text-white px-4 py-3 rounded-lg shadow-lg flex items-center gap-3`}>
      {icons[type]}
      <span>{message}</span>
      <button onClick={onClose} className="ml-2">
        <X className="w-4 h-4" />
      </button>
    </div>
  );
}

// ToastContainer.tsx
interface Toast {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
}

export function ToastContainer() {
  const [toasts, setToasts] = useState<Toast[]>([]);
  
  const addToast = (type: Toast['type'], message: string) => {
    const id = Date.now().toString();
    setToasts(prev => [...prev, { id, type, message }]);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
      setToasts(prev => prev.filter(toast => toast.id !== id));
    }, 5000);
  };
  
  const removeToast = (id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  };
  
  const value = {
    success: (message: string) => addToast('success', message),
    error: (message: string) => addToast('error', message),
    warning: (message: string) => addToast('warning', message),
    info: (message: string) => addToast('info', message)
  };
  
  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="fixed top-4 right-4 space-y-2 z-50">
        {toasts.map((toast) => (
          <ToastComponent
            key={toast.id}
            type={toast.type}
            message={toast.message}
            onClose={() => removeToast(toast.id)}
          />
        ))}
      </div>
    </ToastContext.Provider>
  );
}
```

---

## 3. Custom Hooks

### 3.1 useKeyboardShortcuts

**File:** `frontend/src/hooks/useKeyboardShortcuts.ts`

**Purpose:** Handle keyboard shortcuts for common actions.

**Example:**
```typescript
function useKeyboardShortcuts(shortcuts: Record<string, () => void>) {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const key = e.key;
      const modifiers = [];
      
      if (e.ctrlKey || e.metaKey) modifiers.push('Ctrl');
      if (e.shiftKey) modifiers.push('Shift');
      if (e.altKey) modifiers.push('Alt');
      
      const shortcut = [...modifiers, key].join('+');
      
      if (shortcuts[shortcut]) {
        e.preventDefault();
        shortcuts[shortcut]();
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [shortcuts]);
}
```

**Usage:**
```typescript
useKeyboardShortcuts({
  'Ctrl+N': () => handleNewChat(),
  'Ctrl+D': () => setShowDocuments(!showDocuments),
  'Ctrl+O': () => setShowObservability(!showObservability),
  'Ctrl+M': () => setShowMCP(!showMCP),
  'Ctrl+L': () => setShowLLM(!showLLM),
  '?': () => setShowAbout(true),
  'Escape': () => closeAllModals()
});
```

---

### 3.2 useAccessibility

**File:** `frontend/src/hooks/useAccessibility.ts`

**Purpose:** Implement accessibility features (screen reader, focus management).

**Example:**
```typescript
function useAccessibility() {
  useEffect(() => {
    // Skip to content link
    const skipLink = document.createElement('a');
    skipLink.href = '#main-content';
    skipLink.textContent = 'Skip to main content';
    skipLink.className = 'sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4';
    document.body.prepend(skipLink);
    
    // Add main content id
    const mainContent = document.getElementById('main-content');
    if (mainContent) {
      mainContent.tabIndex = -1;
    }
    
    return () => {
      skipLink.remove();
    };
  }, []);
  
  const announceToScreenReader = (message: string) => {
    const announcement = document.createElement('div');
    announcement.setAttribute('role', 'status');
    announcement.setAttribute('aria-live', 'polite');
    announcement.className = 'sr-only';
    announcement.textContent = message;
    document.body.appendChild(announcement);
    
    setTimeout(() => {
      document.body.removeChild(announcement);
    }, 1000);
  };
  
  return { announceToScreenReader };
}
```

---

### 3.3 useWebSocket

**File:** `frontend/src/hooks/useWebSocket.ts`

**Purpose:** WebSocket connection management for real-time updates.

**Example:**
```typescript
function useWebSocket(url: string) {
  const [connected, setConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<any>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  
  const connect = useCallback(() => {
    const ws = new WebSocket(url);
    wsRef.current = ws;
    
    ws.onopen = () => {
      setConnected(true);
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setLastMessage(data);
    };
    
    ws.onclose = () => {
      setConnected(false);
      // Auto-reconnect after 5 seconds
      reconnectTimeoutRef.current = setTimeout(() => {
        connect();
      }, 5000);
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }, [url]);
  
  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
  }, []);
  
  useEffect(() => {
    connect();
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);
  
  const sendMessage = useCallback((message: any) => {
    if (wsRef.current && connected) {
      wsRef.current.send(JSON.stringify(message));
    }
  }, [connected]);
  
  return { connected, lastMessage, sendMessage, disconnect };
}
```

---

### 3.4 useRetry

**File:** `frontend/src/hooks/useRetry.ts`

**Purpose:** Retry logic with exponential backoff for failed operations.

**Example:**
```typescript
function useRetry(maxAttempts: number = 3, baseDelay: number = 1000) {
  const [attempt, setAttempt] = useState(0);
  const [loading, setLoading] = useState(false);
  
  const execute = useCallback(async <T,>(
    fn: () => Promise<T>
  ): Promise<T | null> => {
    setLoading(true);
    
    for (let i = 0; i < maxAttempts; i++) {
      try {
        setAttempt(i + 1);
        const result = await fn();
        setLoading(false);
        return result;
      } catch (error) {
        if (i === maxAttempts - 1) {
          setLoading(false);
          throw error;
        }
        
        // Exponential backoff
        const delay = baseDelay * Math.pow(2, i);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
    
    setLoading(false);
    return null;
  }, [maxAttempts, baseDelay]);
  
  return { execute, attempt, loading };
}
```

---

## 4. State Management

### 4.1 Local State

**useState for Component State:**
```typescript
const [count, setCount] = useState(0);
const [user, setUser] = useState<User | null>(null);
const [items, setItems] = useState<Item[]>([]);
```

### 4.2 Global State

**Context API for Global State:**
```typescript
// Create context
interface AppContextType {
  user: User | null;
  setUser: (user: User | null) => void;
  theme: 'light' | 'dark';
  setTheme: (theme: 'light' | 'dark') => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

// Provider
export function AppProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [theme, setTheme] = useState<'light' | 'dark'>('dark');
  
  return (
    <AppContext.Provider value={{ user, setUser, theme, setTheme }}>
      {children}
    </AppContext.Provider>
  );
}

// Consumer
export function useApp() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within AppProvider');
  }
  return context;
}
```

### 4.3 Server State

**React Query for Server State (Future):**
```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

// Fetch data
function useChats() {
  return useQuery({
    queryKey: ['chats'],
    queryFn: async () => {
      const response = await fetch('/api/v1/chats?user_id=1');
      return response.json();
    }
  });
}

// Mutate data
function useCreateChat() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: CreateChatData) => {
      const response = await fetch('/api/v1/chats', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chats'] });
    }
  });
}
```

---

## 5. API Integration

### 5.1 API Client

**Fetch Wrapper:**
```typescript
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `/api/v1${endpoint}`;
  
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    },
    ...options
  });
  
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  
  return response.json();
}

// Usage
const chats = await apiRequest<Chat[]>('/chats?user_id=1');
```

### 5.2 API Hooks

**Custom Hook for API Calls:**
```typescript
function useApi<T>(endpoint: string) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  
  useEffect(() => {
    apiRequest<T>(endpoint)
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false));
  }, [endpoint]);
  
  return { data, loading, error, refetch: () => {
    setLoading(true);
    apiRequest<T>(endpoint)
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false));
  }};
}
```

---

## 6. Styling

### 6.1 Tailwind CSS Configuration

**File:** `frontend/tailwind.config.js`
```javascript
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        gray: {
          900: '#1a1a1a',
          800: '#2d2d2d',
          700: '#404040',
          600: '#525252',
        }
      }
    },
  },
  plugins: [],
}
```

### 6.2 Component Styling

**Example Styling:**
```typescript
// Button component
<button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50">
  Click me
</button>

// Card component
<div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
  <h2 className="text-xl font-bold mb-4">Card Title</h2>
  <p className="text-gray-300">Card content</p>
</div>

// Input component
<input className="w-full bg-gray-700 text-white rounded-lg p-3 border border-gray-600 focus:border-blue-500 focus:outline-none" />
```

---

## 7. Performance Optimization

### 7.1 Code Splitting

**React.lazy for Lazy Loading:**
```typescript
const ObservabilityDashboard = React.lazy(() => import('./components/ObservabilityDashboard'));
const DocumentManager = React.lazy(() => import('./components/DocumentManager'));

// Usage with Suspense
<Suspense fallback={<SkeletonLoader />}>
  {showObservability && <ObservabilityDashboard />}
</Suspense>
```

### 7.2 Memoization

**React.memo for Component Memoization:**
```typescript
const MessageBubble = React.memo(({ message }: { message: Message }) => {
  return (
    <div className="p-3 rounded-lg">
      <p>{message.content}</p>
    </div>
  );
});
```

**useMemo for Expensive Computations:**
```typescript
const filteredDocuments = useMemo(() => {
  return documents.filter(doc =>
    doc.title.toLowerCase().includes(searchQuery.toLowerCase())
  );
}, [documents, searchQuery]);
```

**useCallback for Function Memoization:**
```typescript
const handleDeleteChat = useCallback(async (chatId: number) => {
  await fetch(`/api/v1/chats/${chatId}`, { method: 'DELETE' });
  setChats(prev => prev.filter(chat => chat.id !== chatId));
}, []);
```

### 7.3 Virtual Scrolling

**React Virtual for Long Lists (Future):**
```typescript
import { useVirtualizer } from '@tanstack/react-virtual';

function VirtualList({ items }: { items: Item[] }) {
  const parentRef = useRef<HTMLDivElement>(null);
  
  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
  });
  
  return (
    <div ref={parentRef} style={{ height: '400px', overflow: 'auto' }}>
      <div style={{ height: `${virtualizer.getTotalSize()}px` }}>
        {virtualizer.getVirtualItems().map((virtualItem) => (
          <div
            key={virtualItem.key}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: `${virtualItem.size}px`,
              transform: `translateY(${virtualItem.start}px)`,
            }}
          >
            {items[virtualItem.index].content}
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## 8. Accessibility

### 8.1 ARIA Attributes

**ARIA Labels:**
```typescript
<button
  onClick={handleDelete}
  aria-label="Delete chat"
>
  <Trash2 className="w-4 h-4" />
</button>
```

**ARIA Live Regions:**
```typescript
<div
  role="status"
  aria-live="polite"
  aria-atomic="true"
>
  {statusMessage}
</div>
```

**Modal Accessibility:**
```typescript
<div
  role="dialog"
  aria-modal="true"
  aria-labelledby="modal-title"
>
  <h2 id="modal-title">Modal Title</h2>
  {/* Modal content */}
</div>
```

### 8.2 Keyboard Navigation

**Focus Management:**
```typescript
const modalRef = useRef<HTMLDivElement>(null);

useEffect(() => {
  if (showModal) {
    // Focus first focusable element
    const firstFocusable = modalRef.current?.querySelector(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    firstFocusable?.focus();
  }
}, [showModal]);
```

**Focus Trapping:**
```typescript
useEffect(() => {
  if (showModal) {
    const handleTab = (e: KeyboardEvent) => {
      if (e.key === 'Tab') {
        const focusableElements = modalRef.current?.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        const firstElement = focusableElements?.[0];
        const lastElement = focusableElements?.[focusableElements.length - 1];
        
        if (e.shiftKey && document.activeElement === firstElement) {
          e.preventDefault();
          lastElement?.focus();
        } else if (!e.shiftKey && document.activeElement === lastElement) {
          e.preventDefault();
          firstElement?.focus();
        }
      }
    };
    
    document.addEventListener('keydown', handleTab);
    return () => document.removeEventListener('keydown', handleTab);
  }
}, [showModal]);
```

### 8.3 Screen Reader Support

**Semantic HTML:**
```typescript
<nav aria-label="Main navigation">
  {/* Navigation links */}
</nav>

<main id="main-content">
  {/* Main content */}
</main>

<aside aria-label="Chat list">
  {/* Sidebar */}
</aside>
```

---

## 9. Testing

### 9.1 Unit Testing

**Jest + React Testing Library:**
```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './Button';

describe('Button', () => {
  it('renders button text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });
  
  it('calls onClick when clicked', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    
    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
```

### 9.2 Integration Testing

**Testing Component Integration:**
```typescript
import { render, screen, waitFor } from '@testing-library/react';
import { ChatInterface } from './ChatInterface';

describe('ChatInterface', () => {
  it('loads messages on mount', async () => {
    render(<ChatInterface selectedChat={1} />);
    
    await waitFor(() => {
      expect(screen.getByText('Hello')).toBeInTheDocument();
    });
  });
  
  it('sends message when send button clicked', async () => {
    render(<ChatInterface selectedChat={1} />);
    
    const input = screen.getByPlaceholderText('Type your message...');
    const sendButton = screen.getByText('Send');
    
    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.click(sendButton);
    
    await waitFor(() => {
      expect(screen.getByText('Test message')).toBeInTheDocument();
    });
  });
});
```

### 9.3 E2E Testing

**Playwright for E2E Tests (Future):**
```typescript
import { test, expect } from '@playwright/test';

test('user can create a new chat', async ({ page }) => {
  await page.goto('http://localhost:5173');
  
  await page.click('button:has-text("New Chat")');
  
  await expect(page.locator('.chat-item')).toHaveCount(1);
});

test('user can send a message', async ({ page }) => {
  await page.goto('http://localhost:5173');
  
  await page.fill('textarea', 'Hello');
  await page.click('button:has-text("Send")');
  
  await expect(page.locator('.message').last()).toContainText('Hello');
});
```

---

## 10. Build Configuration

### 10.1 Vite Configuration

**File:** `frontend/vite.config.ts`
```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          ui: ['lucide-react']
        }
      }
    }
  }
});
```

### 10.2 TypeScript Configuration

**File:** `frontend/tsconfig.json`
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

---

## 11. Deployment

### 11.1 Build Process

**Development:**
```bash
npm run dev
```

**Production Build:**
```bash
npm run build
```

**Preview Build:**
```bash
npm run preview
```

### 11.2 Static File Serving

**Nginx Configuration (Future):**
```nginx
server {
  listen 80;
  server_name cortexdesk.com;
  
  root /var/www/cortexdesk/dist;
  index index.html;
  
  location / {
    try_files $uri $uri/ /index.html;
  }
  
  location /api {
    proxy_pass http://localhost:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
  }
}
```

---

### 2.7 LLMManager Component

**File:** `frontend/src/components/LLMManager.tsx`

**Purpose:** LLM provider configuration management with dynamic switching capability.

**State:**
```typescript
interface LLMManagerState {
  configurations: LLMConfiguration[];
  availableProviders: LLMProvider[];
  loading: boolean;
  showAddForm: boolean;
  selectedProvider: string;
  config: {
    model_name: string;
    endpoint: string;
    api_key: string;
    temperature: number;
    max_tokens: number;
  };
  testing: boolean;
}
```

**Key Features:**
- Configuration list with active status
- Add new LLM configuration
- Delete configuration
- Activate configuration
- Test configuration
- Provider selection with dynamic form fields
- Status indicators for active configuration

**Supported Providers:**
- Local (GPT-2)
- Groq (llama2-70b, mixtral-8x7b)
- RunPod (custom)
- OpenAI (gpt-4, gpt-3.5)
- Anthropic (claude-3-opus, claude-3-sonnet)
- Azure OpenAI (gpt-4)
- Custom (any OpenAI-compatible endpoint)

---

## 12. Frontend Future Enhancements

### 12.1 Planned Features

**Real-Time Updates:**
- WebSocket integration for live updates
- Live typing indicators
- Real-time document processing status

**Advanced Features:**
- Message streaming
- Message edit/delete
- Conversation export
- Multi-language support
- Theme customization

**Performance:**
- Service Worker for offline support
- IndexedDB for local storage
- Progressive Web App (PWA)

---

**End of Part 5: Frontend Architecture**

Continue to Part 6: Deployment & Infrastructure
