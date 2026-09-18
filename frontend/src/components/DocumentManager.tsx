import React, { useState, useEffect } from 'react'
import { FileText, Upload, Trash2, Search, Plus, X, CheckCircle, AlertCircle, Clock } from 'lucide-react'
import { useToast } from './ToastContainer'
import { DocumentSkeleton } from './SkeletonLoader'
import { API_BASE_URL } from '../config'

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
  const [uploadProgress, setUploadProgress] = useState(0)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<any[]>([])
  const [searching, setSearching] = useState(false)
  const [dragActive, setDragActive] = useState(false)
  const { success, error, info } = useToast()

  const fetchDocuments = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/documents`)
      if (response.ok) {
        const data = await response.json()
        setDocuments(data)
      } else {
        error('Failed to fetch documents')
      }
    } catch (err) {
      console.error('Failed to fetch documents:', err)
      error('Failed to fetch documents')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDocuments()
  }, [])

  const handleUpload = async () => {
    if (!uploadTitle || !uploadContent) {
      error('Please provide both title and content')
      return
    }

    setUploading(true)
    setUploadProgress(0)
    
    // Simulate upload progress
    const progressInterval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= 90) {
          clearInterval(progressInterval)
          return 90
        }
        return prev + 10
      })
    }, 200)

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/v1/documents/text?title=${encodeURIComponent(uploadTitle)}&content=${encodeURIComponent(uploadContent)}`
      )
      if (response.ok) {
        const data = await response.json()
        setUploadProgress(100)
        clearInterval(progressInterval)
        success('Document uploaded successfully')
        setShowUpload(false)
        setUploadTitle('')
        setUploadContent('')
        fetchDocuments()
      } else {
        error('Failed to upload document')
        clearInterval(progressInterval)
      }
    } catch (err) {
      console.error('Failed to upload document:', err)
      error('Failed to upload document')
      clearInterval(progressInterval)
    } finally {
      setUploading(false)
      setUploadProgress(0)
    }
  }

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0]
      handleFileUpload(file)
    }
  }

  const handleFileUpload = async (file: File) => {
    setUploading(true)
    setUploadProgress(0)
    
    // Simulate upload progress
    const progressInterval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= 90) {
          clearInterval(progressInterval)
          return 90
        }
        return prev + 10
      })
    }, 200)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch(`${API_BASE_URL}/api/v1/documents/upload`, {
        method: 'POST',
        body: formData
      })

      if (response.ok) {
        const data = await response.json()
        setUploadProgress(100)
        clearInterval(progressInterval)
        success(`File "${file.name}" uploaded successfully`)
        fetchDocuments()
      } else {
        const errorData = await response.json()
        error(errorData.detail || 'Failed to upload file')
        clearInterval(progressInterval)
      }
    } catch (err) {
      console.error('Failed to upload file:', err)
      error('Failed to upload file')
      clearInterval(progressInterval)
    } finally {
      setUploading(false)
      setUploadProgress(0)
    }
  }

  const handleDelete = async (documentId: number) => {
    if (!confirm('Are you sure you want to delete this document?')) return

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/documents/${documentId}`, {
        method: 'DELETE'
      })
      if (response.ok) {
        success('Document deleted successfully')
        fetchDocuments()
      } else {
        error('Failed to delete document')
      }
    } catch (err) {
      console.error('Failed to delete document:', err)
      error('Failed to delete document')
    }
  }

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      error('Please enter a search query')
      return
    }

    setSearching(true)
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/v1/documents/search?query=${encodeURIComponent(searchQuery)}`
      )
      if (response.ok) {
        const data = await response.json()
        setSearchResults(data.results || [])
        info(`Found ${data.results?.length || 0} results`)
      } else {
        error('Search failed')
      }
    } catch (err) {
      console.error('Failed to search documents:', err)
      error('Failed to search documents')
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
    <div 
      className="relative p-6 bg-gray-800 rounded-lg border border-gray-700"
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
      role="region"
      aria-label="Document Manager"
    >
      {dragActive && (
        <div className="absolute inset-0 bg-blue-500/20 border-2 border-dashed border-blue-500 rounded-lg flex items-center justify-center z-10">
          <div className="text-center">
            <Upload className="w-12 h-12 text-blue-400 mx-auto mb-2" />
            <p className="text-blue-400 font-semibold">Drop file here to upload</p>
          </div>
        </div>
      )}
      
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
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => <DocumentSkeleton key={i} />)}
        </div>
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
        <div 
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
          role="dialog"
          aria-modal="true"
          aria-labelledby="upload-modal-title"
        >
          <div className="bg-gray-800 rounded-lg max-w-lg w-full border border-gray-700">
            <div className="flex items-center justify-between p-6 border-b border-gray-700">
              <h3 id="upload-modal-title" className="text-lg font-semibold">Add Document</h3>
              <button
                onClick={() => setShowUpload(false)}
                className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
                aria-label="Close upload modal"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label htmlFor="document-title" className="block text-sm font-medium text-gray-300 mb-2">Title</label>
                <input
                  id="document-title"
                  type="text"
                  value={uploadTitle}
                  onChange={(e) => setUploadTitle(e.target.value)}
                  placeholder="Document title"
                  className="w-full px-4 py-2 bg-gray-900 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                  aria-required="true"
                />
              </div>
              
              <div>
                <label htmlFor="document-file" className="block text-sm font-medium text-gray-300 mb-2">Or Upload File</label>
                <input
                  id="document-file"
                  type="file"
                  onChange={(e) => {
                    const file = e.target.files?.[0]
                    if (file) {
                      setUploadTitle(file.name)
                      handleFileUpload(file)
                    }
                  }}
                  accept=".txt,.md,.json,.csv,.xml,.html,.py,.js,.ts,.java,.c,.cpp,.h,.css,.sql,.pdf,.docx,.doc,.pptx,.ppt,.odt,.rtf,.png,.jpg,.jpeg,.gif,.bmp,.webp,.svg"
                  className="w-full px-4 py-2 bg-gray-900 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                />
                <p className="text-xs text-gray-400 mt-1">
                  Supported: Text files, PDFs, Word docs, PowerPoint, images
                </p>
              </div>
              
              <div>
                <label htmlFor="document-content" className="block text-sm font-medium text-gray-300 mb-2">Or Paste Content</label>
                <textarea
                  id="document-content"
                  value={uploadContent}
                  onChange={(e) => setUploadContent(e.target.value)}
                  placeholder="Document content (text, notes, etc.)"
                  rows={6}
                  className="w-full px-4 py-2 bg-gray-900 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 resize-none"
                  aria-required="true"
                />
              </div>
              {uploadProgress > 0 && (
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
              )}
              <div className="flex justify-end gap-2">
                <button
                  onClick={() => setShowUpload(false)}
                  disabled={uploading}
                  className="px-4 py-2 bg-gray-700 hover:bg-gray-600 disabled:bg-gray-800 text-white rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleUpload}
                  disabled={uploading || !uploadTitle || !uploadContent}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded-lg transition-colors"
                >
                  {uploading ? `Uploading ${uploadProgress}%` : 'Upload'}
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