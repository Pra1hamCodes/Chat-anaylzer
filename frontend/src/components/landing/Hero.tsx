"use client";
import { motion } from "framer-motion";
import { DropZone } from "@/components/upload/DropZone";
import { Shield, Sparkles } from "lucide-react";

export function Hero() {
  return (
    <section className="relative overflow-hidden px-6 pt-24 pb-20 md:pt-32 md:pb-28">
      {/* Animated background */}
      <div className="absolute inset-0 bg-grad-hero opacity-70" aria-hidden />
      <div className="absolute inset-0 pointer-events-none" aria-hidden>
        {[...Array(8)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute rounded-full blur-3xl"
            style={{
              left: `${(i * 13 + 10) % 90}%`,
              top: `${(i * 17 + 5) % 80}%`,
              width: 180 + (i % 4) * 60,
              height: 180 + (i % 4) * 60,
              background: i % 2 === 0 ? "rgba(0,212,170,.09)" : "rgba(124,58,237,.12)",
            }}
            animate={{ y: [0, -30, 0], x: [0, 10, 0] }}
            transition={{ duration: 8 + i, repeat: Infinity, ease: "easeInOut" }}
          />
        ))}
      </div>

      <div className="relative max-w-6xl mx-auto text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="inline-flex items-center gap-2 glass px-4 py-1.5 text-xs text-white/70 mb-6"
        >
          <Sparkles className="w-3.5 h-3.5 text-brand" />
          Production-grade chat analytics — no signup required
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.1 }}
          className="text-5xl md:text-7xl font-bold leading-tight tracking-tight"
        >
          Decode Your
          <br />
          <span className="gradient-text">WhatsApp Conversations</span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.2 }}
          className="mt-6 text-lg md:text-xl text-white/60 max-w-2xl mx-auto"
        >
          Upload a chat export and get deep analytics — sentiment, social graphs, engagement
          scores, churn risk, burst detection, and more.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.3 }}
          className="mt-12 max-w-xl mx-auto"
        >
          <DropZone />
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="mt-6 inline-flex items-center gap-2 text-xs text-white/40"
        >
          <Shield className="w-3.5 h-3.5" />
          Your data never leaves your session · auto-deleted in 24 hours
        </motion.div>
      </div>
    </section>
  );
}
