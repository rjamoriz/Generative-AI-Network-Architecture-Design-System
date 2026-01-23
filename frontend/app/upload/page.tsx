'use client'

import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'

interface UploadedFile {
  file: File
  status: 'pending' | 'uploading' | 'processing' | 'completed' | 'error'
  progress: number
  message?: string
  documentId?: string
}

export default function UploadPage() {
  const [files, setFiles] = useState<UploadedFile[]>([])
  const [isProcessing, setIsProcessing] = useState(false)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles = acceptedFiles.map(file => ({
      file,
      status: 'pending' as const,
      progress: 0
    }))
    setFiles(prev => [...prev, ...newFiles])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    multiple: true
  })

  const uploadFiles = async () => {
    setIsProcessing(true)
    
    for (let i = 0; i < files.length; i++) {
      if (files[i].status !== 'pending') continue

      try {
        // Update status to uploading
        setFiles(prev => prev.map((f, idx) => 
          idx === i ? { ...f, status: 'uploading', progress: 0 } : f
        ))

        // Create form data
        const formData = new FormData()
        formData.append('file', files[i].file)
        formData.append('generate_embeddings', 'true')
        formData.append('store_in_vector_db', 'true')

        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
        
        // Upload file
        const response = await fetch(`${apiUrl}/api/v1/historical/upload`, {
          method: 'POST',
          body: formData,
        })

        if (!response.ok) {
          throw new Error(`Upload failed: ${response.statusText}`)
        }

        // Update to processing
        setFiles(prev => prev.map((f, idx) => 
          idx === i ? { ...f, status: 'processing', progress: 50 } : f
        ))

        const result = await response.json()

        // Update to completed
        setFiles(prev => prev.map((f, idx) => 
          idx === i ? { 
            ...f, 
            status: 'completed', 
            progress: 100,
            message: `Processed ${result.page_count} pages (${result.chunk_count} chunks)`,
            documentId: result.document_id
          } : f
        ))

      } catch (error) {
        setFiles(prev => prev.map((f, idx) => 
          idx === i ? { 
            ...f, 
            status: 'error', 
            progress: 0,
            message: error instanceof Error ? error.message : 'Upload failed'
          } : f
        ))
      }
    }

    setIsProcessing(false)
  }

  const clearCompleted = () => {
    setFiles(prev => prev.filter(f => f.status !== 'completed'))
  }

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, idx) => idx !== index))
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-12">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Upload Historical Network Designs
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-300">
            Upload PDF documents of validated network designs. The system will automatically extract content, 
            generate embeddings using OpenAI, and store them in DataStax for RAG-powered retrieval.
          </p>
        </div>

        {/* Upload Zone */}
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all mb-8 ${
            isDragActive 
              ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' 
              : 'border-gray-300 dark:border-gray-700 hover:border-blue-400 dark:hover:border-blue-600'
          }`}
        >
          <input {...getInputProps()} />
          <div className="text-6xl mb-4">📄</div>
          {isDragActive ? (
            <p className="text-xl text-blue-600 dark:text-blue-400 font-semibold">
              Drop PDF files here...
            </p>
          ) : (
            <>
              <p className="text-xl text-gray-700 dark:text-gray-300 font-semibold mb-2">
                Drag & drop PDF files here, or click to select
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Supports multiple PDF files. Each file will be processed for embeddings.
              </p>
            </>
          )}
        </div>

        {/* File List */}
        {files.length > 0 && (
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-semibold">
                Files ({files.length})
              </h2>
              <div className="flex gap-3">
                <button
                  onClick={clearCompleted}
                  className="px-4 py-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
                  disabled={!files.some(f => f.status === 'completed')}
                >
                  Clear Completed
                </button>
                <button
                  onClick={uploadFiles}
                  disabled={isProcessing || !files.some(f => f.status === 'pending')}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-semibold"
                >
                  {isProcessing ? 'Processing...' : 'Upload & Generate Embeddings'}
                </button>
              </div>
            </div>

            <div className="space-y-3">
              {files.map((fileItem, index) => (
                <div
                  key={index}
                  className="border dark:border-gray-700 rounded-lg p-4 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-3 flex-1">
                      <div className="text-2xl">
                        {fileItem.status === 'completed' && '✅'}
                        {fileItem.status === 'error' && '❌'}
                        {fileItem.status === 'uploading' && '⬆️'}
                        {fileItem.status === 'processing' && '⚙️'}
                        {fileItem.status === 'pending' && '📄'}
                      </div>
                      <div className="flex-1">
                        <p className="font-medium text-gray-900 dark:text-white">
                          {fileItem.file.name}
                        </p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          {(fileItem.file.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={() => removeFile(index)}
                      className="text-red-600 hover:text-red-700 px-3 py-1"
                      disabled={fileItem.status === 'uploading' || fileItem.status === 'processing'}
                    >
                      Remove
                    </button>
                  </div>

                  {/* Progress Bar */}
                  {(fileItem.status === 'uploading' || fileItem.status === 'processing') && (
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mb-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${fileItem.progress}%` }}
                      />
                    </div>
                  )}

                  {/* Status Message */}
                  {fileItem.message && (
                    <p className={`text-sm ${
                      fileItem.status === 'error' 
                        ? 'text-red-600 dark:text-red-400' 
                        : 'text-green-600 dark:text-green-400'
                    }`}>
                      {fileItem.message}
                    </p>
                  )}

                  {/* Embedding ID */}
                  {fileItem.documentId && (
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      Document ID: {fileItem.documentId}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Info Section */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6">
            <h3 className="font-semibold text-lg mb-2 text-blue-900 dark:text-blue-100">
              📤 Upload Process
            </h3>
            <p className="text-sm text-blue-800 dark:text-blue-200">
              PDFs are uploaded to the backend, text is extracted, and content is chunked for optimal embedding generation.
            </p>
          </div>

          <div className="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg p-6">
            <h3 className="font-semibold text-lg mb-2 text-purple-900 dark:text-purple-100">
              🧠 Embedding Generation
            </h3>
            <p className="text-sm text-purple-800 dark:text-purple-200">
              OpenAI embeddings are generated for each chunk, capturing semantic meaning of network designs and configurations.
            </p>
          </div>

          <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-6">
            <h3 className="font-semibold text-lg mb-2 text-green-900 dark:text-green-100">
              💾 DataStax Storage
            </h3>
            <p className="text-sm text-green-800 dark:text-green-200">
              Embeddings are stored in DataStax Astra DB with vector search capabilities for fast RAG retrieval.
            </p>
          </div>
        </div>

        {/* Usage Instructions */}
        <div className="mt-8 bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
          <h2 className="text-2xl font-semibold mb-4">How It Works</h2>
          <ol className="space-y-3 text-gray-700 dark:text-gray-300">
            <li className="flex gap-3">
              <span className="font-bold text-blue-600">1.</span>
              <span>Upload PDF documents containing historical validated network designs</span>
            </li>
            <li className="flex gap-3">
              <span className="font-bold text-blue-600">2.</span>
              <span>System extracts text and metadata from PDFs</span>
            </li>
            <li className="flex gap-3">
              <span className="font-bold text-blue-600">3.</span>
              <span>Content is chunked into optimal sizes for embedding generation</span>
            </li>
            <li className="flex gap-3">
              <span className="font-bold text-blue-600">4.</span>
              <span>OpenAI generates semantic embeddings for each chunk</span>
            </li>
            <li className="flex gap-3">
              <span className="font-bold text-blue-600">5.</span>
              <span>Embeddings are stored in DataStax Astra DB with vector search indexes</span>
            </li>
            <li className="flex gap-3">
              <span className="font-bold text-blue-600">6.</span>
              <span>When validating new designs, RAG retrieves similar historical designs for comparison</span>
            </li>
          </ol>
        </div>
      </div>
    </div>
  )
}
