// app/context/page.tsx
'use client';

import React, { useState, useEffect, useCallback } from 'react';

interface ContextEntry {
  id: number;
  content: string;
  source_type: string;
  timestamp: string;
  processed_insights: string | object; // Can be string or object
}

export default function ContextPage() {
  const [content, setContent] = useState('');
  const [sourceType, setSourceType] = useState('note'); // Default source type
  const [contextEntries, setContextEntries] = useState<ContextEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [submitLoading, setSubmitLoading] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitSuccess, setSubmitSuccess] = useState<string | null>(null);

  // Helper function to safely display processed_insights
  const displayProcessedInsights = (insights: string | object | null) => {
    if (!insights) return 'N/A';
    
    try {
      // If it's already an object, stringify it directly
      if (typeof insights === 'object') {
        return JSON.stringify(insights, null, 2);
      }
      
      // If it's a string, try to parse it first, then stringify
      if (typeof insights === 'string') {
        const parsed = JSON.parse(insights);
        return JSON.stringify(parsed, null, 2);
      }
      
      return String(insights);
    } catch (error) {
      // If parsing fails, just return the original string
      return typeof insights === 'string' ? insights : String(insights);
    }
  };

  const fetchContextEntries = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8000/api/context/');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data: ContextEntry[] = await response.json();
      setContextEntries(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchContextEntries();
  }, [fetchContextEntries]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitLoading(true);
    setSubmitError(null);
    setSubmitSuccess(null);

    try {
      const response = await fetch('http://localhost:8000/api/context/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content, source_type: sourceType }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || JSON.stringify(errorData) || `HTTP error! status: ${response.status}`);
      }

      setSubmitSuccess('Context entry added successfully and analyzed by AI!');
      setContent(''); // Clear form
      fetchContextEntries(); // Refresh the list
    } catch (err: any) {
      setSubmitError(err.message);
    } finally {
      setSubmitLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center p-8 bg-gray-100">
      <h1 className="text-4xl font-bold text-gray-800 mb-8">Daily Context Input</h1>

      {/* Context Input Form */}
      <div className="w-full max-w-2xl mx-auto bg-white shadow-lg rounded-lg p-6 mb-8 border border-gray-200">
        <h2 className="text-2xl font-bold text-gray-800 mb-4 text-center">Add New Context Entry</h2>
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label htmlFor="content" className="block text-gray-700 text-sm font-bold mb-2">
              Content:
            </label>
            <textarea
              id="content"
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline h-32 resize-none"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              required
              disabled={submitLoading}
            ></textarea>
          </div>
          <div className="mb-6">
            <label htmlFor="sourceType" className="block text-gray-700 text-sm font-bold mb-2">
              Source Type:
            </label>
            <select
              id="sourceType"
              className="shadow border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              value={sourceType}
              onChange={(e) => setSourceType(e.target.value)}
              disabled={submitLoading}
            >
              <option value="note">Note</option>
              <option value="message">Message</option>
              <option value="email">Email</option>
            </select>
          </div>
          <div className="flex items-center justify-between">
            <button
              type="submit"
              className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={submitLoading || !content.trim()}
            >
              {submitLoading ? 'Adding...' : 'Add Context'}
            </button>
          </div>
          {submitError && <p className="text-red-500 text-xs italic mt-4">{submitError}</p>}
          {submitSuccess && <p className="text-green-500 text-xs italic mt-4">{submitSuccess}</p>}
        </form>
      </div>

      {/* Context History View */}
      <div className="w-full max-w-2xl mx-auto bg-white shadow-lg rounded-lg p-6 border border-gray-200">
        <h2 className="text-2xl font-bold text-gray-800 mb-4 text-center">Context History</h2>
        {loading ? (
          <p className="text-center text-gray-600">Loading context entries...</p>
        ) : error ? (
          <p className="text-center text-red-500">Error: {error}</p>
        ) : contextEntries.length === 0 ? (
          <p className="text-center text-gray-600">No context entries yet.</p>
        ) : (
          <div className="space-y-4">
            {contextEntries.map((entry) => (
              <div key={entry.id} className="border-b pb-4 last:border-b-0">
                <p className="text-gray-800 text-base mb-1">
                  <strong>Content:</strong> {entry.content}
                </p>
                <p className="text-gray-600 text-sm mb-1">
                  <strong>Source:</strong> {entry.source_type}
                </p>
                <p className="text-gray-600 text-sm mb-1">
                  <strong>Timestamp:</strong> {new Date(entry.timestamp).toLocaleString()}
                </p>
                <div className="text-gray-600 text-sm">
                  <strong>AI Insights:</strong>
                  <pre className="mt-1 p-2 bg-gray-100 rounded text-xs overflow-x-auto">
                    {displayProcessedInsights(entry.processed_insights)}
                  </pre>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

