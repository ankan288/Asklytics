"use client";

import Link from "next/link";
import { BarChart2, Shield, FileText, Cookie, Heart } from "lucide-react";

export function Footer() {
  return (
    <footer className="relative z-10 border-t border-white/10 bg-[#050810]/80 backdrop-blur-md text-slate-400 py-12 px-6">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-8">
        {/* Brand */}
        <div className="flex flex-col items-center md:items-start gap-2">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 bg-indigo-600 rounded-lg flex items-center justify-center">
              <BarChart2 size={16} className="text-white" />
            </div>
            <span className="text-white font-bold text-base tracking-tight">Asklytics</span>
          </div>
          <p className="text-xs text-slate-400 max-w-sm text-center md:text-left">
            Verifiable conversational business intelligence & automated SQL analytics engine.
          </p>
        </div>

        {/* Legal & Policy Navigation */}
        <div className="flex flex-wrap items-center justify-center gap-6 text-xs font-medium">
          <Link
            href="/privacy"
            className="flex items-center gap-1.5 hover:text-white transition-colors"
          >
            <Shield size={14} className="text-indigo-400" />
            Privacy Policy
          </Link>
          <Link
            href="/terms"
            className="flex items-center gap-1.5 hover:text-white transition-colors"
          >
            <FileText size={14} className="text-indigo-400" />
            Terms & Conditions
          </Link>
          <Link
            href="/cookies"
            className="flex items-center gap-1.5 hover:text-white transition-colors"
          >
            <Cookie size={14} className="text-indigo-400" />
            Cookie Policy
          </Link>
          <Link
            href="/dashboard"
            className="hover:text-white transition-colors"
          >
            Dashboard
          </Link>
          <Link
            href="/components-demo"
            className="hover:text-white transition-colors"
          >
            Showcase
          </Link>
        </div>

        {/* Copyright */}
        <div className="text-xs text-slate-400 text-center md:text-right">
          <p>© {new Date().getFullYear()} Asklytics. All rights reserved.</p>
          <p className="text-[11px] text-slate-400 mt-1">
            Built with AST-guarded Text-to-SQL & Claim Verification
          </p>
        </div>
      </div>
    </footer>
  );
}

export default Footer;

