"use client";

import { useEffect, useState } from "react";

interface AuditLog {
  id: number;
  actor: string | null;
  action: string;
  status: string;
  resource_type: string | null;
  resource_id: string | null;
  message: string | null;
  metadata: any;
  trace_id: string | null;
  request_id: string | null;
  created_at: string;
}

export default function AuditPage() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [actionFilter, setActionFilter] = useState<string>("");
  const [limit, setLimit] = useState(50);

  const fetchLogs = async () => {
    setIsLoading(true);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const params = new URLSearchParams({
        limit: limit.toString(),
        offset: "0",
      });
      if (statusFilter) params.append("status", statusFilter);
      if (actionFilter) params.append("action", actionFilter);

      const response = await fetch(`${apiUrl}/api/v1/audit/logs?${params}`);
      if (!response.ok) {
        throw new Error("Failed to fetch audit logs");
      }

      const data = await response.json();
      setLogs(data);
    } catch (error) {
      console.error("Error fetching audit logs:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [statusFilter, actionFilter, limit]);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Audit Logs
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-300">
            View system activity and audit trail for all operations
          </p>
        </div>

        {/* Filters */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Filters</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Status</label>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full p-3 border dark:border-gray-700 rounded-lg dark:bg-gray-900"
              >
                <option value="">All</option>
                <option value="success">Success</option>
                <option value="failed">Failed</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Action</label>
              <select
                value={actionFilter}
                onChange={(e) => setActionFilter(e.target.value)}
                className="w-full p-3 border dark:border-gray-700 rounded-lg dark:bg-gray-900"
              >
                <option value="">All</option>
                <option value="design_generate">Design Generate</option>
                <option value="design_validate">Design Validate</option>
                <option value="salesforce_ingest">Salesforce Ingest</option>
                <option value="pdf_ingest">PDF Ingest</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Limit</label>
              <select
                value={limit}
                onChange={(e) => setLimit(parseInt(e.target.value))}
                className="w-full p-3 border dark:border-gray-700 rounded-lg dark:bg-gray-900"
              >
                <option value="25">25</option>
                <option value="50">50</option>
                <option value="100">100</option>
              </select>
            </div>
          </div>

          <button
            onClick={fetchLogs}
            className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Refresh
          </button>
        </div>

        {/* Logs Table */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden">
          {isLoading ? (
            <div className="text-center py-20">
              <div className="animate-spin text-6xl mb-4">⚙️</div>
              <p className="text-lg font-semibold">Loading audit logs...</p>
            </div>
          ) : logs.length === 0 ? (
            <div className="text-center py-20 text-gray-400">
              <div className="text-6xl mb-4">📋</div>
              <p>No audit logs found</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-100 dark:bg-gray-700">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                      Timestamp
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                      Action
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                      Resource
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                      Message
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                      Actor
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                  {logs.map((log) => (
                    <tr
                      key={log.id}
                      className="hover:bg-gray-50 dark:hover:bg-gray-700"
                    >
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {new Date(log.created_at).toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        {log.action}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`px-2 py-1 text-xs font-semibold rounded-full ${
                            log.status === "success"
                              ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                              : "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
                          }`}
                        >
                          {log.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {log.resource_type && (
                          <div>
                            <div className="font-medium">
                              {log.resource_type}
                            </div>
                            {log.resource_id && (
                              <div className="text-xs text-gray-500">
                                {log.resource_id}
                              </div>
                            )}
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 text-sm max-w-md truncate">
                        {log.message || "-"}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {log.actor || "system"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Stats */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6">
            <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">
              {logs.length}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Total Logs Displayed
            </div>
          </div>

          <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-6">
            <div className="text-3xl font-bold text-green-600 dark:text-green-400">
              {logs.filter((l) => l.status === "success").length}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Successful Operations
            </div>
          </div>

          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6">
            <div className="text-3xl font-bold text-red-600 dark:text-red-400">
              {logs.filter((l) => l.status === "failed").length}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Failed Operations
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
