// app/components/TaskForm.tsx
'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation'; // For navigation after submission

// Define interfaces for Task and Category (should match your API response)
interface Task {
  id?: number; // Optional for new tasks
  title: string;
  description: string;
  category?: number;
  category_name?: string;
  priority_score?: string;
  priority?: string;
  deadline?: string;
  status: string;
  is_ai_suggested?: boolean;
  created_at?: string;
  updated_at?: string;
}

interface Category {
  id: number;
  name: string;
  usage_count: number;
}

interface TaskFormProps {
  initialTask?: Task;
  onTaskSubmitted?: () => void;
}

const TaskForm: React.FC<TaskFormProps> = ({ initialTask, onTaskSubmitted }) => {
  const router = useRouter();

  const [title, setTitle] = useState(initialTask?.title || '');
  const [description, setDescription] = useState(initialTask?.description || '');
  const [status, setStatus] = useState(initialTask?.status || 'pending');
  const [category, setCategory] = useState<string>(initialTask?.category?.toString() || '');
  const [deadline, setDeadline] = useState(initialTask?.deadline ? new Date(initialTask.deadline).toISOString().split('T')[0] : '');

  const [categories, setCategories] = useState<Category[]>([]);
  const [loadingCategories, setLoadingCategories] = useState(true);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // AI Suggestions states
  const [aiPriorityScore, setAiPriorityScore] = useState<string | undefined>(initialTask?.priority_score);
  const [aiPriority, setAiPriority] = useState<string | undefined>(initialTask?.priority);
  const [aiDeadline, setAiDeadline] = useState<string | undefined>(initialTask?.deadline);
  const [aiCategories, setAiCategories] = useState<string[]>([]);
  const [aiEnhancedDescription, setAiEnhancedDescription] = useState<string | undefined>(initialTask?.description);
  const [aiLoading, setAiLoading] = useState(false);


  // Fetch categories on mount
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/categories/' );
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data: Category[] = await response.json();
        setCategories(data);
      } catch (err: any) {
        console.error("Failed to fetch categories:", err);
      } finally {
        setLoadingCategories(false);
      }
    };
    fetchCategories();
  }, []);

  // Effect to update form fields if initialTask changes (for edit mode)
  useEffect(() => {
    if (initialTask) {
      setTitle(initialTask.title || '');
      setDescription(initialTask.description || '');
      setStatus(initialTask.status || 'pending');
      setCategory(initialTask.category?.toString() || '');
      setDeadline(initialTask.deadline ? new Date(initialTask.deadline).toISOString().split('T')[0] : '');

      setAiPriorityScore(initialTask.priority_score);
      setAiPriority(initialTask.priority);
      setAiDeadline(initialTask.deadline);
      setAiEnhancedDescription(initialTask.description);
    }
  }, [initialTask]);


  // Function to fetch AI suggestions
  const fetchAiSuggestions = async () => {
    if (!title.trim() && !description.trim()) {
      // Clear previous AI suggestions if input is empty
      setAiPriorityScore(undefined);
      setAiPriority(undefined);
      setAiDeadline(undefined);
      setAiCategories([]);
      setAiEnhancedDescription(undefined);
      return;
    }
    setAiLoading(true);
    setError(null);

    try {
      let responseData;
      if (initialTask?.id) {
        // For existing tasks, use the specific task's AI suggestions endpoint
        const response = await fetch(`http://localhost:8000/api/tasks/${initialTask.id}/get-ai-suggestions/`, { method: 'POST' } );
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        responseData = await response.json();
      } else {
        // For new tasks, use the new endpoint that takes title/description
        const response = await fetch('http://localhost:8000/api/tasks/get-ai-suggestions-for-new-task/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ title, description } ),
        });
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        responseData = await response.json();
      }

      // Update AI suggestion states
      setAiPriorityScore(responseData.suggested_priority_score);
      setAiPriority(responseData.suggested_priority);
      setAiDeadline(responseData.suggested_deadline);
      setAiCategories(responseData.suggested_categories || []);
      setAiEnhancedDescription(responseData.enhanced_description);

    } catch (err: any) {
      console.error("Failed to fetch AI suggestions:", err);
      setError(`Failed to get AI suggestions: ${err.message}`);
    } finally {
      setAiLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    const method = initialTask?.id ? 'PUT' : 'POST';
    const url = initialTask?.id
      ? `http://localhost:8000/api/tasks/${initialTask.id}/`
      : 'http://localhost:8000/api/tasks/';

    const payload: any = {
      title,
      description,
      status,
    };
    if (category ) {
      payload.category = parseInt(category); // Convert back to number for API
    }
    if (deadline) {
      payload.deadline = deadline; // YYYY-MM-DD
    }

    try {
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || JSON.stringify(errorData) || `HTTP error! status: ${response.status}`);
      }

      const resultTask = await response.json();
      setSuccess(`Task "${resultTask.title}" ${initialTask?.id ? 'updated' : 'created'} successfully!`);
      if (onTaskSubmitted) {
        onTaskSubmitted();
      }
      if (!initialTask?.id) { // Redirect to dashboard after creating new task
        router.push('/');
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto bg-white shadow-lg rounded-lg p-6 border border-gray-200">
      <h2 className="text-2xl font-bold text-gray-800 mb-4 text-center">
        {initialTask?.id ? 'Edit Task' : 'Create New Task'}
      </h2>
      <form onSubmit={handleSubmit}>
        {/* Title */}
        <div className="mb-4">
          <label htmlFor="title" className="block text-gray-700 text-sm font-bold mb-2">
            Title:
          </label>
          <input
            type="text"
            id="title"
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            onBlur={fetchAiSuggestions}
            required
            disabled={loading}
          />
        </div>

        {/* Description */}
        <div className="mb-4">
          <label htmlFor="description" className="block text-gray-700 text-sm font-bold mb-2">
            Description:
          </label>
          <textarea
            id="description"
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline h-24 resize-none"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            onBlur={fetchAiSuggestions}
            disabled={loading}
          ></textarea>
        </div>

        {/* AI Suggestions Display */}
        <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h3 className="text-lg font-semibold text-blue-800 mb-2">AI Suggestions:</h3>
          {aiLoading ? (
            <p className="text-blue-600">Getting AI suggestions...</p>
          ) : (
            <>
              <p className="text-sm text-blue-700">
                <strong>Priority:</strong> {aiPriority || 'N/A'} ({aiPriorityScore || 'N/A'})
              </p>
              <p className="text-sm text-blue-700">
                <strong>Deadline:</strong> {aiDeadline ? new Date(aiDeadline).toLocaleDateString() : 'N/A'}
              </p>
              <p className="text-sm text-blue-700">
                <strong>Categories:</strong> {aiCategories.length > 0 ? aiCategories.join(', ') : 'N/A'}
              </p>
              <p className="text-sm text-blue-700">
                <strong>Enhanced Description:</strong> {aiEnhancedDescription || 'N/A'}
              </p>
            </>
          )}
        </div>

        {/* ... (rest of the form remains the same) ... */}
        <div className="mb-4">
          <label htmlFor="status" className="block text-gray-700 text-sm font-bold mb-2">
            Status:
          </label>
          <select
            id="status"
            className="shadow border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            disabled={loading}
          >
            <option value="pending">Pending</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
          </select>
        </div>

        {/* Category */}
        <div className="mb-4">
          <label htmlFor="category" className="block text-gray-700 text-sm font-bold mb-2">
            Category:
          </label>
          {loadingCategories ? (
            <p className="text-gray-600">Loading categories...</p>
          ) : (
            <select
              id="category"
              className="shadow border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              disabled={loading}
            >
              <option value="">Select Category (Optional)</option>
              {categories.map((cat) => (
                <option key={cat.id} value={cat.id}>
                  {cat.name}
                </option>
              ))}
            </select>
          )}
        </div>

        {/* Deadline */}
        <div className="mb-6">
          <label htmlFor="deadline" className="block text-gray-700 text-sm font-bold mb-2">
            Deadline (YYYY-MM-DD):
          </label>
          <input
            type="date"
            id="deadline"
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            value={deadline}
            onChange={(e) => setDeadline(e.target.value)}
            disabled={loading}
          />
        </div>

        {/* Submit Button */}
        <div className="flex items-center justify-between">
          <button
            type="submit"
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={loading || !title.trim()}
          >
            {loading ? 'Saving...' : (initialTask?.id ? 'Update Task' : 'Create Task')}
          </button>
          {initialTask?.id && (
            <button
              type="button"
              onClick={() => router.push('/')}
              className="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline ml-4"
            >
              Cancel
            </button>
          )}
        </div>
        {error && <p className="text-red-500 text-xs italic mt-4">{error}</p>}
        {success && <p className="text-green-500 text-xs italic mt-4">{success}</p>}
      </form>
    </div>
  );
};

export default TaskForm;