import React from 'react';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  color?: 'blue' | 'red' | 'yellow' | 'green' | 'purple';
  icon?: React.ReactNode;
}

const StatCard: React.FC<StatCardProps> = ({ 
  title, 
  value, 
  subtitle, 
  color = 'blue',
  icon 
}) => {
  const colorClasses = {
    blue: 'border-primary-500 bg-primary-500/10',
    red: 'border-danger-500 bg-danger-500/10',
    yellow: 'border-warning-500 bg-warning-500/10',
    green: 'border-success-500 bg-success-500/10',
    purple: 'border-purple-500 bg-purple-500/10',
  };

  return (
    <div className={`p-6 rounded-lg border-2 ${colorClasses[color]} backdrop-blur-sm`}>
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-medium text-dark-muted">{title}</h3>
        {icon && <div className="text-2xl">{icon}</div>}
      </div>
      <div className="text-3xl font-bold text-dark-text mb-1">{value}</div>
      {subtitle && <p className="text-xs text-dark-muted">{subtitle}</p>}
    </div>
  );
};

export default StatCard;
