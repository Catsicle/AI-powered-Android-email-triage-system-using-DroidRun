export interface Email {
  id: string;
  sender: string;  // Maps to "name" from backend
  subject: string;
  preview: string;  // Maps to "summary" or "purpose" from backend
  timestamp: string;  // Combined "date" + "time" from backend
  category: "urgent" | "info" | "calendar" | "spam" | "decisions";
  read?: boolean;
}

export interface EmailData {
  urgent: Email[];
  info: Email[];
  calendar: Email[];
  spam: Email[];
  decisions: Email[];
  lastSync: string;
}

export interface MetricCardData {
  category: "urgent" | "decisions" | "calendar" | "info" | "spam";
  count: number;
  trend?: number;
  color: string;
}
