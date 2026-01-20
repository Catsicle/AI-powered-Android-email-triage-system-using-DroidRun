import { EmailData } from "@/types";
import MetricCard from "./MetricCard";

type View = "dashboard" | "decisions" | "spam" | "urgent" | "info" | "calendar";

interface DashboardProps {
  emailData: EmailData;
  onNavigate: (view: View) => void;
}

export default function Dashboard({ emailData, onNavigate }: DashboardProps) {
  const metrics = [
    {
      category: "urgent" as const,
      count: emailData.urgent.length,
      label: "Urgent",
      color: "accent-urgent",
      icon: "⚠️",
    },
    {
      category: "decisions" as const,
      count: emailData.decisions.length,
      label: "Decisions",
      color: "accent-decisions",
      icon: "📋",
      featured: true,
    },
    {
      category: "calendar" as const,
      count: emailData.calendar.length,
      label: "Calendar",
      color: "accent-calendar",
      icon: "📅",
    },
    {
      category: "info" as const,
      count: emailData.info.length,
      label: "Info",
      color: "accent-info",
      icon: "ℹ️",
    },
    {
      category: "spam" as const,
      count: emailData.spam.length,
      label: "Spam",
      color: "accent-spam",
      icon: "🗑️",
    },
  ];

  return (
    <div className="space-y-8">
      {/* Hero Section - The HUD */}
      <section>
        <h2 className="text-3xl font-bold mb-6 text-text-primary">Command Center</h2>
        
        <div className="grid grid-cols-5 gap-4">
          {metrics.map((metric) => (
            <MetricCard
              key={metric.category}
              {...metric}
              onClick={() => onNavigate(metric.category)}
            />
          ))}
        </div>
      </section>

      {/* Quick Action Section */}
      <section className="bg-bg-card rounded-xl p-6 border border-gray-800">
        <h3 className="text-xl font-semibold mb-4">Quick Actions</h3>
        
        <div className="grid grid-cols-3 gap-4">
          <button
            onClick={() => onNavigate("decisions")}
            className="p-4 bg-accent-decisions/10 hover:bg-accent-decisions/20 rounded-lg border border-accent-decisions/30 transition-colors"
          >
            <div className="text-2xl mb-2">📋</div>
            <div className="text-sm font-medium text-text-primary">Process Decisions</div>
            <div className="text-xs text-text-secondary mt-1">
              {emailData.decisions.length} items pending
            </div>
          </button>

          <button
            onClick={() => onNavigate("spam")}
            className="p-4 bg-accent-spam/10 hover:bg-accent-spam/20 rounded-lg border border-accent-spam/30 transition-colors"
          >
            <div className="text-2xl mb-2">🗑️</div>
            <div className="text-sm font-medium text-text-primary">Review Spam</div>
            <div className="text-xs text-text-secondary mt-1">
              {emailData.spam.length} items quarantined
            </div>
          </button>

          <button
            onClick={() => onNavigate("urgent")}
            className="p-4 bg-accent-urgent/10 hover:bg-accent-urgent/20 rounded-lg border border-accent-urgent/30 transition-colors"
          >
            <div className="text-2xl mb-2">⚠️</div>
            <div className="text-sm font-medium text-text-primary">Check Urgent</div>
            <div className="text-xs text-text-secondary mt-1">
              {emailData.urgent.length} items require attention
            </div>
          </button>
        </div>
      </section>

      {/* Status Footer */}
      {emailData.decisions.length === 0 && emailData.spam.length === 0 && (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">✨</div>
          <h3 className="text-2xl font-semibold text-text-primary mb-2">All Caught Up</h3>
          <p className="text-text-secondary">DroidRun is sleeping.</p>
        </div>
      )}
    </div>
  );
}
