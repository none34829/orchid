'use client';

import { useParams } from 'next/navigation';
import WebsitePreview from '../../components/WebsitePreview';
import Link from 'next/link';

export default function PreviewPage() {
  const params = useParams();
  const jobId = params.jobId as string;

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 py-4 px-2">
      <div className="max-w-7xl mx-auto">
        <header className="flex flex-col sm:flex-row items-center justify-between mb-4 px-4">
          <div className="flex items-center mb-4 sm:mb-0">
            <Link href="/" className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-800 dark:text-white">Orchids Website Cloner</h1>
            </Link>
          </div>
          
          <div className="flex space-x-4">
            <Link 
              href={`/status/${jobId}`}
              className="bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 px-4 py-2 rounded-md text-gray-800 dark:text-white"
            >
              Back to Status
            </Link>
            <Link 
              href="/"
              className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-md text-white"
            >
              Clone Another
            </Link>
          </div>
        </header>

        <WebsitePreview jobId={jobId} />
      </div>
    </div>
  );
}
