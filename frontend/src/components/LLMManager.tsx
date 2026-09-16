import React, { useState, useEffect } from 'react'
import { Settings, Plus, Trash2, CheckCircle, XCircle, RefreshCw, X, Zap, Database, Globe, Cloud } from 'lucide-react'
import { useToast } from './ToastContainer'

interface LLMProvider {
  value: string
  name: string
  description: string
  requires_endpoint: boolean
  requires_api_key: boolean
  default_model: string
}

interface LLMConfiguration {
  id: number
  provider: string
  model_name: string
  endpoint: string | null
  api_key: string | null
  temperature: number
  max_tokens: number
  is_active: boolean
  created_at: string
  updated_at: string | null
}

interface LLMManagerProps {
  onClose: () => void
}

export function LLMManager({ onClose }: LLMManagerProps) {
  const [configurations, setConfigurations] = useState<LLMConfiguration[]>([])
  const [availableProviders, setAvailableProviders] = useState<LLMProvider[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddForm, setShowAddForm] = useState(false)
  const [selectedProvider, setSelectedProvider] = useState('')
  const [config, setConfig] = useState({
    model_name: '',
    endpoint: '',
    api_key: '',
    temperature: 0.7,
    max_tokens: 1000
  })
  const [testing, setTesting] = useState(false)
  const { success, error } = useToast()

  useEffect(() => {
    loadConfigurations()
    loadProviders()
  }, [])

  const loadConfigurations = async () => {
    try {
      const response = await fetch('/api/v1/llm/config')
      const data = await response.json()
      setConfigurations(data.configurations)
    } catch (err) {
      error('Failed to load LLM configurations')
    } finally {
      setLoading(false)
    }
  }

  const loadProviders = async () => {
    try {
      const response = await fetch('/api/v1/llm/providers')
      const data = await response.json()
      setAvailableProviders(data.providers)
    } catch (err) {
      error('Failed to load available providers')
    }
  }

  const handleCreateConfiguration = async () => {
    try {
      const response = await fetch('/api/v1/llm/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          provider: selectedProvider,
          model_name: config.model_name,
          endpoint: config.endpoint || null,
          api_key: config.api_key || null,
          temperature: config.temperature,
          max_tokens: config.max_tokens
        })
      })

      const data = await response.json()
      setConfigurations(prev => [data, ...prev])
      setShowAddForm(false)
      success('LLM configuration created successfully')
    } catch (err) {
      error('Failed to create LLM configuration')
    }
  }

  const handleActivateConfiguration = async (configId: number) => {
    try {
      const response = await fetch(`/api/v1/llm/config/${configId}/activate`, {
        method: 'POST'
      })

      const data = await response.json()
      setConfigurations(prev => prev.map(c => ({
        ...c,
        is_active: c.id === configId
      })))
      success('LLM configuration activated')
    } catch (err) {
      error('Failed to activate LLM configuration')
    }
  }

  const handleDeleteConfiguration = async (configId: number) => {
    try {
      await fetch(`/api/v1/llm/config/${configId}`, {
        method: 'DELETE'
      })
      setConfigurations(prev => prev.filter(c => c.id !== configId))
      success('LLM configuration deleted')
    } catch (err) {
      error('Failed to delete LLM configuration')
    }
  }

  const handleTestConfiguration = async () => {
    setTesting(true)
    try {
      const response = await fetch('/api/v1/llm/config/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          provider: selectedProvider,
          model_name: config.model_name,
          endpoint: config.endpoint || null,
          api_key: config.api_key || null
        })
      })

      const data = await response.json()
      if (data.success) {
        success('Configuration is valid')
      } else {
        error('Configuration test failed')
      }
    } catch (err) {
      error('Failed to test configuration')
    } finally {
      setTesting(false)
    }
  }

  const getProviderIcon = (provider: string) => {
    switch (provider) {
      case 'local':
        return <Database className="w-5 h-5" />
      case 'groq':
      case 'runpod':
      case 'openai':
      case 'anthropic':
      case 'azure':
        return <Cloud className="w-5 h-5" />
      case 'custom':
        return <Globe className="w-5 h-5" />
      default:
        return <Zap className="w-5 h-5" />
    }
  }

  const getStatusIcon = (isActive: boolean) => {
    return isActive ? (
      <CheckCircle className="w-5 h-5 text-green-400" />
    ) : (
      <XCircle className="w-5 h-5 text-gray-400" />
    )
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-800 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto border border-gray-700">
        {/* Modal Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-700">
          <div className="flex items-center gap-3">
            <Settings className="w-6 h-6 text-blue-400" />
            <h2 className="text-xl font-bold">LLM Configuration</h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Content */}
        <div className="p-6">
          {/* Header */}
          <div className="flex justify-between items-center mb-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-300">Configurations</h3>
              <p className="text-sm text-gray-400">Manage your LLM provider configurations</p>
            </div>
            <button
              onClick={() => setShowAddForm(true)}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Plus className="w-4 h-4" />
              Add Configuration
            </button>
          </div>

          {/* Configurations List */}
          {loading ? (
            <div className="text-center py-8 text-gray-400">
              <RefreshCw className="w-8 h-8 mx-auto mb-2 animate-spin" />
              <p>Loading configurations...</p>
            </div>
          ) : configurations.length === 0 ? (
            <div className="text-center py-8 text-gray-400">
              <Settings className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p>No LLM configurations found</p>
              <p className="text-sm mt-2">Add your first configuration to get started</p>
            </div>
          ) : (
            <div className="space-y-4">
              {configurations.map((configuration) => (
                <div
                  key={configuration.id}
                  className={`bg-gray-900 rounded-lg p-4 border ${
                    configuration.is_active ? 'border-green-500' : 'border-gray-700'
                  }`}
                >
                  <div className="flex justify-between items-start">
                    <div className="flex items-start gap-3">
                      {getProviderIcon(configuration.provider)}
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="font-semibold text-white capitalize">
                            {configuration.provider}
                          </h4>
                          {getStatusIcon(configuration.is_active)}
                          {configuration.is_active && (
                            <span className="text-xs px-2 py-1 bg-green-500/20 text-green-400 rounded">
                              Active
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-gray-400">
                          Model: {configuration.model_name}
                        </p>
                        {configuration.endpoint && (
                          <p className="text-sm text-gray-400">
                            Endpoint: {configuration.endpoint}
                          </p>
                        )}
                        <div className="flex gap-4 mt-2 text-xs text-gray-500">
                          <span>Temperature: {configuration.temperature}</span>
                          <span>Max Tokens: {configuration.max_tokens}</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      {!configuration.is_active && (
                        <button
                          onClick={() => handleActivateConfiguration(configuration.id)}
                          className="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
                        >
                          Activate
                        </button>
                      )}
                      <button
                        onClick={() => handleDeleteConfiguration(configuration.id)}
                        className="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Add Configuration Modal */}
        {showAddForm && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-gray-800 rounded-lg max-w-md w-full border border-gray-700">
              <div className="flex items-center justify-between p-6 border-b border-gray-700">
                <h3 className="text-lg font-semibold">Add LLM Configuration</h3>
                <button
                  onClick={() => setShowAddForm(false)}
                  className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              <div className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Provider</label>
                  <select
                    value={selectedProvider}
                    onChange={(e) => setSelectedProvider(e.target.value)}
                    className="w-full px-4 py-2 bg-gray-900 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                  >
                    <option value="">Select provider</option>
                    {availableProviders.map((provider) => (
                      <option key={provider.value} value={provider.value}>
                        {provider.name} - {provider.description}
                      </option>
                    ))}
                  </select>
                </div>

                {selectedProvider && (
                  <>
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">Model Name</label>
                      <input
                        type="text"
                        value={config.model_name}
                        onChange={(e) => setConfig({ ...config, model_name: e.target.value })}
                        placeholder={availableProviders.find(p => p.value === selectedProvider)?.default_model}
                        className="w-full px-4 py-2 bg-gray-900 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                      />
                    </div>

                    {availableProviders.find(p => p.value === selectedProvider)?.requires_endpoint && (
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">Endpoint URL</label>
                        <input
                          type="text"
                          value={config.endpoint}
                          onChange={(e) => setConfig({ ...config, endpoint: e.target.value })}
                          placeholder="https://api.example.com/v1"
                          className="w-full px-4 py-2 bg-gray-900 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                        />
                      </div>
                    )}

                    {availableProviders.find(p => p.value === selectedProvider)?.requires_api_key && (
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">API Key</label>
                        <input
                          type="password"
                          value={config.api_key}
                          onChange={(e) => setConfig({ ...config, api_key: e.target.value })}
                          placeholder="Enter your API key"
                          className="w-full px-4 py-2 bg-gray-900 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                        />
                      </div>
                    )}

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">Temperature</label>
                        <input
                          type="number"
                          value={config.temperature}
                          onChange={(e) => setConfig({ ...config, temperature: parseFloat(e.target.value) })}
                          min="0"
                          max="2"
                          step="0.1"
                          className="w-full px-4 py-2 bg-gray-900 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">Max Tokens</label>
                        <input
                          type="number"
                          value={config.max_tokens}
                          onChange={(e) => setConfig({ ...config, max_tokens: parseInt(e.target.value) })}
                          min="1"
                          max="8000"
                          className="w-full px-4 py-2 bg-gray-900 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                        />
                      </div>
                    </div>

                    <button
                      onClick={handleTestConfiguration}
                      disabled={testing}
                      className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                    >
                      {testing ? (
                        <>
                          <RefreshCw className="w-4 h-4 animate-spin" />
                          Testing...
                        </>
                      ) : (
                        'Test Configuration'
                      )}
                    </button>
                  </>
                )}

                <div className="flex gap-3">
                  <button
                    onClick={() => setShowAddForm(false)}
                    className="flex-1 px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleCreateConfiguration}
                    disabled={!selectedProvider}
                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                  >
                    Create
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default LLMManager
