import { Sidebar } from "./Sidebar";
import { Outlet } from "react-router-dom";
import { Bell, Settings as SettingsIcon, Menu } from "lucide-react";

export function Topbar() {
  return (
    <header className="md:hidden fixed top-0 left-0 w-full z-50 flex justify-between items-center px-6 h-16 bg-surface/60 backdrop-blur-xl border-b border-outline-variant/10 shadow-sm">
      <div className="flex items-center gap-3">
        <Menu className="text-primary cursor-pointer" size={24} />
        <span className="text-lg font-bold text-primary">VisualRAG</span>
      </div>
      <div className="flex items-center gap-4 text-on-surface-variant">
        <Bell size={20} className="hover:text-primary transition-colors cursor-pointer" />
        <SettingsIcon size={20} className="hover:text-primary transition-colors cursor-pointer" />
      </div>
    </header>
  );
}

export function Layout() {
  return (
    <div className="min-h-screen bg-background text-on-surface font-sans flex">
      <Sidebar />
      <Topbar />
      <main className="flex-1 md:ml-64 pt-20 md:pt-8 w-full max-w-[1600px] mx-auto px-4 md:px-8 pb-12 overflow-x-hidden min-h-screen">
        <Outlet />
      </main>
    </div>
  );
}
