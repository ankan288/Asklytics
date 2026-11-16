"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { Cookie, ShieldCheck, X } from "lucide-react";

export function CookieConsent() {
  const [show, setShow] = useState(false);

  useEffect(() => {
    // Check if consent has already been given
    const consent = localStorage.getItem("asklytics_cookie_consent");
    if (!consent) {
      // Small timeout for smooth entrance
      const timer = setTimeout(() => setShow(true), 800);
      return () => clearTimeout(timer);
    }
  }, []);

  const handleAccept = (type: "accepted" | "essential") => {
    localStorage.setItem("asklytics_cookie_consent", type);
    localStorage.setItem("asklytics_cookie_consent_timestamp", new Date().toISOString());
    window.dispatchEvent(new Event("cookie-consent-updated"));
    setShow(false);
  };

  return (
    <AnimatePresence>
      {show && (
        <motion.div
          initial={{ y: 80, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 80, opacity: 0 }}
          transition={{ duration: 0.4, ease: "easeOut" }}
          className="fixed bottom-5 left-4 right-4 md:left-auto md:right-6 md:max-w-xl z-50 pointer-events-auto"
        >
          <div className="bg-[#0b101f]/95 border border-indigo-500/30 backdrop-blur-xl shadow-2xl rounded-2xl p-5 text-white">
            <div className="flex items-start gap-4">
              <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center shrink-0 text-indigo-400 mt-0.5">
                <Cookie size={20} />
              </div>

              <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <h4 className="text-sm font-semibold text-white flex items-center gap-1.5">
                    Cookie & Data Privacy Choice
                    <ShieldCheck size={14} className="text-emerald-400" />
                  </h4>
                  <button
                    onClick={() => handleAccept("essential")}
                    className="text-slate-400 hover:text-white transition-colors p-1"
                    aria-label="Dismiss cookie notice"
                  >
                    <X size={16} />
                  </button>
                </div>

                <p className="text-xs text-slate-300 leading-relaxed mb-4">
                  Asklytics uses essential session tokens and local storage to authenticate users, manage conversation state, and ensure AST-guarded query safety. We never sell your personal data or uploaded CSV files. Learn more in our{" "}
                  <Link
                    href="/cookies"
                    className="text-indigo-400 hover:text-indigo-300 underline underline-offset-2"
                  >
                    Cookie Policy
                  </Link>{" "}
                  and{" "}
                  <Link
                    href="/privacy"
                    className="text-indigo-400 hover:text-indigo-300 underline underline-offset-2"
                  >
                    Privacy Policy
                  </Link>.
                </p>

                <div className="flex flex-wrap items-center gap-2.5">
                  <button
                    onClick={() => handleAccept("accepted")}
                    className="px-4 py-2 text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-colors shadow-md shadow-indigo-600/20 cursor-pointer"
                  >
                    Accept All Cookies
                  </button>
                  <button
                    onClick={() => handleAccept("essential")}
                    className="px-3.5 py-2 text-xs font-medium border border-white/20 hover:border-white/40 text-slate-300 hover:text-white rounded-lg transition-colors cursor-pointer"
                  >
                    Essential Only
                  </button>
                  <Link
                    href="/cookies"
                    className="px-3 py-2 text-xs text-slate-400 hover:text-slate-200 transition-colors ml-auto"
                  >
                    Customize
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

export default CookieConsent;

