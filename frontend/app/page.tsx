import Link from 'next/link'

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center">
            <h1 className="text-5xl md:text-6xl font-bold text-gray-900 dark:text-white mb-6">
              AI-Powered Network Architecture
              <span className="block text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">
                Design & Validation System
              </span>
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-3xl mx-auto">
              Enterprise-grade Generative AI system for designing and validating both legacy and SDN network architectures with RAG-powered historical knowledge
            </p>
            <div className="flex gap-4 justify-center">
              <Link
                href="/dashboard"
                className="px-8 py-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all transform hover:scale-105 font-semibold shadow-lg"
              >
                Launch Dashboard →
              </Link>
              <Link
                href="/upload"
                className="px-8 py-4 border-2 border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 dark:hover:bg-gray-800 transition-all font-semibold"
              >
                Upload Documents
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Key Features */}
      <section className="py-20 bg-white dark:bg-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center mb-12">Enterprise Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Document Upload & Embeddings */}
            <div className="p-6 border-2 border-blue-200 dark:border-blue-800 rounded-xl hover:shadow-xl transition-all">
              <div className="text-4xl mb-4">📄</div>
              <h3 className="text-xl font-semibold mb-3">Document Upload & Embeddings</h3>
              <p className="text-gray-600 dark:text-gray-300 mb-4">
                Upload PDF documents of historical validated network designs. Automatically generate embeddings and store in DataStax for RAG-powered retrieval.
              </p>
              <Link href="/upload" className="text-blue-600 hover:text-blue-700 font-medium">
                Upload Documents →
              </Link>
            </div>

            {/* RAG-Powered Validation */}
            <div className="p-6 border-2 border-purple-200 dark:border-purple-800 rounded-xl hover:shadow-xl transition-all">
              <div className="text-4xl mb-4">🔍</div>
              <h3 className="text-xl font-semibold mb-3">RAG-Powered Historical Validation</h3>
              <p className="text-gray-600 dark:text-gray-300 mb-4">
                Validate new designs against historical data using semantic search. AI compares your design with similar validated architectures.
              </p>
              <Link href="/validate" className="text-purple-600 hover:text-purple-700 font-medium">
                Validate Design →
              </Link>
            </div>

            {/* AI Design Generation */}
            <div className="p-6 border-2 border-green-200 dark:border-green-800 rounded-xl hover:shadow-xl transition-all">
              <div className="text-4xl mb-4">🤖</div>
              <h3 className="text-xl font-semibold mb-3">Multi-Agent AI Design</h3>
              <p className="text-gray-600 dark:text-gray-300 mb-4">
                4 specialized AI agents work together: Requirement Analysis, RAG Retrieval, Design Synthesis, and Validation & Compliance.
              </p>
              <Link href="/design/new" className="text-green-600 hover:text-green-700 font-medium">
                Generate Design →
              </Link>
            </div>

            {/* Network Canvas */}
            <div className="p-6 border-2 border-orange-200 dark:border-orange-800 rounded-xl hover:shadow-xl transition-all">
              <div className="text-4xl mb-4">🎨</div>
              <h3 className="text-xl font-semibold mb-3">Interactive Design Canvas</h3>
              <p className="text-gray-600 dark:text-gray-300 mb-4">
                Visual network topology builder with drag-and-drop components. Real-time validation as you design.
              </p>
              <Link href="/canvas" className="text-orange-600 hover:text-orange-700 font-medium">
                Open Canvas →
              </Link>
            </div>

            {/* Compliance & Security */}
            <div className="p-6 border-2 border-red-200 dark:border-red-800 rounded-xl hover:shadow-xl transition-all">
              <div className="text-4xl mb-4">🔒</div>
              <h3 className="text-xl font-semibold mb-3">Compliance & Security</h3>
              <p className="text-gray-600 dark:text-gray-300 mb-4">
                Deterministic + probabilistic validation. Complete audit logs. RBAC. Zero-trust architecture. Human-in-the-loop approval required.
              </p>
              <Link href="/compliance" className="text-red-600 hover:text-red-700 font-medium">
                View Compliance →
              </Link>
            </div>

            {/* Historical Analytics */}
            <div className="p-6 border-2 border-indigo-200 dark:border-indigo-800 rounded-xl hover:shadow-xl transition-all">
              <div className="text-4xl mb-4">📊</div>
              <h3 className="text-xl font-semibold mb-3">Historical Analytics</h3>
              <p className="text-gray-600 dark:text-gray-300 mb-4">
                Browse validated designs, track changes, compare configurations. Full data lineage and versioning.
              </p>
              <Link href="/historical" className="text-indigo-600 hover:text-indigo-700 font-medium">
                View Analytics →
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* AI Workflow */}
      <section className="py-20 bg-gray-50 dark:bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center mb-12">AI-Powered Workflow</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">1</div>
              <h3 className="font-semibold mb-2">Requirements Analysis</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">AI extracts and structures network requirements</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-purple-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">2</div>
              <h3 className="font-semibold mb-2">RAG Retrieval</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">Semantic search of validated designs from embeddings</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-green-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">3</div>
              <h3 className="font-semibold mb-2">Design Synthesis</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">Generate architecture using RAG context</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-red-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">4</div>
              <h3 className="font-semibold mb-2">Validation</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">Deterministic + LLM validation with scoring</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-purple-600 text-white">
        <div className="max-w-4xl mx-auto text-center px-4">
          <h2 className="text-4xl font-bold mb-6">Ready to Transform Your Network Design Process?</h2>
          <p className="text-xl mb-8 opacity-90">
            Start by uploading your historical network design documents to build your knowledge base
          </p>
          <Link
            href="/upload"
            className="inline-block px-10 py-4 bg-white text-blue-600 rounded-lg hover:bg-gray-100 transition-all transform hover:scale-105 font-bold text-lg shadow-xl"
          >
            Upload Documents & Get Started
          </Link>
        </div>
      </section>
    </div>
  )
}
