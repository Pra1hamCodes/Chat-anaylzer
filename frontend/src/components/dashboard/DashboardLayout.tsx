"use client";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  LayoutDashboard, Users, Clock, Brain, Share2, TrendingUp, Download, ArrowLeft,
} from "lucide-react";
import { cn } from "@/lib/utils";

const TABS = [
  { key: "overview",   label: "Overview",   icon: LayoutDashboard },
  { key: "users",      label: "Users",      icon: Users },
  { key: "temporal",   label: "Timeline",   icon: Clock },
  { key: "nlp",        label: "Sentiment",  icon: Brain },
  { key: "network",    label: "Network",    icon: Share2 },
  { key: "engagement", label: "Engagement", icon: TrendingUp },
  { key: "export",     label: "Export",     icon: Download },
];

export function DashboardLayout({
  tab, onTabChange, groupName, children,
}: { tab: string; onTabChange: (t: string) => void; groupName?: string | null; children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex bg-brand-bg text-white">
      <aside className="w-64 hidden md:flex flex-col border-r border-white/5 p-4">
        <Link href="/" className="flex items-center gap-2 mb-8 text-white/60 hover:text-white">
          <ArrowLeft className="w-4 h-4" /> <span className="text-sm">Back</span>
        </Link>
        <div className="mb-8 px-2">
          <div className="text-xs uppercase tracking-wider text-white/40 mb-1">Group</div>
          <div className="font-semibold truncate">{groupName || "WhatsApp Chat"}</div>
        </div>
        <nav className="space-y-1">
          {TABS.map((t) => (
            <button
              key={t.key}
              onClick={() => onTabChange(t.key)}
              className={cn(
                "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all",
                tab === t.key
                  ? "bg-brand/10 text-white border border-brand/20"
                  : "text-white/50 hover:text-white hover:bg-white/5"
              )}
            >
              <t.icon className="w-4 h-4" />
              {t.label}
            </button>
          ))}
        </nav>
      </aside>

      {/* Mobile bottom nav */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 glass border-t border-white/10 z-40 overflow-x-auto">
        <div className="flex">
          {TABS.map((t) => (
            <button
              key={t.key}
              onClick={() => onTabChange(t.key)}
              className={cn(
                "flex-shrink-0 flex flex-col items-center gap-1 px-4 py-2",
                tab === t.key ? "text-brand" : "text-white/50"
              )}
            >
              <t.icon className="w-4 h-4" />
              <span className="text-[10px]">{t.label}</span>
            </button>
          ))}
        </div>
      </nav>

      <main className="flex-1 p-6 md:p-10 pb-24 md:pb-10 overflow-x-hidden">
        <motion.div key={tab} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.25 }}>
          {children}
        </motion.div>
      </main>
    </div>
  );
}
