"use client";

import { useState } from "react";
import { Email } from "@/types";
import { ChevronDown, ChevronRight } from "lucide-react";

interface InfoViewProps {
  emails: Email[];
}

export default function InfoView({ emails }: InfoViewProps) {
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());

  const toggleExpand = (id: string) => {
    setExpandedIds((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(id)) {
        newSet.delete(id);
      } else {
        newSet.add(id);
      }
      return newSet;
    });
  };

  if (emails.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64">
        <div className="text-6xl mb-4">📭</div>
        <h3 className="text-2xl font-semibold text-text-primary mb-2">No Info Items</h3>
        <p className="text-text-secondary">Inbox is clean</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6">
        <h2 className="text-3xl font-bold text-text-primary mb-2">Info</h2>
        <p className="text-text-secondary">{emails.length} informational emails</p>
      </div>

      {/* Collapsed Accordion List */}
      <div className="bg-bg-card rounded-xl border border-gray-800 overflow-hidden divide-y divide-gray-800">
        {emails.map((email) => {
          const isExpanded = expandedIds.has(email.id);
          
          return (
            <div key={email.id} className="transition-all">
              <button
                onClick={() => toggleExpand(email.id)}
                className="w-full px-6 py-4 flex items-center justify-between hover:bg-bg-primary/50 transition-colors"
              >
                <div className="flex items-center space-x-3 flex-1 text-left">
                  {isExpanded ? (
                    <ChevronDown size={18} className="text-text-secondary" />
                  ) : (
                    <ChevronRight size={18} className="text-text-secondary" />
                  )}
                  
                  <div className="flex-1">
                    <div className="font-medium text-text-primary">{email.subject}</div>
                    <div className="text-sm text-text-muted mt-1">{email.sender}</div>
                  </div>
                </div>
                
                <div className="text-xs text-text-muted font-mono ml-4">
                  {email.timestamp}
                </div>
              </button>

              {isExpanded && (
                <div className="px-6 py-4 bg-bg-primary/30 border-t border-gray-800">
                  <p className="text-text-secondary">{email.preview}</p>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
