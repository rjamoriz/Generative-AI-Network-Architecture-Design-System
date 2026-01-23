'use client'

import { useEffect, useState } from 'react'

export default function Dashboard() {
  const [apiStatus, setApiStatus] = useState<'checking' | 'connected' | 'error'>('checking')
  const [apiData, setApiData] = useState<any>(null)

  useEffect(() => {
    const checkAPI = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
        const response = await fetch(`${apiUrl}/health`)
        const data = await response.json()
        setApiData(data)
        setApiStatus('connected')
      } catch (error) {
        console.error('API connection error:', error)
        setApiStatus('error')
      }
    }

    checkAPI()
  }, [])

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Dashboard</h1>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="p-6 border rounded-lg bg-white dark:bg-gray-800">
            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">
              API Status
            </h3>
            <div className="flex items-center gap-2">
              {apiStatus === 'checking' && (
                <>
                  <span className="text-yellow-500">●</span>
                  <span className="text-2xl font-bold">Checking...</span>
                </>
              )}
              {apiStatus === 'connected' && (
                <>
                  <span className="text-green-500">●</span>
                  <span className="text-2xl font-bold">Connected</span>
                </>
              )}
              {apiStatus === 'error' && (
                <>
                  <span className="text-red-500">●</span>
                  <span className="text-2xl font-bold">Error</span>
                </>
              )}
            </div>
          </div>

          <div className="p-6 border rounded-lg bg-white dark:bg-gray-800">
            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">
              Designs
            </h3>
            <p className="text-2xl font-bold">0</p>
          </div>

          <div className="p-6 border rounded-lg bg-white dark:bg-gray-800">
            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">
              Validations
            </h3>
            <p className="text-2xl font-bold">0</p>
          </div>
        </div>

        {apiData && (
          <div className="p-6 border rounded-lg bg-white dark:bg-gray-800 mb-8">
            <h2 className="text-xl font-semibold mb-4">Backend Health</h2>
            <pre className="bg-gray-100 dark:bg-gray-900 p-4 rounded overflow-auto">
              {JSON.stringify(apiData, null, 2)}
            </pre>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="p-6 border rounded-lg bg-white dark:bg-gray-800">
            <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
            <div className="space-y-3">
              <button className="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors">
                Create New Design
              </button>
              <button className="w-full px-4 py-2 border rounded hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                View Designs
              </button>
              <button className="w-full px-4 py-2 border rounded hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                Historical Data
              </button>
            </div>
          </div>

          <div className="p-6 border rounded-lg bg-white dark:bg-gray-800">
            <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
            <p className="text-gray-500 dark:text-gray-400">No recent activity</p>
          </div>
        </div>
      </div>
    </div>
  )
}
