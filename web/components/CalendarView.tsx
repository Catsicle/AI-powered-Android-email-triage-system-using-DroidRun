import { Email } from "@/types";
import { Calendar as CalendarIcon } from "lucide-react";

interface CalendarViewProps {
  emails: Email[];
}

export default function CalendarView({ emails }: CalendarViewProps) {
  if (emails.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64">
        <div className="text-6xl mb-4">📅</div>
        <h3 className="text-2xl font-semibold text-text-primary mb-2">No Calendar Items</h3>
        <p className="text-text-secondary">No upcoming events</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6">
        <h2 className="text-3xl font-bold text-text-primary mb-2">Calendar</h2>
        <p className="text-text-secondary">{emails.length} meeting invites and scheduling requests</p>
      </div>

      {/* Timeline View */}
      <div className="relative">
        {/* Timeline Line */}
        <div className="absolute left-[21px] top-0 bottom-0 w-0.5 bg-accent-calendar/30"></div>

        <div className="space-y-6">
          {emails.map((email, index) => (
            <div key={email.id} className="relative pl-12">
              {/* Timeline Dot */}
              <div className="absolute left-0 w-11 h-11 rounded-full bg-accent-calendar/20 border-2 border-accent-calendar flex items-center justify-center">
                <CalendarIcon size={18} className="text-accent-calendar" />
              </div>

              {/* Event Card */}
              <div className="bg-bg-card rounded-xl border border-gray-800 overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-800 bg-accent-calendar/5">
                  <div className="flex justify-between items-center">
                    <div>
                      <div className="font-semibold text-text-primary">{email.sender}</div>
                      <div className="text-xs text-text-muted font-mono mt-1">{email.timestamp}</div>
                    </div>
                    <div className="px-3 py-1 bg-accent-calendar/20 rounded-full">
                      <span className="text-xs font-semibold text-accent-calendar uppercase">Meeting</span>
                    </div>
                  </div>
                </div>

                <div className="px-6 py-4">
                  <h3 className="text-lg font-semibold text-text-primary mb-2">
                    {email.subject}
                  </h3>
                  <p className="text-text-secondary">{email.preview}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
