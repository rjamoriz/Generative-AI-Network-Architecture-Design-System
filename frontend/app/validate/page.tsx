"use client";

import { useState } from "react";

interface ValidationResult {
  validation_id: string;
  design_id: string;
  overall_score: number;
  passed: boolean;
  deterministic_validation: {
    overall_score: number;
    passed: boolean;
    issues: Array<{
      severity: string;
      category: string;
      rule_id: string;
      message: string;
    }>;
  };
  llm_validation: {
    overall_score: number;
    passed: boolean;
    reasoning: string;
    confidence: number;
    issues: Array<{
      severity: string;
      category: string;
      message: string;
    }>;
  };
  all_issues: Array<{
    severity: string;
    category: string;
    message: string;
  }>;
  validated_at: string;
}

export default function ValidatePage() {
  const [designInput, setDesignInput] = useState("");
  const [isValidating, setIsValidating] = useState(false);
  const [result, setResult] = useState<ValidationResult | null>(null);

  const validateDesign = async () => {
    setIsValidating(true);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${apiUrl}/api/validate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          design_description: designInput,
          use_rag: true,
          include_similar_designs: true,
        }),
      });

      if (!response.ok) {
        throw new Error("Validation failed");
      }

      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error("Validation error:", error);
    } finally {
      setIsValidating(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
            RAG-Powered Design Validation
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-300">
            Validate your network design against historical validated
            architectures using AI-powered semantic search and analysis
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Input Section */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
            <h2 className="text-2xl font-semibold mb-4">
              Network Design Input
            </h2>

            <textarea
              value={designInput}
              onChange={(e) => setDesignInput(e.target.value)}
              placeholder="Describe your network design here...&#10;&#10;Example:&#10;- Network Type: Enterprise Campus&#10;- Scale: 5000 users&#10;- Topology: 3-tier (Core, Distribution, Access)&#10;- Redundancy: Active-Active&#10;- Protocols: OSPF, BGP&#10;- Security: Firewall zones, IDS/IPS&#10;- Compliance: PCI-DSS"
              className="w-full h-96 p-4 border dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-900 dark:text-white resize-none"
            />

            <button
              onClick={validateDesign}
              disabled={!designInput.trim() || isValidating}
              className="mt-4 w-full px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-semibold text-lg"
            >
              {isValidating ? "Validating with RAG..." : "Validate Design"}
            </button>

            <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
              <h3 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">
                🔍 How RAG Validation Works
              </h3>
              <ol className="text-sm text-blue-800 dark:text-blue-200 space-y-1">
                <li>1. Your design is converted to embeddings</li>
                <li>2. Semantic search finds similar validated designs</li>
                <li>3. AI compares against historical best practices</li>
                <li>4. Deterministic + LLM validation is performed</li>
                <li>5. Detailed scoring and recommendations provided</li>
              </ol>
            </div>
          </div>

          {/* Results Section */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
            <h2 className="text-2xl font-semibold mb-4">Validation Results</h2>

            {!result && !isValidating && (
              <div className="text-center py-20 text-gray-400">
                <div className="text-6xl mb-4">🔍</div>
                <p>Enter a design and click validate to see results</p>
              </div>
            )}

            {isValidating && (
              <div className="text-center py-20">
                <div className="animate-spin text-6xl mb-4">⚙️</div>
                <p className="text-lg font-semibold">
                  Analyzing design with RAG...
                </p>
                <p className="text-sm text-gray-500 mt-2">
                  Searching historical validated designs
                </p>
              </div>
            )}

            {result && (
              <div className="space-y-6">
                {/* Overall Score */}
                <div
                  className={`p-6 rounded-lg border-2 ${
                    result.passed
                      ? "bg-green-50 dark:bg-green-900/20 border-green-500"
                      : "bg-red-50 dark:bg-red-900/20 border-red-500"
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-xl font-semibold">Overall Score</h3>
                    <span className="text-3xl font-bold">
                      {(result.overall_score * 100).toFixed(0)}/100
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
                    <div
                      className={`h-3 rounded-full ${
                        result.passed ? "bg-green-500" : "bg-red-500"
                      }`}
                      style={{ width: `${result.overall_score * 100}%` }}
                    />
                  </div>
                  <p className="mt-2 text-sm">
                    Status:{" "}
                    <span className="font-semibold">
                      {result.passed ? "PASSED" : "FAILED"}
                    </span>
                  </p>
                </div>

                {/* Deterministic Validation */}
                <div className="border dark:border-gray-700 rounded-lg p-4">
                  <h3 className="font-semibold mb-3">
                    Deterministic Validation
                  </h3>
                  <div className="mb-3">
                    <div className="flex items-center gap-2">
                      <span className="text-xl">
                        {result.deterministic_validation.passed ? "✅" : "❌"}
                      </span>
                      <span className="font-medium">
                        Score:{" "}
                        {(
                          result.deterministic_validation.overall_score * 100
                        ).toFixed(0)}
                        %
                      </span>
                    </div>
                  </div>
                  {result.deterministic_validation.issues.length > 0 && (
                    <div className="space-y-2">
                      <p className="text-sm font-medium">Issues:</p>
                      {result.deterministic_validation.issues
                        .slice(0, 5)
                        .map((issue, idx) => (
                          <div
                            key={idx}
                            className="text-sm p-2 bg-gray-50 dark:bg-gray-900 rounded"
                          >
                            <span
                              className={`font-medium ${
                                issue.severity === "critical"
                                  ? "text-red-600"
                                  : issue.severity === "high"
                                    ? "text-orange-600"
                                    : "text-yellow-600"
                              }`}
                            >
                              [{issue.severity.toUpperCase()}]
                            </span>{" "}
                            {issue.message}
                          </div>
                        ))}
                    </div>
                  )}
                </div>

                {/* LLM Analysis */}
                <div className="border dark:border-gray-700 rounded-lg p-4">
                  <h3 className="font-semibold mb-3">AI Analysis</h3>
                  <div className="mb-3">
                    <div className="flex items-center gap-2">
                      <span className="text-xl">
                        {result.llm_validation.passed ? "✅" : "❌"}
                      </span>
                      <span className="font-medium">
                        Score:{" "}
                        {(result.llm_validation.overall_score * 100).toFixed(0)}
                        %
                      </span>
                    </div>
                  </div>
                  <p className="text-sm text-gray-700 dark:text-gray-300 mb-3">
                    {result.llm_validation.reasoning}
                  </p>
                  <div className="flex items-center gap-2 text-sm">
                    <span className="font-medium">Confidence:</span>
                    <span>
                      {(result.llm_validation.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>

                {/* All Issues */}
                {result.all_issues.length > 0 && (
                  <div className="border dark:border-gray-700 rounded-lg p-4">
                    <h3 className="font-semibold mb-3">
                      All Issues ({result.all_issues.length})
                    </h3>
                    <div className="space-y-2 max-h-64 overflow-y-auto">
                      {result.all_issues.map((issue, idx) => (
                        <div
                          key={idx}
                          className="text-sm p-2 bg-gray-50 dark:bg-gray-900 rounded"
                        >
                          <span
                            className={`font-medium ${
                              issue.severity === "critical"
                                ? "text-red-600"
                                : issue.severity === "high"
                                  ? "text-orange-600"
                                  : issue.severity === "medium"
                                    ? "text-yellow-600"
                                    : "text-blue-600"
                            }`}
                          >
                            [{issue.severity.toUpperCase()}]
                          </span>
                          <span className="text-gray-500 ml-2">
                            [{issue.category}]
                          </span>
                          <p className="mt-1">{issue.message}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Metadata */}
                <div className="border dark:border-gray-700 rounded-lg p-4">
                  <h3 className="font-semibold mb-3">Validation Details</h3>
                  <div className="text-sm space-y-1">
                    <p>
                      <span className="font-medium">Validation ID:</span>{" "}
                      {result.validation_id}
                    </p>
                    <p>
                      <span className="font-medium">Design ID:</span>{" "}
                      {result.design_id}
                    </p>
                    <p>
                      <span className="font-medium">Validated At:</span>{" "}
                      {new Date(result.validated_at).toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
