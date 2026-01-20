import { formatDistanceToNow } from "date-fns";
import { useState } from "react";

interface HeaderProps {
  isLive: boolean;
  lastSync: Date;
  onRefresh?: () => void;
}

export default function Header({ isLive, lastSync, onRefresh }: HeaderProps) {
  const [isScanning, setIsScanning] = useState(false);
  const [isRecategorizing, setIsRecategorizing] = useState(false);
  const [isScheduling, setIsScheduling] = useState(false);

  const handleScanInbox = async () => {
    setIsScanning(true);
    try {
      const response = await fetch("/api/emails/scan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ max_emails: 10 }),
      });
      const data = await response.json();
      
      if (!response.ok) {
        // Handle HTTP error responses
        alert("❌ Scan failed: " + (data.detail || data.message || "Unknown error"));
      } else if (data.success) {
        alert(`✅ Scanned ${data.stats.processed} emails!`);
        onRefresh?.();
      } else {
        alert("❌ Scan failed: " + (data.message || "Unknown error"));
      }
    } catch (error) {
      alert("❌ Error scanning inbox: " + (error as Error).message);
    } finally {
      setIsScanning(false);
    }
  };

  const handleRecategorize = async () => {
    setIsRecategorizing(true);
    try {
      const response = await fetch("/api/emails/recategorize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
      const data = await response.json();
      
      if (!response.ok) {
        alert("❌ Recategorization failed: " + (data.detail || data.message || "Unknown error"));
      } else if (data.success) {
        alert(`✅ Recategorized ${data.stats.total} emails!`);
        onRefresh?.();
      } else {
        alert("❌ Recategorization failed: " + (data.message || "Unknown error"));
      }
    } catch (error) {
      alert("❌ Error: " + (error as Error).message);
    } finally {
      setIsRecategorizing(false);
    }
  };

  const handleScheduleEvents = async () => {
    setIsScheduling(true);
    try {
      const response = await fetch("/api/scheduler/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ delay: 1.5 }),
      });
      const data = await response.json();
      
      if (!response.ok) {
        alert("❌ Scheduling failed: " + (data.detail || data.message || "Unknown error"));
      } else if (data.success) {
        alert(`✅ Scheduled ${data.stats.succeeded}/${data.stats.total} events!`);
        onRefresh?.();
      } else {
        alert("❌ Scheduling failed: " + (data.message || "Unknown error"));
      }
    } catch (error) {
      alert("❌ Error: " + (error as Error).message);
    } finally {
      setIsScheduling(false);
    }
  };

  return (
    <header className="h-16 bg-bg-secondary border-b border-gray-800 px-6 flex items-center justify-between">
      <h1 className="text-2xl font-semibold text-text-primary">InboxPilot</h1>
      
      <div className="flex items-center space-x-3">
        {/* Action Buttons */}
        <button
          onClick={handleScanInbox}
          disabled={isScanning}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 rounded-lg text-sm font-medium transition-colors flex items-center space-x-2"
        >
          <span>{isScanning ? "⏳" : "📧"}</span>
          <span>{isScanning ? "Scanning..." : "Scan Inbox"}</span>
        </button>

        <button
          onClick={handleRecategorize}
          disabled={isRecategorizing}
          className="px-4 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 rounded-lg text-sm font-medium transition-colors flex items-center space-x-2"
        >
          <span>{isRecategorizing ? "⏳" : "🔄"}</span>
          <span>{isRecategorizing ? "Processing..." : "Recategorize"}</span>
        </button>

        <button
          onClick={handleScheduleEvents}
          disabled={isScheduling}
          className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 rounded-lg text-sm font-medium transition-colors flex items-center space-x-2"
        >
          <span>{isScheduling ? "⏳" : "📅"}</span>
          <span>{isScheduling ? "Scheduling..." : "Schedule"}</span>
        </button>

        {/* Status Indicators */}
        <div className={`
          flex items-center space-x-2 px-4 py-2 rounded-full
          ${isLive ? "bg-accent-safe/10" : "bg-accent-spam/10"}
        `}>
          <div className={`
            w-2 h-2 rounded-full
            ${isLive ? "bg-accent-safe animate-pulse" : "bg-accent-spam"}
          `}></div>
          <span className={`
            text-sm font-mono
            ${isLive ? "text-accent-safe" : "text-accent-spam"}
          `}>
            {isLive ? "Live" : "Offline"}
          </span>
        </div>
        
        <span className="text-sm text-text-secondary font-mono">
          Last sync: {formatDistanceToNow(lastSync, { addSuffix: true })}
        </span>
      </div>
    </header>
  );
}
