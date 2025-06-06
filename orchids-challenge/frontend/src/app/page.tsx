import Image from "next/image";
import CloneForm from "./components/CloneForm";

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 py-10 px-4">
      <div className="max-w-6xl mx-auto">
        <header className="flex flex-col items-center justify-center mb-12">
          <div className="flex items-center mb-6">
            <h1 className="text-3xl md:text-4xl font-bold text-gray-800 dark:text-white">Orchids Website Cloner</h1>
          </div>
          <p className="text-lg text-center max-w-2xl text-gray-600 dark:text-gray-300">
            Clone any public website with AI. Provide a URL and our AI will generate a
            similar looking website with matching design aesthetics.
          </p>
        </header>

        <div className="flex flex-col md:flex-row gap-8">
          <div className="w-full md:w-1/2">
            <CloneForm />
            
            <div className="mt-12 bg-white dark:bg-gray-800 rounded-xl shadow-md p-6">
              <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-white">How It Works</h2>
              <ol className="list-decimal list-inside text-gray-700 dark:text-gray-300 space-y-3">
                <li>Enter the URL of any public website</li>
                <li>Select an AI model for generating the clone</li>
                <li>Wait while we scrape the website and analyze its design</li>
                <li>The AI generates a cloned version of the website</li>
                <li>View and interact with your cloned website</li>
              </ol>
            </div>
          </div>
          
          <div className="w-full md:w-1/2">
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6 h-full">
              <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-white">Features</h2>
              
              <div className="space-y-4">
                <div className="flex items-start">
                  <div className="flex-shrink-0 h-6 w-6 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4 text-blue-600 dark:text-blue-400">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div className="ml-4">
                    <h3 className="text-lg font-medium text-gray-800 dark:text-white">Advanced Website Scraping</h3>
                    <p className="mt-1 text-gray-600 dark:text-gray-400">Reliable scraping of website content, design elements, and structure</p>
                  </div>
                </div>
                
                <div className="flex items-start">
                  <div className="flex-shrink-0 h-6 w-6 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4 text-blue-600 dark:text-blue-400">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div className="ml-4">
                    <h3 className="text-lg font-medium text-gray-800 dark:text-white">Choice of AI Models</h3>
                    <p className="mt-1 text-gray-600 dark:text-gray-400">Select between Claude 4 Sonnet or Gemini 2.5 Pro for optimal results</p>
                  </div>
                </div>
                
                <div className="flex items-start">
                  <div className="flex-shrink-0 h-6 w-6 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4 text-blue-600 dark:text-blue-400">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div className="ml-4">
                    <h3 className="text-lg font-medium text-gray-800 dark:text-white">Responsive Design</h3>
                    <p className="mt-1 text-gray-600 dark:text-gray-400">Generated websites are responsive and look great on all devices</p>
                  </div>
                </div>
                
                <div className="flex items-start">
                  <div className="flex-shrink-0 h-6 w-6 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4 text-blue-600 dark:text-blue-400">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div className="ml-4">
                    <h3 className="text-lg font-medium text-gray-800 dark:text-white">Fast Processing</h3>
                    <p className="mt-1 text-gray-600 dark:text-gray-400">Background job processing with real-time status updates</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <footer className="mt-16 text-center text-gray-500 dark:text-gray-400">
        <p>Orchids Website Cloner &copy; {new Date().getFullYear()} | AI-powered website cloning</p>
      </footer>
    </div>
  );
}
