// app/tasks/[id]/page.tsx
'use client'; // This page needs to be a client component to use useEffect and useState

import React, { useEffect, useState } from 'react';
import TaskForm from '../../components/TaskForm'; // Adjust path as needed

interface Task {
  id: number;
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

interface TaskDetailPageProps {
  params: {
    id: string; // The ID from the dynamic route
  };
}

export default function TaskDetailPage({ params }: TaskDetailPageProps) {
  const taskId = params.id;
  const [task, setTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTask = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/tasks/${taskId}/` );
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data: Task = await response.json();
        setTask(data);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchTask();
  }, [taskId]); // Re-fetch if taskId changes

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center text-gray-600">Loading task details...</div>;
  }

  if (error) {
    return <div className="min-h-screen flex items-center justify-center text-red-500">Error: {error}</div>;
  }

  if (!task) {
    return <div className="min-h-screen flex items-center justify-center text-gray-600">Task not found.</div>;
  }

  return (
    <div className="min-h-screen flex flex-col items-center p-8 bg-gray-100">
      <h1 className="text-4xl font-bold text-gray-800 mb-8">Edit Task</h1>
      <TaskForm initialTask={task} onTaskSubmitted={() => console.log('Task updated!')} />
    </div>
  );
}
