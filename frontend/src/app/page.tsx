// app/page.tsx

'use client';

import React, { useState, useCallback, useEffect } from 'react'; // Import useEffect
import TaskList from './components/TaskList';
import AddTaskForm from './components/AddTaskForm';
import Link from 'next/link';

// Define Category interface
interface Category {
  id: number;
  name: string;
  usage_count: number;
}

export default function Home( ) {
  const [refreshTasks, setRefreshTasks] = useState(0);
  const [filterCategory, setFilterCategory] = useState<string>('');
  const [filterStatus, setFilterStatus] = useState<string>('');
  const [filterPriority, setFilterPriority] = useState<string>('');
  const [categories, setCategories] = useState<Category[]>([]); // New state for categories
  const [categoriesLoading, setCategoriesLoading] = useState<boolean>(true);
  const [categoriesError, setCategoriesError] = useState<string | null>(null);


  // Fetch categories on component mount
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
        setCategoriesError(err.message);
      } finally {
        setCategoriesLoading(false);
      }
    };

    fetchCategories();
  }, []); // Runs once on mount

  const handleTaskAdded = useCallback(() => {
    setRefreshTasks(prev => prev + 1);
    // Optionally, re-fetch categories if a new one might have been created by AI
    // setCategoriesLoading(true);
    // fetchCategories(); // This would require making fetchCategories a separate function or wrapping it
  }, []);

  const handleCategoryChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setFilterCategory(e.target.value);
    setRefreshTasks(prev => prev + 1);
  };

  const handleStatusChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setFilterStatus(e.target.value);
    setRefreshTasks(prev => prev + 1);
  };

  const handlePriorityChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setFilterPriority(e.target.value);
    setRefreshTasks(prev => prev + 1);
  };

  return (
    <main className="flex min-h-screen flex-col items-center p-8 bg-gray-100">
      <h1 className="text-4xl font-bold text-center text-gray-800 mb-8">
        Smart Todo List
      </h1>
       {/* Navigation Links */}
      <div className="mb-8 flex gap-4">
        <Link href="/tasks/new" className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline">
          Create New Task
        </Link>
        <Link href="/context" className="bg-purple-500 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline">
          Manage Context
        </Link>
      </div>

      <AddTaskForm onTaskAdded={handleTaskAdded} />

      {/* Filter Controls */}
      
    <div className="w-full max-w-4xl mx-auto mb-8 p-6 bg-white shadow-lg rounded-lg border border-gray-200 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {/* Category Filter */}
      <div className="flex flex-col"> {/* Use flex-col for label and select */}
        <label htmlFor="categoryFilter" className="block text-gray-700 text-sm font-bold mb-2">
          Filter by Category:
        </label>
        {categoriesLoading ? (
          <p className="text-gray-600">Loading categories...</p>
        ) : categoriesError ? (
          <p className="text-red-500">Error loading categories: {categoriesError}</p>
        ) : (
          <select
            id="categoryFilter"
            className="shadow border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline w-full" // Added w-full
            value={filterCategory}
            onChange={handleCategoryChange}
          >
            <option value="">All Categories</option>
            {categories.map((cat) => (
              <option key={cat.id} value={cat.id}>
                {cat.name}
              </option>
            ))}
          </select>
        )}
      </div>

      {/* Status Filter */}
      <div className="flex flex-col"> {/* Use flex-col for label and select */}
        <label htmlFor="statusFilter" className="block text-gray-700 text-sm font-bold mb-2">
          Filter by Status:
        </label>
        <select
          id="statusFilter"
          className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" // Added w-full
          value={filterStatus}
          onChange={handleStatusChange}
        >
          <option value="">All Statuses</option>
          <option value="pending">Pending</option>
          <option value="completed">Completed</option>
          <option value="in_progress">In Progress</option>
        </select>
      </div>

      {/* Priority Filter */}
      <div className="flex flex-col"> {/* Use flex-col for label and select */}
        <label htmlFor="priorityFilter" className="block text-gray-700 text-sm font-bold mb-2">
          Filter by Priority:
        </label>
        <select
          id="priorityFilter"
          className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" // Added w-full
          value={filterPriority}
          onChange={handlePriorityChange}
        >
          <option value="">All Priorities</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
      </div>
    </div>

      <TaskList
        key={refreshTasks}
        filterCategory={filterCategory}
        filterStatus={filterStatus}
        filterPriority={filterPriority}
      />
    </main>
  );
}
