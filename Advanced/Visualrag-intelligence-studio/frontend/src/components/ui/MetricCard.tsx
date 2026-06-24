import React from "react";
import { Card } from "./Card";
import { cn } from "../../utils";
import { LucideIcon } from "lucide-react";

interface MetricCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  trend?: string;
  trendColor?: string;
  progress?: number;
  highlightIconColor?: string;
}

export function MetricCard({
  title, value, icon: Icon, trend, trendColor, progress, highlightIconColor
}: MetricCardProps) {
  return (
    <Card className="p-6 flex flex-col justify-between min-h-[140px]">
      <div className="flex justify-between items-start">
        <span className="text-sm font-medium text-on-surface-variant uppercase tracking-wider">{title}</span>
        <Icon size={20} className={cn("opacity-70", highlightIconColor || "text-on-surface-variant")} />
      </div>
      
      <div className="mt-4">
        <div className="flex items-baseline gap-3">
          <span className="text-4xl font-semibold text-on-surface tracking-tight">{value}</span>
          {trend && (
            <span className={cn(
              "text-xs font-medium px-2 py-0.5 rounded-full border",
              trendColor === "tertiary" && "bg-tertiary/10 text-tertiary border-tertiary/20",
              trendColor === "error" && "bg-error/10 text-error border-error/20",
              trendColor === "outline" && "bg-outline-variant/30 text-on-surface-variant border-outline-variant/50"
            )}>
              {trend}
            </span>
          )}
        </div>
        
        {progress !== undefined && (
          <div className="w-full bg-surface-container h-1.5 rounded-full mt-3 overflow-hidden">
            <div 
              className="bg-primary h-full rounded-full shadow-[0_0_8px_rgba(77,142,255,0.6)]" 
              style={{ width: `${progress}%` }} 
            />
          </div>
        )}
      </div>
    </Card>
  );
}
