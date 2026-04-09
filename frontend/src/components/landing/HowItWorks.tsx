"use client";
import { motion } from "framer-motion";

const STEPS = [
  { num: "01", title: "Export chat", desc: "WhatsApp → Chat → Export → Without media." },
  { num: "02", title: "Upload the .txt", desc: "Drag & drop into the box above." },
  { num: "03", title: "Explore insights", desc: "Dashboard loads in seconds." },
];

export function HowItWorks() {
  return (
    <section className="px-6 py-24 border-t border-white/5">
      <div className="max-w-5xl mx-auto">
        <h2 className="text-4xl md:text-5xl font-bold text-center mb-16">
          How it <span className="gradient-text">works</span>
        </h2>
        <div className="grid md:grid-cols-3 gap-6">
          {STEPS.map((s, i) => (
            <motion.div
              key={s.num}
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.15 }}
              className="glass p-8 relative overflow-hidden"
            >
              <div className="text-7xl font-bold text-white/5 absolute -top-4 -right-2 select-none">
                {s.num}
              </div>
              <div className="relative">
                <div className="text-brand text-sm font-mono mb-3">STEP {s.num}</div>
                <h3 className="text-2xl font-semibold mb-2">{s.title}</h3>
                <p className="text-white/60">{s.desc}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
