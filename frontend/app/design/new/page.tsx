"use client";

import { useState } from "react";

interface Requirements {
  network_type: string;
  scale: string;
  bandwidth: string;
  security_level: string;
  compliance: string[];
  constraints: string;
}

interface AgentProgress {
  requirement_analysis: "pending" | "running" | "completed";
  rag_retrieval: "pending" | "running" | "completed";
  design_synthesis: "pending" | "running" | "completed";
  validation: "pending" | "running" | "completed";
}

export default function NewDesignPage() {
  const [requirements, setRequirements] = useState<Requirements>({
    network_type: "",
    scale: "",
    bandwidth: "",
    security_level: "medium",
    compliance: [],
    constraints: "",
  });

  const [isGenerating, setIsGenerating] = useState(false);
  const [agentProgress, setAgentProgress] = useState<AgentProgress>({
    requirement_analysis: "pending",
    rag_retrieval: "pending",
    design_synthesis: "pending",
    validation: "pending",
  });
  const [generatedDesign, setGeneratedDesign] = useState<any>(null);

  const generateDesign = async () => {
    setIsGenerating(true);
    setAgentProgress({
      requirement_analysis: "running",
      rag_retrieval: "pending",
      design_synthesis: "pending",
      validation: "pending",
    });

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

      // Simulate agent workflow
      setTimeout(() => {
        setAgentProgress((prev) => ({
          ...prev,
          requirement_analysis: "completed",
          rag_retrieval: "running",
        }));
      }, 2000);

      setTimeout(() => {
        setAgentProgress((prev) => ({
          ...prev,
          rag_retrieval: "completed",
          design_synthesis: "running",
        }));
      }, 4000);

      setTimeout(() => {
        setAgentProgress((prev) => ({
          ...prev,
          design_synthesis: "completed",
          validation: "running",
        }));
      }, 6000);

      const response = await fetch(`${apiUrl}/api/v1/design/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          project_name: "User Project",
          network_type: requirements.network_type,
          scale: {
            users: parseInt(requirements.scale) || 1000,
            devices: parseInt(requirements.scale) || 1000,
            sites: 1,
          },
          bandwidth: {
            min: requirements.bandwidth,
            max: requirements.bandwidth,
            unit: "Gbps",
          },
          security_level: requirements.security_level,
          compliance: requirements.compliance,
          constraints: requirements.constraints,
        }),
      });

      if (!response.ok) {
        throw new Error("Generation failed");
      }

      const data = await response.json();
      setGeneratedDesign(data);
      setAgentProgress((prev) => ({ ...prev, validation: "completed" }));
    } catch (error) {
      console.error("Generation error:", error);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
            AI-Powered Network Design Generation
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-300">
            Multi-agent AI system generates network architectures using
            RAG-powered historical knowledge
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Requirements Form */}
          <div className="lg:col-span-2 bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
            <h2 className="text-2xl font-semibold mb-6">
              Network Requirements
            </h2>

            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Network Type
                </label>
                <select
                  value={requirements.network_type}
                  onChange={(e) =>
                    setRequirements({
                      ...requirements,
                      network_type: e.target.value,
                    })
                  }
                  className="w-full p-3 border dark:border-gray-700 rounded-lg dark:bg-gray-900"
                >
                  <option value="">Select type...</option>
                  <option value="enterprise_campus">Enterprise Campus</option>
                  <option value="data_center">Data Center</option>
                  <option value="wan">Wide Area Network (WAN)</option>
                  <option value="sdn">Software-Defined Network (SDN)</option>
                  <option value="hybrid">Hybrid (Legacy + SDN)</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Scale (Users/Devices)
                  </label>
                  <input
                    type="text"
                    value={requirements.scale}
                    onChange={(e) =>
                      setRequirements({
                        ...requirements,
                        scale: e.target.value,
                      })
                    }
                    placeholder="e.g., 5000 users"
                    className="w-full p-3 border dark:border-gray-700 rounded-lg dark:bg-gray-900"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">
                    Bandwidth Requirements
                  </label>
                  <input
                    type="text"
                    value={requirements.bandwidth}
                    onChange={(e) =>
                      setRequirements({
                        ...requirements,
                        bandwidth: e.target.value,
                      })
                    }
                    placeholder="e.g., 10 Gbps"
                    className="w-full p-3 border dark:border-gray-700 rounded-lg dark:bg-gray-900"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Security Level
                </label>
                <select
                  value={requirements.security_level}
                  onChange={(e) =>
                    setRequirements({
                      ...requirements,
                      security_level: e.target.value,
                    })
                  }
                  className="w-full p-3 border dark:border-gray-700 rounded-lg dark:bg-gray-900"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Compliance Requirements
                </label>
                <div className="grid grid-cols-2 gap-3">
                  {["PCI-DSS", "HIPAA", "SOC2", "ISO27001"].map((comp) => (
                    <label key={comp} className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={requirements.compliance.includes(comp)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setRequirements({
                              ...requirements,
                              compliance: [...requirements.compliance, comp],
                            });
                          } else {
                            setRequirements({
                              ...requirements,
                              compliance: requirements.compliance.filter(
                                (c) => c !== comp,
                              ),
                            });
                          }
                        }}
                        className="w-4 h-4"
                      />
                      <span className="text-sm">{comp}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Additional Constraints
                </label>
                <textarea
                  value={requirements.constraints}
                  onChange={(e) =>
                    setRequirements({
                      ...requirements,
                      constraints: e.target.value,
                    })
                  }
                  placeholder="Any specific requirements, constraints, or preferences..."
                  className="w-full p-3 border dark:border-gray-700 rounded-lg dark:bg-gray-900 h-32"
                />
              </div>

              <button
                onClick={generateDesign}
                disabled={!requirements.network_type || isGenerating}
                className="w-full px-6 py-4 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-semibold text-lg"
              >
                {isGenerating
                  ? "AI Agents Working..."
                  : "Generate Design with AI"}
              </button>
            </div>
          </div>

          {/* Agent Progress */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
            <h2 className="text-2xl font-semibold mb-6">AI Agent Workflow</h2>

            <div className="space-y-4">
              {[
                {
                  key: "requirement_analysis",
                  label: "Requirement Analysis",
                  icon: "📋",
                  color: "blue",
                },
                {
                  key: "rag_retrieval",
                  label: "RAG Retrieval",
                  icon: "🔍",
                  color: "purple",
                },
                {
                  key: "design_synthesis",
                  label: "Design Synthesis",
                  icon: "🎨",
                  color: "green",
                },
                {
                  key: "validation",
                  label: "Validation",
                  icon: "✅",
                  color: "red",
                },
              ].map(({ key, label, icon, color }) => {
                const status = agentProgress[key as keyof AgentProgress];
                return (
                  <div
                    key={key}
                    className="border dark:border-gray-700 rounded-lg p-4"
                  >
                    <div className="flex items-center gap-3">
                      <div className="text-2xl">{icon}</div>
                      <div className="flex-1">
                        <div className="font-medium">{label}</div>
                        <div className="text-sm text-gray-500">
                          {status === "pending" && "Waiting..."}
                          {status === "running" && (
                            <span className="text-blue-600 dark:text-blue-400">
                              Running...
                            </span>
                          )}
                          {status === "completed" && (
                            <span className="text-green-600 dark:text-green-400">
                              Completed ✓
                            </span>
                          )}
                        </div>
                      </div>
                      {status === "running" && (
                        <div className="animate-spin text-xl">⚙️</div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>

            {generatedDesign && (
              <div className="mt-6 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                <h3 className="font-semibold text-green-900 dark:text-green-100 mb-2">
                  ✅ Design Generated Successfully!
                </h3>
                <p className="text-sm text-green-800 dark:text-green-200">
                  Scroll down to view the complete network architecture
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Generated Design Display */}
        {generatedDesign && (
          <div className="mt-8 bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
            <h2 className="text-2xl font-semibold mb-6">
              Generated Network Design
            </h2>
            <pre className="bg-gray-100 dark:bg-gray-900 p-6 rounded-lg overflow-auto text-sm">
              {JSON.stringify(generatedDesign, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}
