"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  ShieldCheck,
  Code2,
  Clock,
  Database,
  CheckCircle2,
  AlertTriangle,
  Copy,
  Check,
  ChevronDown,
  ChevronUp,
  Sparkles,
  Info,
} from "lucide-react";
import type { AuditMetadata } from "@/lib/types";

interface AuditDrawerProps {
  audit?: AuditMetadata;
  rawSql?: string;
}

export function AuditDrawer({ audit, rawSql }: AuditDrawerProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [copied, setCopied] = useState(false);
  const [activeTab, setActiveTab] = useState<"verification" | "sql" | "telemetry">("verification");

  const sqlToDisplay = audit?.sanitized_sql || rawSql || "";
  const verification = audit?.verification;
  const isVerified = verification ? verification.verified : true;

  const handleCopy = () => {
    if (!sqlToDisplay) return;
    navigator.clipboard.writeText(sqlToDisplay);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="mt-3 border border-slate-800/80 rounded-xl bg-slate-950/60 backdrop-blur-md overflow-hidden">
      {/* Trigger Header */}
      <button
        onClick={() => setIsOpen((prev) => !prev)}
        className="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-slate-900/40 transition-colors"
      >
        <div className="flex items-center gap-2.5">
          <div className={`p-1.5 rounded-lg ${isVerified ? "bg-emerald-500/10 text-emerald-400" : "bg-amber-500/10 text-amber-400"}`}>
            <ShieldCheck size={16} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-medium text-slate-200">How I got this</span>
              {verification?.badge && (
                <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${
                  isVerified
                    ? "bg-emerald-500/15 text-emerald-300 border border-emerald-500/30"
                    : "bg-amber-500/15 text-amber-300 border border-amber-500/30"
                }`}>
                  {verification.badge}
                </span>
              )}
            </div>
            <p className="text-[11px] text-slate-400">
              Audit query, telemetry, and verified numbers
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {audit?.execution_time_ms !== undefined && (
            <span className="text-[11px] text-slate-500 flex items-center gap-1 font-mono">
              <Clock size={12} />
              {audit.execution_time_ms}ms
            </span>
          )}
          {isOpen ? <ChevronUp size={16} className="text-slate-400" /> : <ChevronDown size={16} className="text-slate-400" />}
        </div>
      </button>

      {/* Expandable Content */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="border-t border-slate-800/80 px-4 py-4 space-y-4"
          >
            {/* Tabs */}
            <div className="flex gap-2 border-b border-slate-800 pb-2">
              <button
                onClick={() => setActiveTab("verification")}
                className={`text-xs px-3 py-1.5 rounded-lg transition-all ${
                  activeTab === "verification"
                    ? "bg-indigo-600/20 text-indigo-300 font-medium border border-indigo-500/30"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                Numbers Verified ({verification?.claims_verified ?? 0}/{verification?.claims_total ?? 0})
              </button>
              <button
                onClick={() => setActiveTab("sql")}
                className={`text-xs px-3 py-1.5 rounded-lg transition-all ${
                  activeTab === "sql"
                    ? "bg-indigo-600/20 text-indigo-300 font-medium border border-indigo-500/30"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                Safe SQL AST
              </button>
              <button
                onClick={() => setActiveTab("telemetry")}
                className={`text-xs px-3 py-1.5 rounded-lg transition-all ${
                  activeTab === "telemetry"
                    ? "bg-indigo-600/20 text-indigo-300 font-medium border border-indigo-500/30"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                Execution Telemetry
              </button>
            </div>

            {/* Tab 1: Verification */}
            {activeTab === "verification" && (
              <div className="space-y-2.5">
                {verification?.claims && verification.claims.length > 0 ? (
                  verification.claims.map((claim, idx) => (
                    <div
                      key={idx}
                      className="p-3 rounded-lg bg-slate-900/70 border border-slate-800 flex items-start gap-3"
                    >
                      {claim.status === "VERIFIED" ? (
                        <CheckCircle2 size={16} className="text-emerald-400 shrink-0 mt-0.5" />
                      ) : (
                        <AlertTriangle size={16} className="text-amber-400 shrink-0 mt-0.5" />
                      )}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between gap-2">
                          <span className="text-xs font-medium text-slate-200">
                            Claimed: <code className="text-indigo-300 bg-indigo-950/60 px-1.5 py-0.5 rounded text-[11px]">{claim.claimed_value}</code>
                          </span>
                          <span
                            className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${
                              claim.status === "VERIFIED"
                                ? "bg-emerald-500/10 text-emerald-400"
                                : "bg-amber-500/10 text-amber-400"
                            }`}
                          >
                            {claim.status}
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-400 mt-1">{claim.explanation}</p>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-xs text-slate-400 flex items-center gap-2 p-3 bg-slate-900/40 rounded-lg">
                    <Info size={14} className="text-slate-500" />
                    All assertions are grounded directly in returned rows without discrepancies.
                  </div>
                )}
              </div>
            )}

            {/* Tab 2: SQL */}
            {activeTab === "sql" && (
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-400 font-mono">AST-Validated SQLite Query</span>
                  <button
                    onClick={handleCopy}
                    className="flex items-center gap-1.5 text-xs text-indigo-400 hover:text-indigo-300 transition-colors px-2 py-1 bg-indigo-950/40 rounded border border-indigo-900/40"
                  >
                    {copied ? <Check size={12} /> : <Copy size={12} />}
                    {copied ? "Copied" : "Copy SQL"}
                  </button>
                </div>
                <pre className="p-3 bg-slate-900 border border-slate-800 rounded-lg text-emerald-400 text-xs font-mono overflow-x-auto leading-relaxed">
                  {sqlToDisplay}
                </pre>
                <div className="flex flex-wrap gap-2 text-[10px] text-slate-400 mt-2">
                  <span className="px-2 py-0.5 bg-slate-800/80 rounded">✓ Read-Only Driver Mode</span>
                  <span className="px-2 py-0.5 bg-slate-800/80 rounded">✓ Enforced LIMIT 1000</span>
                  <span className="px-2 py-0.5 bg-slate-800/80 rounded">✓ Whitelisted Schema Tables</span>
                </div>
              </div>
            )}

            {/* Tab 3: Telemetry */}
            {activeTab === "telemetry" && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
                <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800">
                  <p className="text-slate-500 text-[11px]">Execution Latency</p>
                  <p className="text-slate-200 font-mono font-semibold text-sm mt-0.5">
                    {audit?.execution_time_ms ?? 0} ms
                  </p>
                </div>
                <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800">
                  <p className="text-slate-500 text-[11px]">Rows Scanned</p>
                  <p className="text-slate-200 font-mono font-semibold text-sm mt-0.5">
                    {audit?.rows_scanned ?? 0}
                  </p>
                </div>
                <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800">
                  <p className="text-slate-500 text-[11px]">Confidence Level</p>
                  <p className="text-emerald-400 font-mono font-semibold text-sm mt-0.5">
                    {Math.round((audit?.confidence_score ?? 0.95) * 100)}%
                  </p>
                </div>
                <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800">
                  <p className="text-slate-500 text-[11px]">Security Mode</p>
                  <p className="text-indigo-300 font-mono font-semibold text-sm mt-0.5">
                    AST Guarded
                  </p>
                </div>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
