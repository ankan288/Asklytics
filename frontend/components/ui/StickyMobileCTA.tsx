"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import { Sparkles, ArrowRight } from "lucide-react";

export function StickyMobileCTA() {
  const pathname = usePathname();

  // Hide on dashboard and auth pages to not interfere with chat input / auth forms
  if (pathname === "/dashboard" || pathname === "/login" || pathname === "/register") {
    return null;
  }

  return (
    <div className="md:hidden fixed bottom-0 left-0 right-0 z-30 bg-[#050810]/90 backdrop-blur-lg border-t border-white/10 p-3.5 px-4 shadow-2xl safe-area-pb">
      <div className="flex items-center justify-between gap-3 max-w-md mx-auto">
        <div className="flex items-center gap-2 min-w-0">
          <div className="w-8 h-8 rounded-lg bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center shrink-0 text-indigo-400">
            <Sparkles size={16} />
          </div>
          <div className="truncate">
            <p className="text-xs font-semibold text-white leading-tight truncate">
              Instant AI Analytics
            </p>
            <p className="text-[10px] text-slate-400 leading-tight truncate">
              No SQL required
            </p>
          </div>
        </div>

        <Link
          href="/dashboard"
          className="shrink-0 flex items-center gap-1.5 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold rounded-xl transition-all shadow-md shadow-indigo-600/30 cursor-pointer"
        >
          <span>Try Demo</span>
          <ArrowRight size={13} />
        </Link>
      </div>
    </div>
  );
}

export default StickyMobileCTA;

