"use client";
import { motion } from "framer-motion";
import {
  BarChart3, Brain, GitBranch, Clock, Shield, TrendingUp,
} from "lucide-react";

const FEATURES = [
  {
    icon: BarChart3,
    title: "Deep Statistics",
    desc: "Per-user breakdowns, message velocity, activity heatmaps, and more.",
  },
  {
    icon: Brain,
    title: "Sentiment & Topics",
    desc: "TextBlob-powered sentiment, LDA topic modeling, and language detection.",
  },
  {
    icon: GitBranch,
    title: "Social Graphs",
    desc: "Reply networks, Louvain communities, and centrality metrics.",
  },
  {
    icon: TrendingUp,
    title: "Engagement Scores",
    desc: "Composite engagement metric, churn-risk flags, and member tiering.",
  },
  {
    icon: Clock,
    title: "Retention Curves",
    desc: "Kaplan-Meier survival, cohort retention, and quick-churn detection.",
  },
  {
    icon: Shield,
    title: "Privacy First",
    desc: "Data processed in an isolated session and auto-purged within 24 hours.",
  },
];

export function Features() {
  return (
    <section className="px-6 py-24">
      <div className="max-w-6xl mx-auto">
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-4xl md:text-5xl font-bold text-center mb-4"
        >
          Everything you need to <span className="gradient-text">understand</span> a chat
        </motion.h2>
        <p className="text-white/50 text-center mb-16 max-w-2xl mx-auto">
          Built for community managers, researchers, and curious group admins.
        </p>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
          {FEATURES.map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.05 }}
              className="glass p-6 hover:border-brand/50 transition-all group"
            >
              <div className="inline-flex w-11 h-11 items-center justify-center rounded-lg bg-brand/10 mb-4 group-hover:bg-brand/20 transition-colors">
                <f.icon className="w-5 h-5 text-brand" />
              </div>
              <h3 className="text-lg font-semibold mb-2">{f.title}</h3>
              <p className="text-sm text-white/60">{f.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
