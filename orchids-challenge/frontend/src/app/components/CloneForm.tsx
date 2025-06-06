'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function CloneForm() {
  const [url, setUrl] = useState('');
  const [model, setModel] = useState('claude');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    // Validate URL
    try {
      new URL(url); // This will throw an error if the URL is invalid
    } catch (error) {
      setError('Please enter a valid URL including http:// or https://');
      setIsLoading(false);
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/clone', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url,
          model,
        }),
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to start cloning process');
      }

      // Navigate to the job status page
      router.push(`/status/${data.job_id}`);
    } catch (error) {
      console.error('Error starting clone job:', error);
      setError('Failed to start cloning process. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md mx-auto bg-white dark:bg-gray-800 rounded-xl shadow-md overflow-hidden md:max-w-2xl p-6">
      <h2 className="text-xl font-semibold text-center mb-6 text-gray-800 dark:text-white">
        Clone Any Website
      </h2>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label 
            htmlFor="url" 
            className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
          >
            Website URL
          </label>
          <input
            id="url"
            type="text"
            placeholder="https://example.com"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            required
          />
        </div>

        <div>
          <label 
            htmlFor="model" 
            className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
          >
            AI Model
          </label>
          <select
            id="model"
            value={model}
            onChange={(e) => setModel(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
          >
            <option value="claude">Claude 4 Sonnet</option>
            <option value="gemini">Gemini 2.5 Pro</option>
          </select>
        </div>

        {error && (
          <div className="text-red-500 text-sm">{error}</div>
        )}

        <button
          type="submit"
          disabled={isLoading || !url}
          className={`w-full py-2 px-4 rounded-md text-white font-medium ${
            isLoading || !url 
              ? 'bg-blue-300 cursor-not-allowed' 
              : 'bg-blue-600 hover:bg-blue-700'
          }`}
        >
          {isLoading ? 'Processing...' : 'Clone Website'}
        </button>
      </form>
    </div>
  );
}
