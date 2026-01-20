"use client";

import { useState } from "react";
import { Email } from "@/types";
import { RotateCcw, AlertTriangle } from "lucide-react";
import Toast from "./Toast";

interface SpamQuarantineProps {
  emails: Email[];
}

export default function SpamQuarantine({ emails }: SpamQuarantineProps) {
  const [emailList, setEmailList] = useState(emails);
  const [toast, setToast] = useState<string | null>(null);
  const [showConfirm, setShowConfirm] = useState(false);

  const handlePurgeAll = async () => {
    setShowConfirm(false);
    setEmailList([]);
    setToast(`Purged ${emails.length} spam emails`);

    try {
      await fetch("/api/actions/purge-spam", {
        method: "POST",
      });
    } catch (error) {
      console.error("Failed to purge spam:", error);
    }

    setTimeout(() => setToast(null), 3000);
  };

  const handleRestore = async (emailId: string) => {
    setEmailList((prev) => prev.filter((e) => e.id !== emailId));
    const email = emails.find((e) => e.id === emailId);
    setToast(`Restored email from ${email?.sender}`);

    try {
      await fetch("/api/actions/restore", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ emailId }),
      });
    } catch (error) {
      console.error("Failed to restore email:", error);
    }

    setTimeout(() => setToast(null), 3000);
  };

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header with Purge Button */}
      <div className="sticky top-0 bg-bg-primary z-10 pb-6">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h2 className="text-3xl font-bold text-text-primary mb-2">Spam Quarantine</h2>
            <p className="text-text-secondary">{emailList.length} items in quarantine</p>
          </div>
          
          {emailList.length > 0 && (
            <button
              onClick={() => setShowConfirm(true)}
              className="px-6 py-3 bg-accent-spam hover:bg-accent-spam/80 text-white rounded-lg font-semibold transition-all flex items-center space-x-2"
            >
              <AlertTriangle size={18} />
              <span>Purge All {emailList.length} Items</span>
            </button>
          )}
        </div>
      </div>

      {/* Confirm Dialog */}
      {showConfirm && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
          <div className="bg-bg-card border border-gray-800 rounded-xl p-6 max-w-md">
            <h3 className="text-xl font-semibold text-text-primary mb-4">Confirm Purge</h3>
            <p className="text-text-secondary mb-6">
              Are you sure you want to delete all {emailList.length} spam emails? This action cannot be undone.
            </p>
            <div className="flex space-x-3">
              <button
                onClick={() => setShowConfirm(false)}
                className="flex-1 px-4 py-2 border border-gray-700 rounded-lg hover:bg-bg-primary"
              >
                Cancel
              </button>
              <button
                onClick={handlePurgeAll}
                className="flex-1 px-4 py-2 bg-accent-spam text-white rounded-lg hover:bg-accent-spam/80"
              >
                Delete All
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Email List - Description Cards */}
      {emailList.length > 0 ? (
        <div className="space-y-3">
          {emailList.map((email) => (
            <div
              key={email.id}
              className="bg-bg-card rounded-lg border border-gray-800 hover:border-accent-spam/50 transition-all group"
            >
              <div className="px-6 py-4 flex items-start justify-between">
                {/* Email Description */}
                <div className="flex-1 pr-4">
                  <p className="text-text-secondary leading-relaxed">
                    {email.preview || email.subject}
                  </p>
                  <div className="text-xs text-text-muted font-mono mt-2">
                    {email.timestamp} • {email.sender}
                  </div>
                </div>

                {/* Restore Button */}
                <button
                  onClick={() => handleRestore(email.id)}
                  className="flex-shrink-0 px-4 py-2 rounded-lg border border-accent-safe/30 bg-accent-safe/5 hover:bg-accent-safe/10 text-accent-safe transition-all opacity-0 group-hover:opacity-100 flex items-center space-x-2"
                  title="Not Spam - Restore to Inbox"
                >
                  <RotateCcw size={16} />
                  <span className="text-sm font-medium">Restore</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center h-64">
          <div className="text-6xl mb-4">✅</div>
          <h3 className="text-2xl font-semibold text-text-primary mb-2">No Spam</h3>
          <p className="text-text-secondary">Quarantine is empty</p>
        </div>
      )}

      {/* Toast */}
      {toast && <Toast message={toast} />}
    </div>
  );
}
