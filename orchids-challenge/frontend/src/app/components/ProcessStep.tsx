interface ProcessStepProps {
  number: number;
  title: string;
  description: string;
}

export const ProcessStep = ({ number, title, description }: ProcessStepProps) => {
  return (
    <div className="flex items-start space-x-4">
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-r from-purple-500 to-cyan-500 flex items-center justify-center text-white font-semibold">
        {number}
      </div>
      <div className="flex-1">
        <h3 className="text-lg font-semibold text-white mb-1">{title}</h3>
        <p className="text-slate-300 text-sm">{description}</p>
      </div>
    </div>
  );
};
