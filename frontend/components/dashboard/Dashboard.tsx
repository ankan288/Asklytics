"use client";
import { motion, type Variants } from "framer-motion";
import { ChartCard } from "./ChartCard";
import { AuditDrawer } from "./AuditDrawer";
import { Lightbulb, Sparkles } from "lucide-react";
import type { DashboardResponse } from "@/lib/types";

interface Props {
  dashboard: DashboardResponse;
  showSQL?: boolean;
  onSuggestionClick?: (q: string) => void;
}

const fadeUp: Variants = {
  hidden: { opacity: 0, y: 14 },
  show:   { opacity: 1, y: 0, transition: { duration: 0.35 } },
};

const stagger: Variants = {
  hidden: {},
  show:   { transition: { staggerChildren: 0.08 } },
};

export function Dashboard({ dashboard, showSQL = false, onSuggestionClick }: Props) {
  const kpiCharts   = dashboard.charts.filter((c) => c.type === "kpi");
  const otherCharts = dashboard.charts.filter((c) => c.type !== "kpi");

  const kpiGrid =
    kpiCharts.length === 1 ? "grid-cols-1 max-w-xs"
    : kpiCharts.length === 2 ? "grid-cols-2"
    : "grid-cols-3";

  return (
    <motion.div
      variants={stagger}
      initial="hidden"
      animate="show"
      className="space-y-6"
    >
      {/* Title */}
      <motion.h2 variants={fadeUp} className="text-2xl font-semibold text-white tracking-tight">
        {dashboard.dashboard_title}
      </motion.h2>

      {/* Insight banner */}
      {dashboard.insight_summary && (
        <motion.div
          variants={fadeUp}
          className="flex gap-3 bg-indigo-950/40 border border-indigo-900/50 rounded-xl p-4"
        >
          <Lightbulb className="shrink-0 text-indigo-400 mt-0.5" size={16} />
          <p className="text-slate-300 text-sm leading-relaxed">{dashboard.insight_summary}</p>
        </motion.div>
      )}

      {/* KPI cards row */}
      {kpiCharts.length > 0 && (
        <div className={`grid gap-4 ${kpiGrid}`}>
          {kpiCharts.map((c) => (
            <motion.div key={c.id} variants={fadeUp}>
              <ChartCard spec={c} />
            </motion.div>
          ))}
        </div>
      )}

      {/* Main charts grid */}
      {otherCharts.length > 0 && (
        <div className={`grid gap-5 ${otherCharts.length === 1 ? "grid-cols-1" : "grid-cols-1 md:grid-cols-2"}`}>
          {otherCharts.map((c) => (
            <motion.div key={c.id} variants={fadeUp}>
              <ChartCard spec={c} />
            </motion.div>
          ))}
        </div>
      )}

      {/* "How I Got This" Audit Drawer (Upgrade #7: Trust, Verification & Telemetry) */}
      <motion.div variants={fadeUp}>
        <AuditDrawer audit={dashboard.audit} rawSql={dashboard.sql} />
      </motion.div>

      {/* AI-suggested follow-up questions */}
      {onSuggestionClick && dashboard.follow_up_suggestions && dashboard.follow_up_suggestions.length > 0 && (
        <motion.div variants={fadeUp} className="pt-2">
          <p className="flex items-center gap-1.5 text-slate-500 text-xs mb-2.5">
            <Sparkles size={12} className="text-indigo-400" />
            Suggested follow-ups
          </p>
          <div className="flex flex-wrap gap-2">
            {dashboard.follow_up_suggestions.map((q, i) => (
              <motion.button
                key={q}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.3 + i * 0.06 }}
                onClick={() => onSuggestionClick(q)}
                className="text-xs text-indigo-300 bg-indigo-950/50 hover:bg-indigo-900/50 border border-indigo-800/50 hover:border-indigo-700 rounded-full px-3 py-1.5 transition-colors text-left"
              >
                {q}
              </motion.button>
            ))}
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}
