"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { ArrowLeft, Cookie, Info, CheckCircle2, RotateCcw, ShieldCheck, Settings } from "lucide-react";
import { Footer } from "@/components/ui/Footer";

export default function CookiePolicyPage() {
  const [currentConsent, setCurrentConsent] = useState<string>("Not Set");
  const [resetMessage, setResetMessage] = useState<string | null>(null);

  useEffect(() => {
    const val = localStorage.getItem("asklytics_cookie_consent");
    setCurrentConsent(val ? (val === "accepted" ? "All Cookies Accepted" : "Essential Only") : "No Preference Set");
  }, []);

  const handleReset = () => {
    localStorage.removeItem("asklytics_cookie_consent");
    localStorage.removeItem("asklytics_cookie_consent_timestamp");
    setCurrentConsent("No Preference Set");
    setResetMessage("Your cookie preferences have been cleared. Refreshing or navigating will re-display the consent prompt.");
    setTimeout(() => {
      window.location.reload();
    }, 1200);
  };

  return (
    <div className="min-h-screen bg-[#050810] text-slate-200 flex flex-col justify-between">
      {/* Header Navigation */}
      <nav className="border-b border-white/10 bg-[#050810]/80 backdrop-blur-md px-6 py-4 sticky top-0 z-20">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <Link
            href="/"
            className="flex items-center gap-2 text-sm text-slate-400 hover:text-white transition-colors"
          >
            <ArrowLeft size={16} />
            Back to Home
          </Link>
          <div className="flex items-center gap-2">
            <Cookie size={18} className="text-indigo-400" />
            <span className="text-white font-semibold text-sm">Asklytics Legal Hub</span>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-6 py-14 flex-1">
        {/* Title */}
        <div className="mb-12">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-medium mb-4">
            <Cookie size={12} />
            Transparency & Consent
          </div>
          <h1 className="text-4xl md:text-5xl font-extrabold text-white tracking-tight mb-4">
            Cookie Policy
          </h1>
          <p className="text-slate-400 text-sm">
            Last Updated: <span className="text-slate-300 font-medium">November 16, 2026</span> • Effective Date: January 1, 2026
          </p>
        </div>

        {/* Current User Consent Status Card */}
        <div className="p-6 rounded-2xl bg-indigo-950/20 border border-indigo-500/30 mb-12 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-xs uppercase tracking-wider text-indigo-400 font-semibold mb-1">
              <ShieldCheck size={15} />
              Your Current Status
            </div>
            <p className="text-lg font-bold text-white">
              {currentConsent}
            </p>
            <p className="text-xs text-slate-400 mt-0.5">
              Managed via your local browser storage.
            </p>
          </div>
          <button
            onClick={handleReset}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white text-xs font-medium transition-colors border border-white/10 cursor-pointer"
          >
            <RotateCcw size={14} />
            Reset Cookie Preferences
          </button>
        </div>

        {resetMessage && (
          <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs mb-8 flex items-center gap-2">
            <CheckCircle2 size={16} />
            {resetMessage}
          </div>
        )}

        {/* Policy Content */}
        <div className="space-y-12 text-sm leading-relaxed text-slate-300">
          {/* Section 1 */}
          <section className="space-y-4">
            <h2 className="text-xl font-bold text-white flex items-center gap-2.5 border-b border-white/10 pb-2">
              <Info size={18} className="text-indigo-400" />
              1. What Are Cookies and Local Storage?
            </h2>
            <p>
              Cookies and local browser storage (such as HTML5 `localStorage` and `sessionStorage`) are small data files placed on your device by websites you visit. They are widely used to make web applications work efficiently, preserve authentication sessions, and retain analytical context across page navigation turns.
            </p>
            <p>
              Asklytics prioritizes privacy-first architecture: <strong>we do not employ third-party advertising cookies, cross-site trackers, or data-broker pixels.</strong>
            </p>
          </section>

          {/* Section 2 */}
          <section className="space-y-4">
            <h2 className="text-xl font-bold text-white flex items-center gap-2.5 border-b border-white/10 pb-2">
              <Settings size={18} className="text-indigo-400" />
              2. Specific Storage Items Used by Asklytics
            </h2>
            <p>
              The table below provides a complete audit of the cookies and local storage tokens stored by our application:
            </p>
            
            <div className="overflow-x-auto rounded-xl border border-white/10 my-4">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-900/80 text-white border-b border-white/10">
                  <tr>
                    <th className="p-3 font-semibold">Identifier</th>
                    <th className="p-3 font-semibold">Category</th>
                    <th className="p-3 font-semibold">Purpose</th>
                    <th className="p-3 font-semibold">Duration</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5 text-slate-300 bg-slate-950/40">
                  <tr>
                    <td className="p-3 font-mono text-indigo-300">asklytics_cookie_consent</td>
                    <td className="p-3 text-emerald-400 font-medium">Essential</td>
                    <td className="p-3">Stores your consent preference (`accepted` or `essential`).</td>
                    <td className="p-3">1 Year</td>
                  </tr>
                  <tr>
                    <td className="p-3 font-mono text-indigo-300">asklytics_session_id</td>
                    <td className="p-3 text-emerald-400 font-medium">Essential</td>
                    <td className="p-3">Maintains conversation continuity and isolated table registry.</td>
                    <td className="p-3">Session</td>
                  </tr>
                  <tr>
                    <td className="p-3 font-mono text-indigo-300">asklytics_token</td>
                    <td className="p-3 text-emerald-400 font-medium">Essential</td>
                    <td className="p-3">JWT Bearer token validating authenticated requests.</td>
                    <td className="p-3">7 Days</td>
                  </tr>
                  <tr>
                    <td className="p-3 font-mono text-indigo-300">theme / dark_mode</td>
                    <td className="p-3 text-sky-400 font-medium">Functional</td>
                    <td className="p-3">Preserves your visual dark theme and UI preferences.</td>
                    <td className="p-3">Persistent</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>

          {/* Section 3 */}
          <section className="space-y-4">
            <h2 className="text-xl font-bold text-white flex items-center gap-2.5 border-b border-white/10 pb-2">
              3. Third-Party Embeds & CDN Storage
            </h2>
            <p>
              When rendering high-speed visual components, fonts, or illustrations, your browser may establish secure connections with external CDNs:
            </p>
            <ul className="list-disc pl-6 space-y-2 text-slate-300">
              <li>
                <strong className="text-white">Google Fonts:</strong> Requests for web fonts (`Inter`) are fetched from Google servers, which may log IP and user-agent strings for security and bandwidth optimization.
              </li>
              <li>
                <strong className="text-white">Image CDN Mirrors:</strong> Asset mirrors (`21st.dev`, `unsplash.com`) may cache standard browser headers strictly to deliver image files without tracking your identity.
              </li>
            </ul>
          </section>

          {/* Section 4 */}
          <section className="space-y-4">
            <h2 className="text-xl font-bold text-white flex items-center gap-2.5 border-b border-white/10 pb-2">
              4. How to Control and Delete Cookies
            </h2>
            <p>
              You have full autonomy over how cookies and web storage are stored on your device:
            </p>
            <ul className="list-disc pl-6 space-y-2 text-slate-300">
              <li>
                <strong className="text-white">Using Our In-App Control:</strong> You can click the <em>"Reset Cookie Preferences"</em> button at the top of this page at any time to clear stored consent and re-trigger your preference selection.
              </li>
              <li>
                <strong className="text-white">Browser Settings:</strong> Most modern browsers (Chrome, Edge, Firefox, Safari) allow you to view, delete, or block cookies via their Privacy & Security settings. Note that blocking strictly essential storage will prevent authentication and conversational state persistence.
              </li>
            </ul>
          </section>

          {/* Section 5 */}
          <section className="space-y-4">
            <h2 className="text-xl font-bold text-white flex items-center gap-2.5 border-b border-white/10 pb-2">
              5. Updates to this Policy
            </h2>
            <p>
              We may update this Cookie Policy occasionally to reflect technical changes or legal requirements. Any modifications will be posted here with an updated "Last Updated" timestamp.
            </p>
            <p className="text-xs text-slate-400">
              For any questions regarding our cookie practices, please contact <span className="text-indigo-400">privacy@asklytics.io</span>.
            </p>
          </section>
        </div>
      </main>

      {/* Footer */}
      <Footer />
    </div>
  );
}

