'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export const CloneForm = () => {
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
    <div className="bg-slate-800/50 backdrop-blur-xl rounded-3xl p-8 border border-slate-700/50">
      <h2 className="text-2xl font-bold text-white mb-6">
        Clone Any Website
      </h2>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label 
            htmlFor="url" 
            className="block text-sm font-medium text-slate-300 mb-2"
          >
            Website URL
          </label>
          <input
            id="url"
            type="text"
            placeholder="https://example.com"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="w-full px-4 py-3 bg-slate-700/70 border border-slate-600/50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-purple-500 text-white placeholder-slate-400"
            required
          />
        </div>

        <div>
          <label 
            htmlFor="model" 
            className="block text-sm font-medium text-slate-300 mb-2"
          >
            AI Model
          </label>
          <select
            id="model"
            value={model}
            onChange={(e) => setModel(e.target.value)}
            className="w-full px-4 py-3 bg-slate-700/70 border border-slate-600/50 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-purple-500 text-white"
          >
            <option value="claude">Claude 4 Sonnet</option>
            <option value="gemini">Gemini 2.5 Pro</option>
          </select>
        </div>

        {error && (
          <div className="text-red-400 text-sm mt-2">{error}</div>
        )}

        <button
          type="submit"
          disabled={isLoading || !url}
          className={`w-full py-3 px-4 rounded-xl text-white font-medium ${
            isLoading || !url 
              ? 'bg-purple-500/50 cursor-not-allowed' 
              : 'bg-gradient-to-r from-purple-500 to-cyan-500 hover:from-purple-600 hover:to-cyan-600'
          } transition-all duration-200 shadow-lg`}
        >
          {isLoading ? 'Processing...' : 'Clone Website'}
        </button>
      </form>
    </div>
  );
}

export default CloneForm;
