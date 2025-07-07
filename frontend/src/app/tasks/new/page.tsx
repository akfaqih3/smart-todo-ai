// app/tasks/new/page.tsx
import React from 'react';
import TaskForm from '../../components/TaskForm'; // Adjust path as needed

export default function NewTaskPage() {
  return (
    <div className="min-h-screen flex flex-col items-center p-8 bg-gray-100">
      <h1 className="text-4xl font-bold text-gray-800 mb-8">Create New Task</h1>
      <TaskForm /> {/* Render the TaskForm component */}
    </div>
  );
}
