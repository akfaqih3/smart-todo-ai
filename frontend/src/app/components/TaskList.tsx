// app/components/TaskList.tsx
'use client';

import Link from 'next/link';
import React, { useEffect, useState } from 'react';

interface Task {
  id: number;
  title: string;
  description: string;
  category: number;
  category_name: string;
  priority_score: string;
  priority: string;
  deadline: string;
  status: string;
  is_ai_suggested: boolean;
  created_at: string;
  updated_at: string;
}

// Define props for TaskList to accept filters
interface TaskListProps {
  filterCategory: string;
  filterStatus: string;
  filterPriority: string;
}

const TaskList: React.FC<TaskListProps> = ({ filterCategory, filterStatus, filterPriority }) => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Add a state to trigger re-fetch after completing a task
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  useEffect(() => {
    const fetchTasks = async () => {
      setLoading(true);
      setError(null);
      try {
        const queryParams = new URLSearchParams();
        if (filterCategory) {
          queryParams.append('category_id', filterCategory);
        }
        if (filterStatus) {
          queryParams.append('status', filterStatus);
        }
        if (filterPriority) {
          queryParams.append('priority', filterPriority);
        }

        const url = `http://localhost:8000/api/tasks/?${queryParams.toString( )}`;
        const response = await fetch(url);

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data: Task[] = await response.json();
        setTasks(data);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchTasks();
  }, [filterCategory, filterStatus, filterPriority, refreshTrigger]); // Add refreshTrigger to dependencies

  const handleCompleteTask = async (taskId: number) => {
    try {
      const response = await fetch(`http://localhost:8000/api/tasks/${taskId}/complete/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      } );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      // Trigger a re-fetch of tasks to update the list
      setRefreshTrigger(prev => prev + 1);
    } catch (err: any) {
      setError(`Failed to complete task: ${err.message}`);
    }
  };

  if (loading) {
    return <div className="text-center text-gray-600">Loading tasks...</div>;
  }

  if (error) {
    return <div className="text-center text-red-500">Error: {error}</div>;
  }

  return (
    <div className="w-full max-w-4xl mx-auto mt-8">
      <h2 className="text-3xl font-bold text-gray-800 mb-6 text-center">Your Tasks</h2>
      {tasks.length === 0 ? (
        <p className="text-center text-gray-600">No tasks found matching your criteria.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {tasks.map((task) => (
            <div key={task.id} className="bg-white shadow-lg rounded-lg p-6 border border-gray-200 flex flex-col">
              <h3 className="text-xl font-semibold text-gray-900 mb-2">{task.title}</h3>
              <p className="text-gray-700 text-sm mb-3 flex-grow">{task.description}</p>
              <div className="text-xs text-gray-500 mb-1">
                Category: <span className="font-medium text-gray-700">{task.category_name || 'N/A'}</span>
              </div>
              <div className="text-xs text-gray-500 mb-1">
                Priority: <span className={`font-medium ${task.priority === 'high' ? 'text-red-600' : task.priority === 'medium' ? 'text-yellow-600' : 'text-green-600'}`}>{task.priority} ({task.priority_score})</span>
              </div>
              <div className="text-xs text-gray-500 mb-1">
                Deadline: <span className="font-medium text-gray-700">{new Date(task.deadline).toLocaleDateString()}</span>
              </div>
              <div className="text-xs text-gray-500 mb-1">
                Status: <span className="font-medium text-gray-700">{task.status}</span>
              </div>
              {task.is_ai_suggested && (
                <div className="text-xs text-blue-500 mt-2">AI Suggested</div>
              )}
              <div className="mt-4 flex justify-end gap-2"> {/* Added gap-2 for spacing */}
                {task.status !== 'completed' && ( // Only show complete button if not completed
                  <button
                    onClick={() => handleCompleteTask(task.id)}
                    className="bg-green-500 hover:bg-green-600 text-white text-sm font-bold py-1 px-3 rounded focus:outline-none focus:shadow-outline"
                    disabled={loading}
                  >
                    Complete
                  </button>
                )}
                <Link href={`/tasks/${task.id}`} className="bg-yellow-500 hover:bg-yellow-600 text-white text-sm font-bold py-1 px-3 rounded focus:outline-none focus:shadow-outline">
                  Edit
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default TaskList;