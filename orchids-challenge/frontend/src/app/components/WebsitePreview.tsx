'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

interface WebsitePreviewProps {
  jobId: string;
}

export default function WebsitePreview({ jobId }: WebsitePreviewProps) {
  const [html, setHtml] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchHtml = async () => {
      try {
        const response = await fetch(`http://localhost:8000/clone/${jobId}/html`);
        
        if (!response.ok) {
          throw new Error('Failed to fetch cloned website HTML');
        }
        
        const data = await response.json();
        setHtml(data.html);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching HTML:', error);
        setError('Failed to fetch cloned website');
        setLoading(false);
      }
    };

    fetchHtml();
  }, [jobId]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[300px]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        <p className="mt-4 text-gray-700 dark:text-gray-300">Loading cloned website...</p>
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

  return (
    <div className="flex flex-col w-full">
      <div className="bg-gray-200 dark:bg-gray-700 p-4 flex justify-between items-center mb-2 rounded-t-lg">
        <h2 className="text-lg font-semibold text-gray-800 dark:text-white">
          Cloned Website Preview
        </h2>
        <div className="space-x-2">
          <Link 
            href={`/status/${jobId}`} 
            className="inline-block px-3 py-1 bg-gray-600 text-white text-sm rounded hover:bg-gray-700"
          >
            Back to Status
          </Link>
          <Link 
            href="/" 
            className="inline-block px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
          >
            Clone Another
          </Link>
        </div>
      </div>
      <div className="w-full bg-white p-1 border border-gray-300 rounded-b-lg">
        <iframe
          srcDoc={html}
          className="w-full min-h-screen"
          title="Cloned Website"
        />
      </div>
    </div>
  );
}
