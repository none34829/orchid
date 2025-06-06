'use client';

import { useParams } from 'next/navigation';
import JobStatus from '../../components/JobStatus';
import Link from 'next/link';

export default function StatusPage() {
  const params = useParams();
  const jobId = params.jobId as string;

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 py-10 px-4">
      <div className="max-w-6xl mx-auto">
        <header className="flex flex-col items-center justify-center mb-12">
          <div className="flex items-center mb-6">
            <Link href="/" className="flex items-center">
              <h1 className="text-3xl md:text-4xl font-bold text-gray-800 dark:text-white">Orchids Website Cloner</h1>
            </Link>
          </div>
          <p className="text-lg text-center max-w-2xl text-gray-600 dark:text-gray-300">
            Website Cloning Job Status
          </p>
        </header>

        <JobStatus jobId={jobId} />

        <div className="mt-8 text-center">
          <Link 
            href="/" 
            className="text-blue-600 hover:underline"
          >
            ← Back to Home
          </Link>
        </div>
      </div>
    </div>
  );
}
