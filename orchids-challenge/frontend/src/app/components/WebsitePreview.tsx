'use client';

import { useState, useEffect } from 'react';

interface WebsitePreviewProps {
  jobId: string;
}

export default function WebsitePreview({ jobId }: WebsitePreviewProps) {
  const [previewHtml, setPreviewHtml] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    const fetchPreview = async () => {
      try {
        setLoading(true);
        const response = await fetch(`/api/clone/${jobId}`);
        
        if (!response.ok) {
          throw new Error(`Failed to fetch preview: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (data.html) {
          setPreviewHtml(data.html);
        } else {
          throw new Error('No HTML content available');
        }
      } catch (err) {
        console.error('Error fetching preview:', err);
        setError(err instanceof Error ? err.message : 'Failed to load preview');
      } finally {
        setLoading(false);
      }
    };
    
    fetchPreview();
  }, [jobId]);
  
  if (loading) {
    return (
      <div className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md">
        <div className="flex flex-col items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-300">Loading website preview...</p>
        </div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md">
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <div className="rounded-full bg-red-100 p-3 dark:bg-red-900/20 mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-red-500" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">Failed to load preview</h3>
          <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">{error}</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md">
      <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-white">Website Preview</h2>
      <div className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
        <div className="bg-gray-100 dark:bg-gray-700 p-2 flex items-center space-x-2">
          <div className="flex space-x-1">
            <div className="w-3 h-3 rounded-full bg-red-500"></div>
            <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
            <div className="w-3 h-3 rounded-full bg-green-500"></div>
          </div>
          <div className="text-xs text-gray-500 dark:text-gray-400 flex-1 text-center">Preview</div>
        </div>
        <div className="relative" style={{ height: '75vh' }}>
          {previewHtml && (
            <iframe
              srcDoc={previewHtml}
              className="w-full h-full"
              title="Website Preview"
              sandbox="allow-same-origin allow-scripts"
            />
          )}
        </div>
      </div>
      <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
        This is a static preview of the cloned website. Some interactive elements may not work as expected.
      </p>
    </div>
  );
}
