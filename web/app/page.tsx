"use client";

import { useEffect, useState } from "react";
import Sidebar from "@/components/Sidebar";
import Header from "@/components/Header";
import Dashboard from "@/components/Dashboard";
import DecisionConsole from "@/components/DecisionConsole";
import SpamQuarantine from "@/components/SpamQuarantine";
import UrgentView from "@/components/UrgentView";
import InfoView from "@/components/InfoView";
import CalendarView from "@/components/CalendarView";
import { EmailData } from "@/types";

type View = "dashboard" | "decisions" | "spam" | "urgent" | "info" | "calendar";

export default function Home() {
  const [currentView, setCurrentView] = useState<View>("dashboard");
  const [emailData, setEmailData] = useState<EmailData | null>(null);
  const [lastSync, setLastSync] = useState<Date>(new Date());
  const [isLive, setIsLive] = useState(true);

  // Fetch email data from API
  const fetchData = async () => {
    try {
      const response = await fetch("/api/emails");
      const data = await response.json();
      setEmailData(data);
      setLastSync(new Date());
      setIsLive(true);
    } catch (error) {
      console.error("Failed to fetch email data:", error);
      setIsLive(false);
    }
  };

  useEffect(() => {
    fetchData();
    
    // Poll every 30 seconds for updates
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const renderView = () => {
    if (!emailData) {
      return (
        <div className="flex items-center justify-center h-full">
          <div className="text-text-secondary">Loading...</div>
        </div>
      );
    }

    switch (currentView) {
      case "dashboard":
        return <Dashboard emailData={emailData} onNavigate={setCurrentView} />;
      case "decisions":
        return <DecisionConsole emails={emailData.decisions} />;
      case "spam":
        return <SpamQuarantine emails={emailData.spam} />;
      case "urgent":
        return <UrgentView emails={emailData.urgent} />;
      case "info":
        return <InfoView emails={emailData.info} />;
      case "calendar":
        return <CalendarView emails={emailData.calendar} />;
      default:
        return <Dashboard emailData={emailData} onNavigate={setCurrentView} />;
    }
  };

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar currentView={currentView} onNavigate={setCurrentView} />
      
      <main className="flex-1 flex flex-col overflow-hidden">
        <Header isLive={isLive} lastSync={lastSync} onRefresh={fetchData} />
        
        <div className="flex-1 overflow-y-auto scrollbar-hide p-6">
          {renderView()}
        </div>
      </main>
    </div>
  );
}
