import { ReactNode } from 'react';

interface FeatureCardProps {
  icon: ReactNode;
  title: string;
  description: string;
}

export const FeatureCard = ({ icon, title, description }: FeatureCardProps) => {
  return (
    <div className="flex items-start space-x-4 p-4 rounded-xl bg-slate-700/50 border border-slate-600/50 hover:bg-slate-700/70 transition duration-200">
      <div className="flex-shrink-0 p-2 bg-gradient-to-br from-purple-500/30 to-cyan-500/30 rounded-lg border border-purple-500/20">
        {icon}
      </div>
      <div className="flex-1">
        <h3 className="text-lg font-semibold text-white mb-1">{title}</h3>
        <p className="text-slate-300 text-sm">{description}</p>
      </div>
    </div>
  );
};
