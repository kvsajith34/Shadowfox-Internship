import { LucideIcon } from "lucide-react";
import { Link, useLocation } from "react-router-dom";
import { cn } from "../../utils";
import {
  LayoutDashboard,
  UploadCloud,
  MessageSquare,
  FileText,
  Receipt,
  BarChart,
  FlaskConical,
  FileBarChart,
  Settings,
  Plus
} from "lucide-react";

export function Sidebar() {
  const location = useLocation();

  const navItems = [
    { name: "Dashboard", path: "/", icon: LayoutDashboard },
    { name: "Upload & Analyze", path: "/upload", icon: UploadCloud },
    { name: "Visual Chat", path: "/visual-chat", icon: MessageSquare },
    { name: "PDF RAG Chat", path: "/pdf-rag-chat", icon: FileText },
    { name: "Invoice Extractor", path: "/invoice-extractor", icon: Receipt },
    { name: "Chart Analyzer", path: "/chart-analyzer", icon: BarChart },
    { name: "Evaluation Lab", path: "/evaluation-lab", icon: FlaskConical },
    { name: "Reports", path: "/reports", icon: FileBarChart },
    { name: "Settings", path: "/settings", icon: Settings },
  ];

  return (
    <aside className="hidden md:flex flex-col fixed left-0 top-0 h-full w-64 z-40 bg-surface-variant/40 backdrop-blur-2xl border-r border-outline-variant/20 shadow-xl py-6">
      {/* Brand Header */}
      <div className="px-6 mb-8 flex items-center gap-3">
        <div className="w-10 h-10 rounded-lg overflow-hidden glass-panel flex items-center justify-center border border-outline-variant/20 shadow-sm relative shrink-0">
          <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuAHWCW9IPnkFGKdZ6PVsjya6flixEDqqbaSOVOHtCFdn4V2xBPbbdZZSQ2mFubGvMFYw1aq54DVNj4jNr0jB8NxG0fOM0kBP4z0hCFRK86fOJ_43HTGcdvMMUg2HTIQn8rtXUYKpnhAzvbF6EysFRaMHER23jHHXT9URVdQRIJ6uz3kuB_hLCGvMMj6nHqg6F1lXQEgWQ74a1ndQmzfWnmbAIFeX-TiYwUTTYqsEYwrXzT3P0CYyV9C1DwT3SfZX1ZApG5BMtZJtVE" alt="Logo" className="w-full h-full object-cover" />
          <div className="absolute inset-0 rounded-lg shadow-[inset_0_0_8px_rgba(173,198,255,0.2)] pointer-events-none" />
        </div>
        <div className="flex flex-col justify-center">
          <h1 className="text-xl font-bold text-primary tracking-tight leading-tight">VisualRAG</h1>
          <p className="text-xs text-on-surface-variant/70 font-medium">AI Command Center</p>
        </div>
      </div>
      
      <div className="px-4 mb-6">
        <button className="w-full btn-primary py-3 rounded-lg flex items-center justify-center gap-2 font-medium text-sm">
          <Plus size={18} />
          New Analysis
        </button>
      </div>

      <nav className="flex-1 overflow-y-auto px-2 space-y-1">
        {navItems.map((item, index) => {
          const isActive = location.pathname === item.path;
          const isSettings = item.name === "Settings";
          
          return (
            <Link
              key={item.path}
              to={item.path}
              className={cn(
                "flex items-center gap-3 px-4 py-3 rounded-lg transition-all text-sm font-medium",
                isActive
                  ? "bg-secondary-container/30 text-primary border-r-4 border-primary rounded-r-none translate-x-1"
                  : "text-on-surface-variant hover:bg-surface-variant/50 hover:text-on-surface",
                isSettings && "mt-auto lg:mt-6 border-t border-outline-variant/10 !rounded-none !border-r-0 !translate-x-0"
              )}
            >
              <item.icon size={18} className={cn(isActive ? "text-primary" : "text-outline")} />
              {item.name}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
