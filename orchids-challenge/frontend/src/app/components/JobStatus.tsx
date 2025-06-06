'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

interface JobStatusProps {
  jobId: string;
}

interface JobData {
  job_id: string;
  status: string;
  message: string;
  url: string;
  model: string | null;
  started_at: string | null;
  completed_at: string | null;
  result?: {
    html: string;
    model_used: string;
  };
}

export default function JobStatus({ jobId }: JobStatusProps) {
  const [jobData, setJobData] = useState<JobData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchJobStatus = async () => {
      try {
        const response = await fetch(`http://localhost:8000/jobs/${jobId}`);
        
        if (!response.ok) {
          throw new Error('Failed to fetch job status');
        }
        
        const data = await response.json();
        setJobData(data);
        setLoading(false);
        
        // If job is still processing, poll for updates
        if (['pending', 'scraping', 'generating'].includes(data.status)) {
          setTimeout(() => fetchJobStatus(), 2000);
        }
      } catch (error) {
        console.error('Error fetching job status:', error);
        setError('Failed to fetch job status');
        setLoading(false);
      }
    };

    fetchJobStatus();
  }, [jobId]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[300px]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        <p className="mt-4 text-gray-700 dark:text-gray-300">Loading job status...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 dark:bg-red-900 border border-red-400 dark:border-red-700 text-red-700 dark:text-red-200 px-4 py-3 rounded relative">
        <p>{error}</p>
        <Link href="/" className="mt-4 inline-block text-blue-500 hover:underline">
          Back to Home
        </Link>
      </div>
    );
  }

  if (!jobData) {
    return (
      <div className="bg-yellow-100 dark:bg-yellow-900 border border-yellow-400 dark:border-yellow-700 text-yellow-700 dark:text-yellow-200 px-4 py-3 rounded relative">
        <p>Job not found</p>
        <Link href="/" className="mt-4 inline-block text-blue-500 hover:underline">
          Back to Home
        </Link>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 w-full max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold mb-4 text-gray-800 dark:text-white">Website Clone Status</h2>
      
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row justify-between">
          <div className="mb-2 sm:mb-0">
            <span className="text-sm text-gray-500 dark:text-gray-400">Job ID:</span>
            <p className="font-mono text-sm">{jobData.job_id}</p>
          </div>
          <div>
            <span className="text-sm text-gray-500 dark:text-gray-400">Website:</span>
            <p className="font-mono text-sm truncate max-w-xs">{jobData.url}</p>
          </div>
        </div>
        
        <div className="flex justify-between">
          <div>
            <span className="text-sm text-gray-500 dark:text-gray-400">Status:</span>
            <p className={`
              font-semibold 
              ${jobData.status === 'completed' ? 'text-green-600 dark:text-green-400' : ''} 
              ${jobData.status === 'failed' ? 'text-red-600 dark:text-red-400' : ''} 
              ${['pending', 'scraping', 'generating'].includes(jobData.status) ? 'text-blue-600 dark:text-blue-400' : ''}
            `}>
              {jobData.status.charAt(0).toUpperCase() + jobData.status.slice(1)}
            </p>
          </div>
          <div>
            <span className="text-sm text-gray-500 dark:text-gray-400">Model:</span>
            <p>{jobData.model || 'Default'}</p>
          </div>
        </div>
        
        <div>
          <span className="text-sm text-gray-500 dark:text-gray-400">Message:</span>
          <p className="text-gray-800 dark:text-gray-200">{jobData.message}</p>
        </div>
        
        {jobData.started_at && (
          <div>
            <span className="text-sm text-gray-500 dark:text-gray-400">Started At:</span>
            <p className="text-gray-800 dark:text-gray-200">{new Date(jobData.started_at).toLocaleString()}</p>
          </div>
        )}
        
        {jobData.completed_at && (
          <div>
            <span className="text-sm text-gray-500 dark:text-gray-400">Completed At:</span>
            <p className="text-gray-800 dark:text-gray-200">{new Date(jobData.completed_at).toLocaleString()}</p>
          </div>
        )}
        
        {jobData.status === 'pending' || jobData.status === 'scraping' || jobData.status === 'generating' ? (
          <div className="flex flex-col items-center mt-6">
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
              <div 
                className="bg-blue-600 h-2.5 rounded-full animate-pulse" 
                style={{ 
                  width: jobData.status === 'pending' ? '25%' : 
                         jobData.status === 'scraping' ? '50%' : 
                         jobData.status === 'generating' ? '75%' : '100%' 
                }}
              ></div>
            </div>
            <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
              {jobData.status === 'pending' ? 'Starting job...' : 
               jobData.status === 'scraping' ? 'Scraping website...' : 
               jobData.status === 'generating' ? 'Generating clone with AI...' : ''}
            </p>
          </div>
        ) : null}
        
        {jobData.status === 'completed' && (
          <div className="flex flex-col sm:flex-row justify-center space-y-2 sm:space-y-0 sm:space-x-4 mt-6">
            <Link 
              href={`/preview/${jobData.job_id}`}
              className="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 text-center"
            >
              View Cloned Website
            </Link>
            <Link 
              href="/"
              className="bg-gray-600 text-white py-2 px-4 rounded-md hover:bg-gray-700 text-center"
            >
              Clone Another Website
            </Link>
          </div>
        )}
        
        {jobData.status === 'failed' && (
          <div className="flex justify-center mt-6">
            <Link 
              href="/"
              className="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700"
            >
              Try Again
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
