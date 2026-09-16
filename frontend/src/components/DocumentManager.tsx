import React, { useState, useEffect } from 'react'
import { FileText, Upload, Trash2, Search, Plus, X, CheckCircle, AlertCircle, Clock } from 'lucide-react'

interface Document {
  id: number
  user_id: number
  title: string
  file_type: string
  content: string
  file_path: string | null
  chunk_count: number
  embedding_status: string
  meta_data: any
  created_at: string
  updated_at: string
}

const DocumentManager: React.FC = () => {
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [showUpload, setShowUpload] = useState(false)
  const [uploadTitle, setUploadTitle] = useState('')
  const [uploadContent, setUploadContent] = useState('')
  const [uploading, setUploading] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<any[]>([])
  const [searching, setSearching] = useState(false)

  const fetchDocuments = async () => {
    try {
      const response = await fetch('/api/v1/documents')
      if (response.ok) {
        const data = await response.json()
        setDocuments(data)
      }
    } catch (error) {
      console.error('Failed to fetch documents:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDocuments()
  }, [])

  const handleUpload = async () => {
    if (!uploadTitle || !uploadContent) return

    setUploading(true)
    try {
      const response = await fetch(
        `/api/v1/documents/text?title=${encodeURIComponent(uploadTitle)}&content=${encodeURIComponent(uploadContent)}`
      )
      if (response.ok) {
        const data = await response.json()
        console.log('Document uploaded:', data)
        setShowUpload(false)
        setUploadTitle('')
        setUploadContent('')
        fetchDocuments()
      }
    } catch (error) {
      console.error('Failed to upload document:', error)
    } finally {
      setUploading(false)
    }
  }

  const handleDelete = async (documentId: number) => {
    if (!confirm('Are you sure you want to delete this document?')) return

    try {
      const response = await fetch(`/api/v1/documents/${documentId}`, {
        method: 'DELETE'
      })
      if (response.ok) {
        fetchDocuments()
      }
    } catch (error) {
      console.error('Failed to delete document:', error)
    }
  }

  const handleSearch = async () => {
    if (!searchQuery.trim()) return

    setSearching(true)
    try {
      const response = await fetch(
        `/api/v1/documents/search?query=${encodeURIComponent(searchQuery)}`
      )
      if (response.ok) {
        const data = await response.json()
        setSearchResults(data.results || [])
      }
    } catch (error) {
      console.error('Failed to search documents:', error)
    } finally {
      setSearching(false)
    }
  }

  const getEmbeddingStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-400" />
      case 'completed_no_embeddings':
        return <Clock className="w-4 h-4 text-yellow-400" />
      case 'processing':
        return <Clock className="w-4 h-4 text-blue-400 animate-spin" />
      case 'failed':
        return <AlertCircle className="w-4 h-4 text-red-400" />
      default:
        return <Clock className="w-4 h-4 text-gray-400" />
    }
  }

  const getEmbeddingStatusText = (status: string) => {
    switch (status) {
      case 'completed':
        return 'Embedded'
      case 'completed_no_embeddings':
        return 'No Embeddings (Local Model)'
      case 'processing':
        return 'Processing...'
      case 'failed':
        return 'Failed'
      default:
        return status
    }
  }

  return (
    <div className="p-6 bg-gray-800 rounded-lg border border-gray-700">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <FileText className="w-6 h-6 text-blue-400" />
          <h2 className="text-xl font-semibold">Document Manager</h2>
        </div>
        <button
          onClick={() => setShowUpload(true)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span>Add Document</span>
        </button>
      </div>

      {/* Search Section */}
      <div className="mb-6 p-4 bg-gray-900 rounded-lg border border-gray-700">
        <div className="flex gap-2">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search documents..."
            className="flex-1 px-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
          />
          <button
            onClick={handleSearch}
            disabled={searching || !searchQuery.trim()}
            className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white rounded-lg transition-colors flex items-center gap-2"
          >
            <Search className="w-4 h-4" />
            <span>{searching ? 'Searching...' : 'Search'}</span>
          </button>
        </div>
        {searchResults.length > 0 && (
          <div className="mt-4">
            <h3 className="text-sm font-semibold text-gray-300 mb-2">Search Results</h3>
            <div className="space-y-2">
              {searchResults.map((result, index) => (
                <div key={index} className="p-3 bg-gray-800 rounded border border-gray-700">
                  <div className="flex justify-between items-start mb-1">
                    <span className="text-sm text-white font-medium">{result.payload?.title || 'Unknown'}</span>
                    <span className="text-xs text-gray-400">Score: {result.score?.toFixed(3)}</span>
                  </div>
                  <p className="text-xs text-gray-400 truncate">{result.payload?.content || 'No content'}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Documents List */}
      {loading ? (
        <div className="text-center py-12 text-gray-400">Loading documents...</div>
      ) : documents.length === 0 ? (
        <div className="text-center py-12 text-gray-400">
          <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>No documents yet. Add your first document to get started.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {documents.map((doc) => (
            <div key={doc.id} className="p-4 bg-gray-900 rounded-lg border border-gray-700 hover:border-gray-600 transition-colors">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <FileText className="w-4 h-4 text-blue-400" />
                    <h3 className="font-semibold text-white">{doc.title}</h3>
                    <span className="text-xs px-2 py-1 bg-gray-700 rounded text-gray-300">
                      {doc.file_type.toUpperCase()}
                    </span>
                  </div>
                  <div className="flex items-center gap-4 text-sm text-gray-400 mb-2">
                    <span className="flex items-center gap-1">
                      {getEmbeddingStatusIcon(doc.embedding_status)}
                      <span>{getEmbeddingStatusText(doc.embedding_status)}</span>
                    </span>
                    <span>• {doc.chunk_count} chunks</span>
                    <span>• {new Date(doc.created_at).toLocaleDateString()}</span>
                  </div>
                  <p className="text-sm text-gray-300 line-clamp-2">{doc.content}</p>
                </div>
                <button
                  onClick={() => handleDelete(doc.id)}
                  className="p-2 hover:bg-red-900/30 rounded-lg transition-colors text-red-400"
                  title="Delete document"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Upload Modal */}
      {showUpload && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-800 rounded-lg max-w-lg w-full border border-gray-700">
            <div className="flex items-center justify-between p-6 border-b border-gray-700">
              <h3 className="text-lg font-semibold">Add Document</h3>
              <button
                onClick={() => setShowUpload(false)}
                className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Title</label>
                <input
                  type="text"
                  value={uploadTitle}
                  onChange={(e) => setUploadTitle(e.target.value)}
                  placeholder="Document title"
                  className="w-full px-4 py-2 bg-gray-900 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Content</label>
                <textarea
                  value={uploadContent}
                  onChange={(e) => setUploadContent(e.target.value)}
                  placeholder="Document content (text, notes, etc.)"
                  rows={6}
                  className="w-full px-4 py-2 bg-gray-900 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 resize-none"
                />
              </div>
              <div className="flex justify-end gap-2">
                <button
                  onClick={() => setShowUpload(false)}
                  className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleUpload}
                  disabled={uploading || !uploadTitle || !uploadContent}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded-lg transition-colors"
                >
                  {uploading ? 'Uploading...' : 'Upload'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default DocumentManager