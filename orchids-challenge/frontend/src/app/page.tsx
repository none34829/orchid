import { CloneForm } from './components/CloneForm';
import { FeatureCard } from './components/FeatureCard';
import { ProcessStep } from './components/ProcessStep';
import { Globe, Zap, Monitor, Clock, CheckCircle, Sparkles } from 'lucide-react';

export default function Home() {
  const features = [
    {
      icon: <Globe className="w-6 h-6 text-purple-300" />,
      title: "Advanced Website Scraping",
      description: "Reliable scraping of website content, design elements, and structure with cutting-edge technology"
    },
    {
      icon: <Sparkles className="w-6 h-6 text-purple-300" />,
      title: "Choice of AI Models",
      description: "Select between Claude 4 Sonnet or Gemini 2.5 Pro for optimal results and perfect cloning"
    },
    {
      icon: <Monitor className="w-6 h-6 text-cyan-300" />,
      title: "Responsive Design",
      description: "Generated websites are responsive and look stunning on all devices and screen sizes"
    },
    {
      icon: <Zap className="w-6 h-6 text-cyan-300" />,
      title: "Fast Processing",
      description: "Lightning-fast background job processing with real-time status updates and notifications"
    }
  ];

  const steps = [
    {
      number: 1,
      title: "Enter the URL",
      description: "Provide the URL of any public website you want to clone"
    },
    {
      number: 2,
      title: "Select AI Model",
      description: "Choose your preferred AI model for optimal cloning results"
    },
    {
      number: 3,
      title: "AI Analysis",
      description: "Our AI scrapes and analyzes the website's design and structure"
    },
    {
      number: 4,
      title: "Generate Clone",
      description: "The AI creates a perfect clone with matching aesthetics"
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Background Effects */}
      <div className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg%20width%3D%2260%22%20height%3D%2260%22%20viewBox%3D%220%200%2060%2060%22%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%3E%3Cg%20fill%3D%22none%22%20fill-rule%3D%22evenodd%22%3E%3Cg%20fill%3D%22%239C92AC%22%20fill-opacity%3D%220.05%22%3E%3Ccircle%20cx%3D%2230%22%20cy%3D%2230%22%20r%3D%221%22/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')] opacity-40"></div>
      
      <div className="relative z-10">
        {/* Hero Section */}
        <header className="pt-20 pb-16 px-4">
          <div className="max-w-7xl mx-auto text-center">
            <div className="inline-flex items-center px-4 py-2 rounded-full bg-gradient-to-r from-purple-500/20 to-cyan-500/20 border border-purple-500/30 mb-8">
              <Sparkles className="w-4 h-4 text-purple-400 mr-2" />
              <span className="text-sm text-purple-300 font-medium">AI-Powered Website Cloning</span>
            </div>
            
            <h1 className="text-5xl md:text-7xl font-bold bg-gradient-to-r from-white via-purple-200 to-cyan-200 bg-clip-text text-transparent mb-6 leading-tight">
              Orchids Website
              <span className="block bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent">
                Cloner
              </span>
            </h1>
            
            <p className="text-xl md:text-2xl text-slate-300 max-w-3xl mx-auto mb-12 leading-relaxed">
              Clone any public website with AI. Provide a URL and our advanced AI will generate a 
              <span className="text-purple-400 font-semibold"> pixel-perfect website</span> with matching design aesthetics.
            </p>
          </div>
        </header>

        {/* Main Content */}
        <div className="px-4 pb-20">
          <div className="max-w-7xl mx-auto">
            <div className="grid lg:grid-cols-2 gap-12 mb-20">
              {/* Clone Form Section */}
              <div className="space-y-8">
                <CloneForm />
                
                {/* How It Works */}
                <div className="bg-slate-800/50 backdrop-blur-xl rounded-3xl p-8 border border-slate-700/50">
                  <h2 className="text-2xl font-bold text-white mb-6 flex items-center">
                    <Clock className="w-6 h-6 text-purple-400 mr-3" />
                    How It Works
                  </h2>
                  <div className="space-y-4">
                    {steps.map((step, index) => (
                      <ProcessStep key={index} {...step} />
                    ))}
                  </div>
                </div>
              </div>
              
              {/* Features Section */}
              <div>
                <div className="bg-slate-800/50 backdrop-blur-xl rounded-3xl p-8 border border-slate-700/50 h-full">
                  <h2 className="text-2xl font-bold text-white mb-8 flex items-center">
                    <CheckCircle className="w-6 h-6 text-cyan-400 mr-3" />
                    Premium Features
                  </h2>
                  
                  <div className="space-y-6">
                    {features.map((feature, index) => (
                      <FeatureCard key={index} {...feature} />
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Cloning Capabilities */}
            <div className="bg-gradient-to-r from-purple-600/20 to-cyan-600/20 rounded-3xl p-8 border border-purple-500/30 mb-20">
              <h2 className="text-2xl font-bold text-white mb-6 text-center">What We Can Clone</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                <div className="flex flex-col items-center bg-slate-800/60 rounded-xl p-4 hover:bg-slate-800/80 transition duration-200 border border-slate-700/50">
                  <div className="text-purple-400 mb-2 text-2xl font-bold">Layout</div>
                  <div className="text-slate-300 text-center text-sm">Precise positioning & grid systems</div>
                </div>
                <div className="flex flex-col items-center bg-slate-800/60 rounded-xl p-4 hover:bg-slate-800/80 transition duration-200 border border-slate-700/50">
                  <div className="text-cyan-400 mb-2 text-2xl font-bold">Style</div>
                  <div className="text-slate-300 text-center text-sm">Colors, fonts & animations</div>
                </div>
                <div className="flex flex-col items-center bg-slate-800/60 rounded-xl p-4 hover:bg-slate-800/80 transition duration-200 border border-slate-700/50">
                  <div className="text-purple-400 mb-2 text-2xl font-bold">Content</div>
                  <div className="text-slate-300 text-center text-sm">Text, images & media</div>
                </div>
                <div className="flex flex-col items-center bg-slate-800/60 rounded-xl p-4 hover:bg-slate-800/80 transition duration-200 border border-slate-700/50">
                  <div className="text-cyan-400 mb-2 text-2xl font-bold">Structure</div>
                  <div className="text-slate-300 text-center text-sm">Headers, nav & sections</div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Footer */}
        <footer className="border-t border-slate-700/50 py-8 px-4">
          <div className="max-w-7xl mx-auto text-center">
            <p className="text-slate-400">
              Orchids Website Cloner © {new Date().getFullYear()} | 
              <span className="text-purple-400 font-medium"> AI-powered website cloning technology</span>
            </p>
          </div>
        </footer>
      </div>
    </div>
  );
}
