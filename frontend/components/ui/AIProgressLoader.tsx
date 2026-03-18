"use client";
import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Brain, Code2, Database, BarChart2 } from "lucide-react";

const STEPS = [
  { icon: Brain,    label: "Analyzing your question…", color: "text-purple-400",  ring: "border-purple-800/50", bg: "bg-purple-950/30" },
  { icon: Code2,    label: "Writing SQL query…",        color: "text-blue-400",   ring: "border-blue-800/50",   bg: "bg-blue-950/30"   },
  { icon: Database, label: "Fetching data…",            color: "text-cyan-400",   ring: "border-cyan-800/50",   bg: "bg-cyan-950/30"   },
  { icon: BarChart2,label: "Building charts…",          color: "text-indigo-400", ring: "border-indigo-800/50", bg: "bg-indigo-950/30" },
];

const DURATIONS = [1200, 1600, 1800, 99999];

export function AIProgressLoader() {
  const [step, setStep] = useState(0);

  useEffect(() => {
    setStep(0);
  }, []);

  useEffect(() => {
    if (step >= STEPS.length - 1) return;
    const t = setTimeout(() => setStep(s => s + 1), DURATIONS[step]);
    return () => clearTimeout(t);
  }, [step]);

  const current = STEPS[step];
  const Icon = current.icon;

  return (
    <div className="flex flex-col items-center justify-center gap-5 py-16">
      {/* Animated icon box */}
      <motion.div
        key={step}
        initial={{ scale: 0.6, opacity: 0, rotate: -10 }}
        animate={{ scale: 1, opacity: 1, rotate: 0 }}
        transition={{ type: "spring", stiffness: 260, damping: 18 }}
        className={`w-14 h-14 rounded-2xl border ${current.ring} ${current.bg} flex items-center justify-center ${current.color}`}
      >
        <Icon size={26} />
      </motion.div>

      {/* Step label with fade swap */}
      <AnimatePresence mode="wait">
        <motion.p
          key={step}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          transition={{ duration: 0.25 }}
          className="text-slate-300 text-sm font-medium"
        >
          {current.label}
        </motion.p>
      </AnimatePresence>

      {/* Progress pill bar */}
      <div className="flex items-center gap-1.5">
        {STEPS.map((_, i) => (
          <motion.div
            key={i}
            animate={{
              width: i === step ? 24 : 6,
              backgroundColor: i < step ? "#6366f1" : i === step ? "#818cf8" : "#1e293b",
            }}
            transition={{ duration: 0.35, ease: "easeInOut" }}
            className="h-1.5 rounded-full"
          />
        ))}
      </div>
    </div>
  );
}
