import { TrendingUp, TrendingDown } from "lucide-react";

interface MetricCardProps {
  category: string;
  count: number;
  label: string;
  color: string;
  icon: string;
  trend?: number;
  featured?: boolean;
  onClick: () => void;
}

export default function MetricCard({
  count,
  label,
  color,
  icon,
  trend,
  featured,
  onClick,
}: MetricCardProps) {
  return (
    <button
      onClick={onClick}
      className={`
        relative p-6 rounded-xl transition-all duration-200
        bg-bg-card border border-gray-800
        hover:border-${color} hover:scale-105
        ${featured ? "ring-2 ring-accent-decisions/50 scale-105" : ""}
      `}
    >
      {/* Icon */}
      <div className="text-3xl mb-3">{icon}</div>
      
      {/* Count */}
      <div className="text-4xl font-bold text-text-primary mb-2">
        {count}
      </div>
      
      {/* Label */}
      <div className="text-sm text-text-secondary uppercase tracking-wide">
        {label}
      </div>
      
      {/* Trend Indicator */}
      {trend !== undefined && (
        <div className={`
          absolute top-4 right-4 flex items-center space-x-1
          ${trend > 0 ? "text-accent-urgent" : "text-accent-safe"}
        `}>
          {trend > 0 ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
          <span className="text-xs font-mono">{Math.abs(trend)}</span>
        </div>
      )}
      
      {/* Featured Badge */}
      {featured && (
        <div className="absolute bottom-4 right-4">
          <div className="w-2 h-2 rounded-full bg-accent-decisions animate-pulse"></div>
        </div>
      )}
    </button>
  );
}
