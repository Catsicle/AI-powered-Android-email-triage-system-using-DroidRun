import { Email } from "@/types";
import { AlertCircle } from "lucide-react";

interface UrgentViewProps {
  emails: Email[];
}

export default function UrgentView({ emails }: UrgentViewProps) {
  if (emails.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64">
        <div className="text-6xl mb-4">✅</div>
        <h3 className="text-2xl font-semibold text-text-primary mb-2">No Urgent Items</h3>
        <p className="text-text-secondary">All caught up!</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6">
        <h2 className="text-3xl font-bold text-text-primary mb-2">Urgent</h2>
        <p className="text-text-secondary">{emails.length} items require immediate attention</p>
      </div>

      <div className="space-y-4">
        {emails.map((email) => (
          <div
            key={email.id}
            className="bg-bg-card rounded-xl border-l-4 border-accent-urgent border-r border-r-gray-800 border-y border-y-gray-800 overflow-hidden"
          >
            <div className="px-6 py-5">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 rounded-full bg-accent-urgent/20 flex items-center justify-center">
                    <AlertCircle size={20} className="text-accent-urgent" />
                  </div>
                  <div>
                    <div className="font-semibold text-text-primary">{email.sender}</div>
                    <div className="text-xs text-text-muted font-mono">{email.timestamp}</div>
                  </div>
                </div>
                <div className="px-3 py-1 bg-accent-urgent/10 rounded-full">
                  <span className="text-xs font-semibold text-accent-urgent uppercase">Urgent</span>
                </div>
              </div>

              <h3 className="text-lg font-semibold text-text-primary mb-2">
                {email.subject}
              </h3>
              <p className="text-text-secondary">{email.preview}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
