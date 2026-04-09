"use client";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import type { LucideIcon } from "lucide-react";

type Props = {
  label: string;
  value: string | number;
  icon?: LucideIcon;
  hint?: string;
  delay?: number;
};

export function StatCard({ label, value, icon: Icon, hint, delay = 0 }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.4 }}
      className="glass p-5 relative overflow-hidden group"
    >
      <div className="absolute inset-0 bg-gradient-to-br from-brand/5 to-brand-purple/5 opacity-0 group-hover:opacity-100 transition-opacity" />
      <div className="relative flex items-start justify-between">
        <div>
          <div className="text-[0.7rem] uppercase tracking-wider text-white/50">{label}</div>
          <div className="mt-1 text-3xl font-bold">{value}</div>
          {hint && <div className="mt-1 text-xs text-white/40">{hint}</div>}
        </div>
        {Icon && (
          <div className="rounded-lg bg-brand/10 p-2">
            <Icon className="w-4 h-4 text-brand" />
          </div>
        )}
      </div>
    </motion.div>
  );
}
