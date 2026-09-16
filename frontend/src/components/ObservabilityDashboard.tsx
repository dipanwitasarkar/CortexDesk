import React, { useState, useEffect } from 'react'
import { Activity, Cpu, HardDrive, MemoryStick, AlertCircle, CheckCircle, RefreshCw, Database, Server, FileText, Zap, DatabaseZap } from 'lucide-react'

interface PerformanceData {
  timestamp: string
  cpu: {
    percent: number
    count: number
  }
  memory: {
    percent: number
    available: number
    total: number
    used: number
  }
  disk: {
    percent: number
    free: number
    total: number
    used: number
  }
}

interface ErrorData {
  errors: any[]
  count: number
  timestamp: string
}

interface HealthData {
  status: string
  timestamp: string
  components: {
    logging: string
    metrics: string
    tracing: string
    performance_monitoring: string
    error_tracking: string
  }
}

interface LogsData {
  logs: any[]
  count: number
  timestamp: string
}

interface TracesData {
  traces: any[]
  count: number
  timestamp: string
}

interface DatabaseData {
  table_stats: Record<string, number>
  recent_chats: any[]
  recent_messages: any[]
  recent_executions: any[]
  timestamp: string
}

interface RedisData {
  redis_info: {
    used_memory: string
    connected_clients: number
    total_keys: number
    uptime_in_seconds: number
  }
  key_categories: Record<string, number>
  sample_data: Record<string, any>
  timestamp: string
}

interface QdrantData {
  collections: {
    name: string
    points_count: number
    indexed_vectors_count: number
    status: string
  }[]
  timestamp: string
}

type TabType = 'overview' | 'logs' | 'traces' | 'database' | 'runtime-state' | 'qdrant'

const ObservabilityDashboard: React.FC = () => {
  const [performance, setPerformance] = useState<PerformanceData | null>(null)
  const [errors, setErrors] = useState<ErrorData | null>(null)
  const [health, setHealth] = useState<HealthData | null>(null)
  const [logs, setLogs] = useState<LogsData | null>(null)
  const [traces, setTraces] = useState<TracesData | null>(null)
  const [database, setDatabase] = useState<DatabaseData | null>(null)
  const [redis, setRedis] = useState<RedisData | null>(null)
  const [runtimeState, setRuntimeState] = useState<any>(null)
  const [qdrant, setQdrant] = useState<QdrantData | null>(null)
  const [loading, setLoading] = useState(true)
  const [lastUpdated, setLastUpdated] = useState<string>('')
  const [activeTab, setActiveTab] = useState<TabType>('overview')

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  const fetchData = async () => {
    setLoading(true)
    try {
      const [perfRes, errorRes, healthRes, logsRes, tracesRes, dbRes, runtimeStateRes, qdrantRes] = await Promise.all([
        fetch('/api/v1/observability/performance'),
        fetch('/api/v1/observability/errors'),
        fetch('/api/v1/observability/health'),
        fetch('/api/v1/observability/logs'),
        fetch('/api/v1/observability/traces'),
        fetch('/api/v1/observability/database'),
        fetch('/api/v1/observability/runtime-state'),
        fetch('http://localhost:6333/collections')
      ])

      const perfData = await perfRes.json()
      const errorData = await errorRes.json()
      const healthData = await healthRes.json()
      const logsData = await logsRes.json()
      const tracesData = await tracesRes.json()
      const dbData = await dbRes.json()
      const runtimeStateData = await runtimeStateRes.json()
      const qdrantData = await qdrantRes.json()

      setPerformance(perfData)
      setErrors(errorData)
      setHealth(healthData)
      setLogs(logsData)
      setTraces(tracesData)
      setDatabase(dbData)
      setRuntimeState(runtimeStateData)
      
      // Process Qdrant data
      if (qdrantData.result && qdrantData.result.collections) {
        const collections = await Promise.all(
          qdrantData.result.collections.map(async (collection: any) => {
            const detailRes = await fetch(`http://localhost:6333/collections/${collection.name}`)
            const detailData = await detailRes.json()
            return {
              name: collection.name,
              points_count: detailData.result.points_count,
              indexed_vectors_count: detailData.result.indexed_vectors_count,
              status: detailData.result.status
            }
          })
        )
        setQdrant({
          collections,
          timestamp: new Date().toISOString()
        })
      }
      
      setLastUpdated(new Date().toLocaleTimeString())
    } catch (error) {
      console.error('Failed to fetch observability data:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 30000) // Refresh every 30 seconds
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Activity className="w-6 h-6 text-blue-400" />
          <h1 className="text-2xl font-bold">System Observability</h1>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-400">
            Last updated: {lastUpdated || 'Never'}
          </span>
          <button
            onClick={fetchData}
            disabled={loading}
            className="p-2 hover:bg-gray-700 rounded-lg transition-colors disabled:opacity-50"
            title="Refresh"
          >
            <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-gray-700 pb-4">
        {[
          { id: 'overview', label: 'Overview', icon: Activity },
          { id: 'logs', label: 'Logs', icon: FileText },
          { id: 'traces', label: 'Traces', icon: Zap },
          { id: 'database', label: 'Database', icon: Database },
          { id: 'runtime-state', label: 'Runtime State', icon: Server },
          { id: 'qdrant', label: 'Qdrant', icon: DatabaseZap }
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as TabType)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
              activeTab === tab.id
                ? 'bg-blue-600 text-white'
                : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
            }`}
          >
            <tab.icon className="w-4 h-4" />
            <span className="text-sm">{tab.label}</span>
          </button>
        ))}
      </div>

      {loading && !performance ? (
        <div className="text-center py-12">
          <RefreshCw className="w-8 h-8 mx-auto mb-4 animate-spin text-blue-400" />
          <p className="text-gray-400">Loading observability data...</p>
        </div>
      ) : (
        <>
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <>
              {/* Health Status */}
              {health && (
                <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                  <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <CheckCircle className="w-5 h-5 text-green-400" />
                    System Health
                  </h2>
                  <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                    {Object.entries(health.components).map(([key, value]) => (
                      <div key={key} className="flex items-center gap-2">
                        <div className={`w-2 h-2 rounded-full ${value === 'active' ? 'bg-green-400' : 'bg-red-400'}`} />
                        <span className="text-sm capitalize text-gray-300">{key.replace('_', ' ')}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Performance Metrics */}
              {performance && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {/* CPU */}
                  <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                    <div className="flex items-center gap-3 mb-4">
                      <Cpu className="w-5 h-5 text-blue-400" />
                      <h3 className="font-semibold">CPU Usage</h3>
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-400">Usage</span>
                        <span className="font-mono">{performance.cpu.percent.toFixed(1)}%</span>
                      </div>
                      <div className="w-full bg-gray-700 rounded-full h-2">
                        <div
                          className="bg-blue-500 h-2 rounded-full transition-all"
                          style={{ width: `${performance.cpu.percent}%` }}
                        />
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-400">Cores</span>
                        <span className="font-mono">{performance.cpu.count}</span>
                      </div>
                    </div>
                  </div>

                  {/* Memory */}
                  <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                    <div className="flex items-center gap-3 mb-4">
                      <MemoryStick className="w-5 h-5 text-purple-400" />
                      <h3 className="font-semibold">Memory Usage</h3>
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-400">Usage</span>
                        <span className="font-mono">{performance.memory.percent.toFixed(1)}%</span>
                      </div>
                      <div className="w-full bg-gray-700 rounded-full h-2">
                        <div
                          className="bg-purple-500 h-2 rounded-full transition-all"
                          style={{ width: `${performance.memory.percent}%` }}
                        />
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-400">Used</span>
                        <span className="font-mono">{formatBytes(performance.memory.used)}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-400">Available</span>
                        <span className="font-mono">{formatBytes(performance.memory.available)}</span>
                      </div>
                    </div>
                  </div>

                  {/* Disk */}
                  <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                    <div className="flex items-center gap-3 mb-4">
                      <HardDrive className="w-5 h-5 text-green-400" />
                      <h3 className="font-semibold">Disk Usage</h3>
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-400">Usage</span>
                        <span className="font-mono">{performance.disk.percent.toFixed(1)}%</span>
                      </div>
                      <div className="w-full bg-gray-700 rounded-full h-2">
                        <div
                          className="bg-green-500 h-2 rounded-full transition-all"
                          style={{ width: `${performance.disk.percent}%` }}
                        />
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-400">Used</span>
                        <span className="font-mono">{formatBytes(performance.disk.used)}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-400">Free</span>
                        <span className="font-mono">{formatBytes(performance.disk.free)}</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Errors */}
              {errors && (
                <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                  <div className="flex items-center gap-3 mb-4">
                    <AlertCircle className="w-5 h-5 text-red-400" />
                    <h2 className="text-lg font-semibold">Recent Errors</h2>
                    <span className="text-sm text-gray-400">({errors.count} errors)</span>
                  </div>
                  {errors.count > 0 ? (
                    <div className="space-y-2 max-h-64 overflow-y-auto">
                      {errors.errors.map((error: any, index: number) => (
                        <div key={index} className="bg-gray-900 rounded p-3 text-sm">
                          <div className="font-mono text-red-400 mb-1">{error.message || 'Unknown error'}</div>
                          <div className="text-gray-400 text-xs">{error.timestamp || 'No timestamp'}</div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-gray-400">
                      <CheckCircle className="w-8 h-8 mx-auto mb-2 text-green-400" />
                      <p>No recent errors</p>
                    </div>
                  )}
                </div>
              )}
            </>
          )}

          {/* Logs Tab */}
          {activeTab === 'logs' && (
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <div className="flex items-center gap-3 mb-4">
                <FileText className="w-5 h-5 text-blue-400" />
                <h2 className="text-lg font-semibold">System Logs</h2>
                <span className="text-sm text-gray-400">({logs?.count || 0} logs)</span>
              </div>
              {logs && logs.count > 0 ? (
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {logs.logs.map((log: any, index: number) => (
                    <div key={index} className="bg-gray-900 rounded p-3 text-sm font-mono">
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`text-xs px-2 py-1 rounded ${
                          log.level === 'ERROR' ? 'bg-red-500/20 text-red-400' :
                          log.level === 'WARNING' ? 'bg-yellow-500/20 text-yellow-400' :
                          log.level === 'INFO' ? 'bg-blue-500/20 text-blue-400' :
                          'bg-gray-500/20 text-gray-400'
                        }`}>
                          {log.level}
                        </span>
                        <span className="text-gray-400 text-xs">{log.timestamp}</span>
                      </div>
                      <div className="text-gray-300">{log.message}</div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-400">
                  <FileText className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <p>No logs available</p>
                </div>
              )}
            </div>
          )}

          {/* Traces Tab */}
          {activeTab === 'traces' && (
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <div className="flex items-center gap-3 mb-4">
                <Zap className="w-5 h-5 text-yellow-400" />
                <h2 className="text-lg font-semibold">Request Traces</h2>
                <span className="text-sm text-gray-400">({traces?.count || 0} traces)</span>
              </div>
              {traces && traces.count > 0 ? (
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {traces.traces.map((trace: any, index: number) => (
                    <div key={index} className="bg-gray-900 rounded p-3 text-sm">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-gray-400 text-xs">{trace.timestamp}</span>
                        <span className="text-blue-400">{trace.operation}</span>
                      </div>
                      <div className="text-gray-300">Request ID: {trace.request_id}</div>
                      {trace.duration && (
                        <div className="text-gray-400 text-xs">Duration: {trace.duration.toFixed(3)}s</div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-400">
                  <Zap className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <p>No traces available</p>
                </div>
              )}
            </div>
          )}

          {/* Database Tab */}
          {activeTab === 'database' && (
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <div className="flex items-center gap-3 mb-4">
                <Database className="w-5 h-5 text-green-400" />
                <h2 className="text-lg font-semibold">Database Statistics</h2>
              </div>
              {database && (
                <div className="space-y-6">
                  {/* Table Stats */}
                  <div>
                    <h3 className="text-md font-semibold mb-3 text-gray-300">Table Row Counts</h3>
                    <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                      {Object.entries(database.table_stats).map(([table, count]) => (
                        <div key={table} className="bg-gray-900 rounded p-3">
                          <div className="text-2xl font-bold text-blue-400">{count}</div>
                          <div className="text-sm text-gray-400 capitalize">{table}</div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Recent Chats */}
                  <div>
                    <h3 className="text-md font-semibold mb-3 text-gray-300">Recent Chats</h3>
                    <div className="space-y-2 max-h-48 overflow-y-auto">
                      {database.recent_chats.map((chat: any, index: number) => (
                        <div key={index} className="bg-gray-900 rounded p-3 text-sm">
                          <div className="flex justify-between">
                            <span className="text-gray-300">ID: {chat.id}</span>
                            <span className="text-gray-400 text-xs">{chat.created_at}</span>
                          </div>
                          <div className="text-gray-300">{chat.title}</div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Recent Messages */}
                  <div>
                    <h3 className="text-md font-semibold mb-3 text-gray-300">Recent Messages</h3>
                    <div className="space-y-2 max-h-48 overflow-y-auto">
                      {database.recent_messages.map((msg: any, index: number) => (
                        <div key={index} className="bg-gray-900 rounded p-3 text-sm">
                          <div className="flex justify-between">
                            <span className="text-blue-400">{msg.role}</span>
                            <span className="text-gray-400 text-xs">{msg.created_at}</span>
                          </div>
                          <div className="text-gray-300">{msg.content}</div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Recent Executions */}
                  <div>
                    <h3 className="text-md font-semibold mb-3 text-gray-300">Recent Agent Executions</h3>
                    <div className="space-y-2 max-h-48 overflow-y-auto">
                      {database.recent_executions.map((exec: any, index: number) => (
                        <div key={index} className="bg-gray-900 rounded p-3 text-sm">
                          <div className="flex justify-between">
                            <span className="text-purple-400">{exec.agent_name}</span>
                            <span className={`text-xs ${exec.status === 'completed' ? 'text-green-400' : 'text-red-400'}`}>
                              {exec.status}
                            </span>
                          </div>
                          <div className="text-gray-400 text-xs">
                            Duration: {exec.execution_time?.toFixed(2)}s | Chat: {exec.chat_id}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Runtime State Tab */}
          {activeTab === 'runtime-state' && (
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <div className="flex items-center gap-3 mb-4">
                <Server className="w-5 h-5 text-red-400" />
                <h2 className="text-lg font-semibold">Runtime State (Redis)</h2>
              </div>
              {runtimeState && (
                <div className="space-y-6">
                  {/* Key Categories */}
                  <div>
                    <h3 className="text-md font-semibold mb-3 text-gray-300">State Categories</h3>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                      {Object.entries(runtimeState.key_categories).map(([category, count]) => (
                        <div key={category} className="bg-gray-900 rounded p-3">
                          <div className="text-2xl font-bold text-blue-400">{count}</div>
                          <div className="text-sm text-gray-400 capitalize">{category.replace('_', ' ')}</div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Sample Data */}
                  <div>
                    <h3 className="text-md font-semibold mb-3 text-gray-300">Sample State Data</h3>
                    <div className="space-y-2 max-h-64 overflow-y-auto">
                      {Object.entries(runtimeState.sample_data).map(([category, data]) => (
                        <div key={category} className="bg-gray-900 rounded p-3 text-sm">
                          <div className="flex justify-between mb-1">
                            <span className="text-gray-300 capitalize">{category.replace('_', ' ')}</span>
                            <span className="text-gray-400 text-xs">{data.total_keys} keys</span>
                          </div>
                          <div className="text-gray-400 text-xs font-mono break-all">
                            {data.key}
                          </div>
                          <div className="text-gray-300 text-xs mt-1">
                            {typeof data.value === 'object' ? JSON.stringify(data.value, null, 2) : String(data.value)}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Description */}
                  <div>
                    <h3 className="text-md font-semibold mb-3 text-gray-300">What This Stores</h3>
                    <div className="bg-gray-900 rounded p-4 text-sm text-gray-300">
                      <ul className="space-y-2">
                        <li className="flex items-start gap-2">
                          <span className="text-blue-400">•</span>
                          <span><strong>Conversation:</strong> Recent messages buffer (last 50 messages)</span>
                        </li>
                        <li className="flex items-start gap-2">
                          <span className="text-green-400">•</span>
                          <span><strong>Agent State:</strong> Current agent status and progress</span>
                        </li>
                        <li className="flex items-start gap-2">
                          <span className="text-purple-400">•</span>
                          <span><strong>Response Cache:</strong> Cached LLM responses (1 hour TTL)</span>
                        </li>
                        <li className="flex items-start gap-2">
                          <span className="text-yellow-400">•</span>
                          <span><strong>Tool Cache:</strong> Cached tool results (5-15 min TTL)</span>
                        </li>
                        <li className="flex items-start gap-2">
                          <span className="text-pink-400">•</span>
                          <span><strong>Screenshot Cache:</strong> Cached screenshots (24h TTL)</span>
                        </li>
                        <li className="flex items-start gap-2">
                          <span className="text-red-400">•</span>
                          <span><strong>Workflow:</strong> Long-running workflow progress</span>
                        </li>
                        <li className="flex items-start gap-2">
                          <span className="text-orange-400">•</span>
                          <span><strong>Memory Queue:</strong> Pending memory extraction tasks</span>
                        </li>
                      </ul>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Qdrant Tab */}
          {activeTab === 'qdrant' && (
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <div className="flex items-center gap-3 mb-4">
                <DatabaseZap className="w-5 h-5 text-purple-400" />
                <h2 className="text-lg font-semibold">Qdrant Vector Database</h2>
              </div>
              {qdrant && (
                <div className="space-y-6">
                  {/* Collections Overview */}
                  <div>
                    <h3 className="text-md font-semibold mb-3 text-gray-300">Collections</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {qdrant.collections.map((collection) => (
                        <div key={collection.name} className="bg-gray-900 rounded p-4">
                          <div className="flex items-center justify-between mb-3">
                            <h4 className="font-semibold text-blue-400">{collection.name}</h4>
                            <span className={`px-2 py-1 rounded text-xs ${
                              collection.status === 'green' ? 'bg-green-900 text-green-300' : 'bg-red-900 text-red-300'
                            }`}>
                              {collection.status}
                            </span>
                          </div>
                          <div className="space-y-2">
                            <div className="flex justify-between">
                              <span className="text-gray-400">Points:</span>
                              <span className="text-white font-semibold">{collection.points_count}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-400">Indexed Vectors:</span>
                              <span className="text-white font-semibold">{collection.indexed_vectors_count}</span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Description */}
                  <div>
                    <h3 className="text-md font-semibold mb-3 text-gray-300">What This Stores</h3>
                    <div className="bg-gray-900 rounded p-4 text-sm text-gray-300">
                      <ul className="space-y-2">
                        <li className="flex items-start gap-2">
                          <span className="text-blue-400">•</span>
                          <span><strong>Documents:</strong> Document embeddings for RAG (384-dimensional vectors)</span>
                        </li>
                        <li className="flex items-start gap-2">
                          <span className="text-green-400">•</span>
                          <span><strong>AI Assistant Memory:</strong> Long-term memory embeddings</span>
                        </li>
                        <li className="flex items-start gap-2">
                          <span className="text-purple-400">•</span>
                          <span><strong>Vector Size:</strong> 384 dimensions (sentence-transformers/all-MiniLM-L6-v2)</span>
                        </li>
                        <li className="flex items-start gap-2">
                          <span className="text-yellow-400">•</span>
                          <span><strong>Distance Metric:</strong> Cosine similarity</span>
                        </li>
                        <li className="flex items-start gap-2">
                          <span className="text-pink-400">•</span>
                          <span><strong>Purpose:</strong> Semantic search and RAG retrieval</span>
                        </li>
                      </ul>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default ObservabilityDashboard