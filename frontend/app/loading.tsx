import { BarChart2 } from "lucide-react";

export default function Loading() {
  return (
    <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-[#050810] text-white">
      {/* Glow effect */}
      <div className="absolute w-72 h-72 bg-indigo-600/20 rounded-full blur-3xl pointer-events-none animate-pulse" />

      {/* Brand Icon with Spinner Ring */}
      <div className="relative flex items-center justify-center mb-6">
        <div className="w-16 h-16 rounded-2xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center backdrop-blur-md">
          <BarChart2 size={28} className="text-indigo-400 animate-pulse" />
        </div>
        <div className="absolute inset-0 w-16 h-16 rounded-2xl border-2 border-transparent border-t-indigo-500 animate-spin" />
      </div>

      {/* Text Indicator */}
      <h3 className="text-lg font-bold text-white tracking-tight mb-1">
        Asklytics
      </h3>
      <p className="text-xs text-slate-400 flex items-center gap-1.5 font-medium">
        Loading analytics engine...
      </p>
    </div>
  );
}

