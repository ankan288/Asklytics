"use client";

import { useEffect } from "react";
import Link from "next/link";
import { AlertTriangle, RotateCcw, Home, ShieldAlert } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function ErrorBoundary({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log unexpected client error to monitoring telemetry
    console.error("Asklytics Runtime Error:", error);
  }, [error]);

  return (
    <div className="min-h-screen bg-[#050810] text-slate-200 flex items-center justify-center p-6 relative overflow-hidden">
      {/* Background glow */}
      <div className="absolute w-96 h-96 bg-red-600/10 rounded-full blur-3xl pointer-events-none" />

      <div className="relative z-10 max-w-md w-full bg-slate-900/60 border border-red-500/20 backdrop-blur-xl rounded-3xl p-8 text-center shadow-2xl">
        <div className="w-14 h-14 bg-red-500/10 border border-red-500/30 rounded-2xl flex items-center justify-center text-red-400 mx-auto mb-6">
          <AlertTriangle size={28} />
        </div>

        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-red-500/10 border border-red-500/20 text-red-400 text-xs font-semibold mb-3">
          <ShieldAlert size={13} />
          Application Error Encountered
        </div>

        <h1 className="text-2xl font-bold text-white mb-2">
          Something went wrong
        </h1>

        <p className="text-xs text-slate-400 leading-relaxed mb-6">
          {error.message || "An unexpected error occurred while processing your request or rendering the analytical dashboard."}
        </p>

        {error.digest && (
          <p className="text-[10px] font-mono text-slate-400 bg-slate-950/60 p-2 rounded-lg mb-6 border border-white/5 break-all">
            Digest Code: {error.digest}
          </p>
        )}

        <div className="flex flex-col sm:flex-row items-center gap-3 justify-center">
          <Button
            onClick={() => reset()}
            className="w-full sm:w-auto bg-indigo-600 hover:bg-indigo-500 text-white flex items-center justify-center gap-2 text-xs py-2.5 px-5"
          >
            <RotateCcw size={14} />
            Try Again
          </Button>
          <Link
            href="/"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-md text-xs font-medium border border-white/10 hover:bg-white/5 text-slate-300 hover:text-white transition-colors"
          >
            <Home size={14} />
            Back to Home
          </Link>
        </div>
      </div>
    </div>
  );
}

