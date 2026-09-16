import React, { useState, useEffect } from 'react'
import { Plus, Trash2, Edit, RefreshCw, CheckCircle, XCircle, Settings, Plug } from 'lucide-react'
import { useToast } from './ToastContainer'

interface MCPIntegration {
  id: number
  name: string
  type: string
  config: Record<string, any>
  enabled: boolean
  status: string
  last_connected: string | null
  last_error: string | null
  description: string | null
  created_at: string
  updated_at: string | null
}

interface MCPType {
  type: string
  name: string
  description: string
  required_config: string[]
  optional_config: string[]
}

const MCPManager: React.FC = () => {
  const [integrations, setIntegrations] = useState<MCPIntegration[]>([])
  const [availableTypes, setAvailableTypes] = useState<MCPType[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editingIntegration, setEditingIntegration] = useState<MCPIntegration | null>(null)
  const [formData, setFormData] = useState({
    name: '',
    type: '',
    config: {} as Record<string, any>,
    description: ''
  })
  const { success, error, info, warning } = useToast()

  const fetchIntegrations = async () => {
    try {
      const response = await fetch('/api/v1/mcp/integrations')
      if (response.ok) {
        const data = await response.json()
        setIntegrations(data)
      } else {
        error('Failed to fetch integrations')
      }
    } catch (err) {
      console.error('Failed to fetch integrations:', err)
      error('Failed to fetch integrations')
    }
  }

  const fetchAvailableTypes = async () => {
    try {
      const response = await fetch('/api/v1/mcp/types')
      if (response.ok) {
        const data = await response.json()
        setAvailableTypes(data)
      } else {
        error('Failed to fetch available MCP types')
      }
    } catch (err) {
      console.error('Failed to fetch available types:', err)
      error('Failed to fetch available MCP types')
    }
  }

  useEffect(() => {
    fetchIntegrations()
    fetchAvailableTypes()
    setLoading(false)
  }, [])

  const handleCreate = async () => {
    if (!formData.name || !formData.type) {
      error('Please provide name and type')
      return
    }

    try {
      const response = await fetch('/api/v1/mcp/integrations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      })
      
      if (response.ok) {
        success('MCP integration created successfully')
        await fetchIntegrations()
        setShowModal(false)
        resetForm()
      } else {
        error('Failed to create MCP integration')
      }
    } catch (err) {
      console.error('Failed to create integration:', err)
      error('Failed to create MCP integration')
    }
  }

  const handleUpdate = async () => {
    if (!editingIntegration) return
    
    try {
      const response = await fetch(`/api/v1/mcp/integrations/${editingIntegration.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      })
      
      if (response.ok) {
        success('MCP integration updated successfully')
        await fetchIntegrations()
        setShowModal(false)
        resetForm()
        setEditingIntegration(null)
      } else {
        error('Failed to update MCP integration')
      }
    } catch (err) {
      console.error('Failed to update integration:', err)
      error('Failed to update MCP integration')
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this integration?')) return
    
    try {
      const response = await fetch(`/api/v1/mcp/integrations/${id}`, {
        method: 'DELETE'
      })
      
      if (response.ok) {
        success('MCP integration deleted successfully')
        await fetchIntegrations()
      } else {
        error('Failed to delete MCP integration')
      }
    } catch (err) {
      console.error('Failed to delete integration:', err)
      error('Failed to delete MCP integration')
    }
  }

  const handleTest = async (id: number) => {
    try {
      const response = await fetch(`/api/v1/mcp/integrations/${id}/test`, {
        method: 'POST'
      })
      const result = await response.json()
      
      if (result.success) {
        success('Connection test successful!')
        await fetchIntegrations()
      } else {
        error(`Connection test failed: ${result.error}`)
      }
    } catch (err) {
      console.error('Failed to test connection:', err)
      error('Connection test failed')
    }
  }

  const handleEdit = (integration: MCPIntegration) => {
    setEditingIntegration(integration)
    setFormData({
      name: integration.name,
      type: integration.type,
      config: integration.config,
      description: integration.description || ''
    })
    setShowModal(true)
  }

  const resetForm = () => {
    setFormData({
      name: '',
      type: '',
      config: {} as Record<string, any>,
      description: ''
    })
    setEditingIntegration(null)
  }

  const handleTypeChange = (type: string) => {
    setFormData({
      ...formData,
      type,
      config: {} // Reset config when type changes
    })
  }

  const handleConfigChange = (key: string, value: string) => {
    setFormData({
      ...formData,
      config: {
        ...formData.config,
        [key]: value
      }
    })
  }

  const selectedType = availableTypes.find(t => t.type === formData.type)

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-400" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Plug className="w-6 h-6 text-purple-400" />
          <h2 className="text-xl font-semibold">MCP Integrations</h2>
        </div>
        <button
          onClick={() => { resetForm(); setShowModal(true) }}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span>Add Integration</span>
        </button>
      </div>

      {/* Integrations List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {integrations.map((integration) => (
          <div key={integration.id} className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1">
                <h3 className="font-semibold text-white">{integration.name}</h3>
                <p className="text-sm text-gray-400 capitalize">{integration.type}</p>
              </div>
              <div className="flex items-center gap-2">
                {integration.status === 'connected' ? (
                  <CheckCircle className="w-5 h-5 text-green-400" />
                ) : (
                  <XCircle className="w-5 h-5 text-red-400" />
                )}
              </div>
            </div>
            
            {integration.description && (
              <p className="text-sm text-gray-300 mb-3">{integration.description}</p>
            )}
            
            <div className="flex items-center justify-between text-xs text-gray-400 mb-3">
              <span>{integration.enabled ? 'Enabled' : 'Disabled'}</span>
              {integration.last_connected && (
                <span>Last: {new Date(integration.last_connected).toLocaleDateString()}</span>
              )}
            </div>
            
            {integration.last_error && (
              <div className="text-xs text-red-400 mb-3 truncate">
                Error: {integration.last_error}
              </div>
            )}
            
            <div className="flex items-center gap-2">
              <button
                onClick={() => handleTest(integration.id)}
                className="flex-1 flex items-center justify-center gap-1 px-3 py-2 bg-gray-700 text-white rounded hover:bg-gray-600 transition-colors text-sm"
              >
                <RefreshCw className="w-3 h-3" />
                Test
              </button>
              <button
                onClick={() => handleEdit(integration)}
                className="flex-1 flex items-center justify-center gap-1 px-3 py-2 bg-gray-700 text-white rounded hover:bg-gray-600 transition-colors text-sm"
              >
                <Edit className="w-3 h-3" />
                Edit
              </button>
              <button
                onClick={() => handleDelete(integration.id)}
                className="flex-1 flex items-center justify-center gap-1 px-3 py-2 bg-red-900 text-white rounded hover:bg-red-800 transition-colors text-sm"
              >
                <Trash2 className="w-3 h-3" />
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>

      {integrations.length === 0 && (
        <div className="text-center py-12 text-gray-400">
          <Plug className="w-12 h-12 mx-auto mb-4 text-gray-600" />
          <p>No MCP integrations configured</p>
          <p className="text-sm">Click "Add Integration" to get started</p>
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-800 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-gray-700">
            <div className="flex items-center justify-between p-6 border-b border-gray-700">
              <h3 className="text-xl font-bold">
                {editingIntegration ? 'Edit Integration' : 'Add Integration'}
              </h3>
              <button
                onClick={() => { setShowModal(false); resetForm() }}
                className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
              >
                <XCircle className="w-5 h-5" />
              </button>
            </div>
            
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white"
                  placeholder="Integration name"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Type</label>
                <select
                  value={formData.type}
                  onChange={(e) => handleTypeChange(e.target.value)}
                  className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white"
                >
                  <option value="">Select type...</option>
                  {availableTypes.map((type) => (
                    <option key={type.type} value={type.type}>{type.name}</option>
                  ))}
                </select>
              </div>
              
              {selectedType && (
                <div className="bg-gray-900 rounded-lg p-4">
                  <h4 className="font-semibold text-sm text-gray-300 mb-3">Configuration</h4>
                  <p className="text-xs text-gray-400 mb-3">{selectedType.description}</p>
                  
                  {selectedType.required_config.map((key) => (
                    <div key={key} className="mb-3">
                      <label className="block text-sm font-medium text-gray-300 mb-1">
                        {key} <span className="text-red-400">*</span>
                      </label>
                      <input
                        type="text"
                        value={formData.config[key] || ''}
                        onChange={(e) => handleConfigChange(key, e.target.value)}
                        className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white"
                        placeholder={`Enter ${key}`}
                      />
                    </div>
                  ))}
                  
                  {selectedType.optional_config.map((key) => (
                    <div key={key} className="mb-3">
                      <label className="block text-sm font-medium text-gray-300 mb-1">
                        {key} <span className="text-gray-500">(optional)</span>
                      </label>
                      <input
                        type="text"
                        value={formData.config[key] || ''}
                        onChange={(e) => handleConfigChange(key, e.target.value)}
                        className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white"
                        placeholder={`Enter ${key}`}
                      />
                    </div>
                  ))}
                </div>
              )}
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white"
                  rows={3}
                  placeholder="Integration description (optional)"
                />
              </div>
            </div>
            
            <div className="flex justify-end gap-3 p-6 border-t border-gray-700">
              <button
                onClick={() => { setShowModal(false); resetForm() }}
                className="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={editingIntegration ? handleUpdate : handleCreate}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                {editingIntegration ? 'Update' : 'Create'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default MCPManager