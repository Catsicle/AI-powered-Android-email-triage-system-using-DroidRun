"use client";

import { useState } from "react";
import { Email } from "@/types";
import { Archive, Trash2, Reply } from "lucide-react";
import Toast from "./Toast";

interface DecisionConsoleProps {
  emails: Email[];
}

export default function DecisionConsole({ emails }: DecisionConsoleProps) {
  const [emailList, setEmailList] = useState(emails);
  const [toast, setToast] = useState<{ message: string; action: string } | null>(null);

  const handleAction = async (emailId: string, action: "archive" | "delete" | "reply") => {
    // Optimistic UI update
    setEmailList((prev) => prev.filter((e) => e.id !== emailId));
    
    const email = emails.find((e) => e.id === emailId);
    setToast({
      message: `Action Queued: ${action} email from ${email?.sender}`,
      action,
    });

    // Queue action to backend
    try {
      await fetch("/api/actions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ emailId, action }),
      });
    } catch (error) {
      console.error("Failed to queue action:", error);
    }

    // Clear toast after 3 seconds
    setTimeout(() => setToast(null), 3000);
  };

  if (emailList.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full">
        <div className="text-6xl mb-4">✨</div>
        <h3 className="text-2xl font-semibold text-text-primary mb-2">All Caught Up</h3>
        <p className="text-text-secondary">DroidRun is sleeping.</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-4">
      <div className="mb-6">
        <h2 className="text-3xl font-bold text-text-primary mb-2">Decision Console</h2>
        <p className="text-text-secondary">{emailList.length} items require your attention</p>
      </div>

      {/* Action Cards Stream */}
      <div className="space-y-4">
        {emailList.map((email) => (
          <div
            key={email.id}
            className="bg-bg-card rounded-xl border border-gray-800 overflow-hidden transition-all hover:border-accent-decisions"
          >
            {/* Header */}
            <div className="px-6 py-4 border-b border-gray-800 flex justify-between items-center">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-full bg-accent-decisions/20 flex items-center justify-center text-accent-decisions font-semibold">
                  {email.sender.charAt(0).toUpperCase()}
                </div>
                <div>
                    <div className="font-semibold text-text-primary">{email.sender}</div>
                    <div className="text-xs text-text-muted font-mono">{email.timestamp}</div>
                </div>
              </div>
            </div>

            {/* Body */}
            <div className="px-6 py-4">
              <h3 className="text-xl font-semibold text-text-primary mb-2">
                {email.subject}
              </h3>
              <p className="text-text-secondary mb-4">{email.preview}</p>
            </div>

            {/* Footer - Control Bar */}
            <div className="px-6 py-4 bg-bg-primary/50 flex items-center space-x-3">
              <button
                onClick={() => handleAction(email.id, "archive")}
                className="flex-1 px-4 py-2 rounded-lg border border-gray-700 text-text-secondary hover:text-text-primary hover:border-gray-600 transition-all"
              >
                <Archive size={16} className="inline mr-2" />
                Archive
              </button>
              
              <button
                onClick={() => handleAction(email.id, "delete")}
                className="flex-1 px-4 py-2 rounded-lg border border-gray-700 text-text-secondary hover:text-accent-spam hover:border-accent-spam transition-all"
              >
                <Trash2 size={16} className="inline mr-2" />
                Delete
              </button>
              
              <button
                onClick={() => handleAction(email.id, "reply")}
                className="flex-1 px-4 py-2 rounded-lg bg-accent-decisions text-white hover:bg-accent-decisions/80 transition-all font-medium"
              >
                <Reply size={16} className="inline mr-2" />
                Reply
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Toast Notification */}
      {toast && <Toast message={toast.message} />}
    </div>
  );
}
