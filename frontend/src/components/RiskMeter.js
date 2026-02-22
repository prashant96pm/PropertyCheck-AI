import React from 'react';

const RiskMeter = ({ score, size = 200 }) => {
  const radius = (size - 20) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = (score / 100) * circumference;
  const strokeDashoffset = circumference - progress;
  
  // Determine color based on score
  const getColor = () => {
    if (score >= 75) return { stroke: '#10b981', glow: 'risk-meter-glow-green', label: 'SAFE', bg: 'rgba(16, 185, 129, 0.1)' };
    if (score >= 50) return { stroke: '#f59e0b', glow: 'risk-meter-glow-orange', label: 'CAUTION', bg: 'rgba(245, 158, 11, 0.1)' };
    return { stroke: '#ef4444', glow: 'risk-meter-glow-red', label: 'HIGH RISK', bg: 'rgba(239, 68, 68, 0.1)' };
  };
  
  const colorConfig = getColor();
  
  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      {/* Background glow effect */}
      <div 
        className="absolute inset-0 rounded-full blur-xl opacity-50"
        style={{ background: colorConfig.bg }}
      />
      
      {/* SVG Ring */}
      <svg className={`risk-meter-ring ${colorConfig.glow}`} width={size} height={size}>
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="rgba(148, 163, 184, 0.1)"
          strokeWidth="12"
        />
        {/* Progress circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={colorConfig.stroke}
          strokeWidth="12"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          style={{
            filter: `drop-shadow(0 0 10px ${colorConfig.stroke})`,
            transition: 'stroke-dashoffset 1s ease-out'
          }}
        />
      </svg>
      
      {/* Center content */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span 
          className="text-4xl md:text-5xl font-bold font-mono"
          style={{ 
            color: colorConfig.stroke,
            textShadow: `0 0 20px ${colorConfig.stroke}`
          }}
        >
          {score}
        </span>
        <span className="text-xs text-slate-400 uppercase tracking-widest mt-1">
          /100
        </span>
        <span 
          className="text-xs font-semibold uppercase tracking-wider mt-2 px-3 py-1 rounded-full"
          style={{ 
            color: colorConfig.stroke,
            background: colorConfig.bg,
            border: `1px solid ${colorConfig.stroke}40`
          }}
        >
          {colorConfig.label}
        </span>
      </div>
    </div>
  );
};

export default RiskMeter;
