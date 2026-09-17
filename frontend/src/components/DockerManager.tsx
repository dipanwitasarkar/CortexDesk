import { useState, useEffect } from 'react'
import { CheckCircle, XCircle, Loader2, Play, Square, RefreshCw } from 'lucide-react'
import { invoke } from '@tauri-apps/api/core'

interface DockerManagerProps {
  onBackendReady: () => void
}

export default function DockerManager({ onBackendReady }: DockerManagerProps) {
  const [dockerInstalled, setDockerInstalled] = useState<boolean | null>(null)
  const [containersRunning, setContainersRunning] = useState(false)
  const [containersStatus, setContainersStatus] = useState('')
  const [loading, setLoading] = useState(true)
  const [starting, setStarting] = useState(false)
  const [stopping, setStopping] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    checkDockerStatus()
    const interval = setInterval(checkContainersStatus, 5000)
    return () => clearInterval(interval)
  }, [])

  const checkDockerStatus = async () => {
    try {
      const installed = await invoke<boolean>('check_docker')
      setDockerInstalled(installed)
      
      if (installed) {
        await checkContainersStatus()
      }
    } catch (err) {
      setError('Failed to check Docker status')
      setDockerInstalled(false)
    } finally {
      setLoading(false)
    }
  }

  const checkContainersStatus = async () => {
    try {
      const status = await invoke<string>('check_containers_status')
      setContainersStatus(status)
      
      // Check if all containers are running
      const hasPostgres = status.includes('cortexdesk-postgres') && status.includes('Up')
      const hasRedis = status.includes('cortexdesk-redis') && status.includes('Up')
      const hasQdrant = status.includes('cortexdesk-qdrant') && status.includes('Up')
      const hasBackend = status.includes('cortexdesk-backend') && status.includes('Up')
      
      const allRunning = hasPostgres && hasRedis && hasQdrant && hasBackend
      setContainersRunning(allRunning)
      
      if (allRunning) {
        onBackendReady()
      }
    } catch (err) {
      setContainersRunning(false)
    }
  }

  const startContainers = async () => {
    setStarting(true)
    setError('')
    try {
      const result = await invoke<string>('start_docker_containers')
      console.log('Containers started:', result)
      
      // Wait for containers to be ready
      setTimeout(async () => {
        await checkContainersStatus()
        setStarting(false)
      }, 5000)
    } catch (err) {
      setError('Failed to start containers: ' + err)
      setStarting(false)
    }
  }

  const stopContainers = async () => {
    setStopping(true)
    setError('')
    try {
      const result = await invoke<string>('stop_docker_containers')
      console.log('Containers stopped:', result)
      await checkContainersStatus()
      setStopping(false)
    } catch (err) {
      setError('Failed to stop containers: ' + err)
      setStopping(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="animate-spin text-blue-500" size={32} />
      </div>
    )
  }

  if (!dockerInstalled) {
    return (
      <div className="p-6 bg-red-50 border border-red-200 rounded-lg">
        <div className="flex items-center gap-3 mb-4">
          <XCircle className="text-red-500" size={24} />
          <h3 className="text-lg font-semibold text-red-900">Docker Not Installed</h3>
        </div>
        <p className="text-red-700 mb-4">
          CortexDesk requires Docker Desktop to run the backend services.
        </p>
        <a
          href="https://www.docker.com/products/docker-desktop"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
        >
          Download Docker Desktop
        </a>
      </div>
    )
  }

  return (
    <div className="p-6 bg-gray-50 border border-gray-200 rounded-lg">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          {containersRunning ? (
            <CheckCircle className="text-green-500" size={24} />
          ) : (
            <XCircle className="text-red-500" size={24} />
          )}
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              Backend Services
            </h3>
            <p className="text-sm text-gray-600">
              {containersRunning ? 'All services running' : 'Services not running'}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={checkContainersStatus}
            className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded-lg transition-colors"
            title="Refresh status"
          >
            <RefreshCw size={20} />
          </button>
          {!containersRunning && (
            <button
              onClick={startContainers}
              disabled={starting}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {starting ? (
                <>
                  <Loader2 className="animate-spin" size={16} />
                  Starting...
                </>
              ) : (
                <>
                  <Play size={16} />
                  Start Services
                </>
              )}
            </button>
          )}
          {containersRunning && (
            <button
              onClick={stopContainers}
              disabled={stopping}
              className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {stopping ? (
                <>
                  <Loader2 className="animate-spin" size={16} />
                  Stopping...
                </>
              ) : (
                <>
                  <Square size={16} />
                  Stop Services
                </>
              )}
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}

      {containersStatus && (
        <div className="mt-4 p-3 bg-gray-100 rounded-lg">
          <pre className="text-xs text-gray-700 whitespace-pre-wrap font-mono">
            {containersStatus}
          </pre>
        </div>
      )}

      <div className="mt-4 text-sm text-gray-600">
        <p className="font-medium mb-2">Services:</p>
        <ul className="space-y-1">
          <li className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${containersStatus.includes('cortexdesk-postgres') && containersStatus.includes('Up') ? 'bg-green-500' : 'bg-red-500'}`} />
            PostgreSQL (Database)
          </li>
          <li className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${containersStatus.includes('cortexdesk-redis') && containersStatus.includes('Up') ? 'bg-green-500' : 'bg-red-500'}`} />
            Redis (Cache)
          </li>
          <li className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${containersStatus.includes('cortexdesk-qdrant') && containersStatus.includes('Up') ? 'bg-green-500' : 'bg-red-500'}`} />
            Qdrant (Vector Database)
          </li>
          <li className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${containersStatus.includes('cortexdesk-backend') && containersStatus.includes('Up') ? 'bg-green-500' : 'bg-red-500'}`} />
            Backend (API)
          </li>
        </ul>
      </div>
    </div>
  )
}