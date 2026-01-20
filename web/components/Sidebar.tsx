import { Inbox, AlertCircle, Calendar, Info, Trash2, LayoutDashboard } from "lucide-react";

interface SidebarProps {
  currentView: string;
  onNavigate: (view: any) => void;
}

export default function Sidebar({ currentView, onNavigate }: SidebarProps) {
  const navItems = [
    { id: "dashboard", icon: LayoutDashboard, label: "Dashboard" },
    { id: "decisions", icon: Inbox, label: "Decisions", color: "accent-decisions" },
    { id: "urgent", icon: AlertCircle, label: "Urgent", color: "accent-urgent" },
    { id: "calendar", icon: Calendar, label: "Calendar", color: "accent-calendar" },
    { id: "info", icon: Info, label: "Info", color: "accent-info" },
    { id: "spam", icon: Trash2, label: "Spam", color: "accent-spam" },
  ];

  return (
    <div className="w-20 bg-bg-secondary flex flex-col items-center py-6 space-y-6 border-r border-gray-800">
      {/* Logo */}
      <div className="w-12 h-12 rounded-xl bg-accent-decisions flex items-center justify-center font-bold text-xl">
        IP
      </div>

      {/* Navigation */}
      <nav className="flex-1 flex flex-col space-y-4 mt-8">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentView === item.id;
          
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={`
                relative w-12 h-12 rounded-lg flex items-center justify-center
                transition-all duration-200
                ${isActive 
                  ? `bg-${item.color || "accent-decisions"} text-white` 
                  : "text-text-secondary hover:text-text-primary hover:bg-bg-card"
                }
              `}
              title={item.label}
            >
              <Icon size={20} />
              {isActive && (
                <div className="absolute left-0 w-1 h-8 bg-white rounded-r"></div>
              )}
            </button>
          );
        })}
      </nav>
    </div>
  );
}
