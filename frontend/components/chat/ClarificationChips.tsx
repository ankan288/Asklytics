"use client";

import React from "react";
import { HelpCircle, ChevronRight, Sparkles } from "lucide-react";
import type { ClarificationPayload } from "@/lib/types";

interface ClarificationChipsProps {
  clarification: ClarificationPayload;
  onSelectOption: (refinedPrompt: string) => void;
}

export function ClarificationChips({
  clarification,
  onSelectOption,
}: ClarificationChipsProps) {
  return (
    <div className="mt-2.5 flex flex-col gap-2 rounded-xl bg-slate-900/90 border border-indigo-500/30 p-3.5 backdrop-blur-md">
      <div className="flex items-center gap-2 text-xs font-semibold text-indigo-400">
        <Sparkles size={14} className="text-indigo-400 animate-pulse" />
        <span>Ambiguity Detected: Disambiguation Options</span>
      </div>
      <p className="text-xs text-slate-300 font-medium">{clarification.question}</p>
      <div className="mt-1 flex flex-col gap-1.5">
        {clarification.options.map((opt, idx) => (
          <button
            key={idx}
            onClick={() => onSelectOption(opt.refined_prompt)}
            className="group flex items-center justify-between text-left rounded-lg bg-slate-800/80 hover:bg-indigo-950/60 border border-slate-700/60 hover:border-indigo-500/50 px-3 py-2 transition-all duration-150 hover:shadow-sm"
          >
            <div className="flex flex-col">
              <span className="text-xs font-medium text-slate-200 group-hover:text-indigo-300">
                {opt.label}
              </span>
              <span className="text-[11px] text-slate-400 group-hover:text-slate-300">
                {opt.subtext}
              </span>
            </div>
            <ChevronRight
              size={14}
              className="text-slate-500 group-hover:text-indigo-400 group-hover:translate-x-0.5 transition-transform"
            />
          </button>
        ))}
      </div>
    </div>
  );
}
