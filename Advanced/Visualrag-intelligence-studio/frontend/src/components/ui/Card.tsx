import React from "react";
import { cn } from "../../utils";

type CardProps = React.HTMLAttributes<HTMLDivElement> & {
  variant?: "panel" | "card";
};

export function Card({ className, variant = "panel", children, ...props }: CardProps) {
  return (
    <div
      className={cn(
        "rounded-xl overflow-hidden",
        variant === "panel" ? "glass-panel" : "glass-card",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}
