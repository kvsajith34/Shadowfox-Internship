import React from "react";
import { cn } from "../../utils";

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "ghost" | "secondary";
};

export function Button({ className, variant = "primary", children, ...props }: ButtonProps) {
  return (
    <button
      className={cn(
        "px-6 py-3 rounded-lg font-medium text-sm transition-all flex items-center justify-center gap-2 outline-none focus-visible:ring-2 focus-visible:ring-primary/50",
        variant === "primary" && "btn-primary",
        variant === "ghost" && "btn-ghost",
        variant === "secondary" && "bg-surface-variant/40 hover:bg-surface-variant/60 text-on-surface border border-outline-variant/30",
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
}
