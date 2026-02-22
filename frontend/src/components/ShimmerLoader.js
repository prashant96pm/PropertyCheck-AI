import React from 'react';

const ShimmerLoader = ({ className = '', variant = 'default' }) => {
  if (variant === 'card') {
    return (
      <div className={`glass-card ${className}`}>
        <div className="space-y-4">
          <div className="shimmer h-4 w-3/4 rounded-lg" />
          <div className="shimmer h-4 w-1/2 rounded-lg" />
          <div className="shimmer h-20 w-full rounded-lg" />
          <div className="flex gap-4">
            <div className="shimmer h-8 w-20 rounded-lg" />
            <div className="shimmer h-8 w-20 rounded-lg" />
          </div>
        </div>
      </div>
    );
  }
  
  if (variant === 'stat') {
    return (
      <div className={`glass-card ${className}`}>
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <div className="shimmer h-3 w-16 rounded-lg" />
            <div className="shimmer h-8 w-12 rounded-lg" />
          </div>
          <div className="shimmer h-12 w-12 rounded-lg" />
        </div>
      </div>
    );
  }
  
  if (variant === 'table') {
    return (
      <div className={`space-y-3 ${className}`}>
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="shimmer h-16 w-full rounded-lg" />
        ))}
      </div>
    );
  }
  
  if (variant === 'risk-meter') {
    return (
      <div className={`flex items-center justify-center ${className}`}>
        <div className="relative">
          <div className="shimmer h-48 w-48 rounded-full" />
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="shimmer h-16 w-16 rounded-lg" />
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div className={`shimmer h-4 w-full rounded-lg ${className}`} />
  );
};

export default ShimmerLoader;
