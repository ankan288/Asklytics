"use client";

import Link from "next/link";
import { ArrowLeft, FileText, Scale, ShieldAlert, Award, AlertTriangle, Copyright } from "lucide-react";
import { Footer } from "@/components/ui/Footer";

export default function TermsAndConditionsPage() {
  const lastUpdated = "November 16, 2026";

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
            <Scale size={18} className="text-indigo-400" />
            <span className="text-white font-semibold text-sm">Asklytics Legal Hub</span>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-6 py-14 flex-1">
        {/* Title */}
        <div className="mb-12">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-medium mb-4">
            <FileText size={12} />
            User Agreement & Service Terms
          </div>
          <h1 className="text-4xl md:text-5xl font-extrabold text-white tracking-tight mb-4">
            Terms and Conditions
          </h1>
          <p className="text-slate-400 text-sm">
            Last Updated: <span className="text-slate-300 font-medium">{lastUpdated}</span> • Effective Date: January 1, 2026
          </p>
        </div>

        {/* Highlight Callout */}
        <div className="p-6 rounded-2xl bg-indigo-950/20 border border-indigo-500/30 mb-12">
          <h3 className="text-lg font-semibold text-white mb-2 flex items-center gap-2">
            <Scale size={18} className="text-indigo-400" />
            Agreement Overview
          </h3>
          <p className="text-slate-300 text-sm leading-relaxed">
            These Terms and Conditions govern your access to and use of the Asklytics platform, APIs, and associated web services. By creating an account, uploading datasets, or querying the platform, you agree to be bound by these Terms.
          </p>
        </div>

        {/* Terms Sections */}
        <div className="space-y-12 text-sm leading-relaxed text-slate-300">
          {/* Section 1 */}
          <section className="space-y-4">
            <h2 className="text-xl font-bold text-white flex items-center gap-2.5 border-b border-white/10 pb-2">
              <Award size={18} className="text-indigo-400" />
              1. Acceptance of Terms & Eligibility
            </h2>
            <p>
              By accessing or using Asklytics, you represent and warrant that you are at least 18 years of age (or have reached the age of majority in your jurisdiction) and possess the legal capacity to enter into binding agreements. If you are using Asklytics on behalf of a company or entity, you represent that you have authority to bind that entity.
            </p>
          </section>

          {/* Section 2 */}
          <section className="space-y-4">
            <h2 className="text-xl font-bold text-white flex items-center gap-2.5 border-b border-white/10 pb-2">
              <ShieldAlert size={18} className="text-indigo-400" />
              2. Acceptable Use Policy & Restrictions
            </h2>
            <p>
              You agree to use Asklytics exclusively for lawful, legitimate analytical and business intelligence purposes. You expressly agree that you will not:
            </p>
            <ul className="list-disc pl-6 space-y-2 text-slate-300">
              <li>
                Attempt to bypass, subvert, or exploit the Abstract Syntax Tree (AST) query sanitizer or driver-level read-only protections to execute destructive SQL statements (`DROP`, `DELETE`, `TRUNCATE`, `ALTER`, or SQL injection payloads).
              </li>
              <li>
                Upload datasets containing malicious code, viruses, or illegal material (including infringing intellectual property or unredacted confidential health/banking records without authorization).
              </li>
              <li>
                Conduct automated denial-of-service (DoS) attacks, scrape backend endpoints, or intentionally consume excessive computational or LLM token quotas.
              </li>
              <li>
                Reverse engineer, decompile, or create unauthorized derivative works of the proprietary components of the platform.
              </li>
            </ul>
          </section>

          {/* Section 3 */}
          <section className="space-y-4">
            <h2 className="text-xl font-bold text-white flex items-center gap-2.5 border-b border-white/10 pb-2">
              <AlertTriangle size={18} className="text-indigo-400" />
              3. AI-Generated Insights & Verifiability Disclaimer
            </h2>
            <p>
              Asklytics employs dual-model consensus, AST parsing, and deterministic claim recomputation to minimize hallucination and provide verified calculations. However:
            </p>
            <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-200/90 text-xs leading-relaxed">
              <strong>IMPORTANT DISCLAIMER:</strong> Analytical outputs, SQL queries, and generated visualizations are provided for informational and decision-support purposes only. They do not constitute formal legal, accounting, tax, or investment advice. You remain solely responsible for validating critical operational metrics prior to making high-stakes business or financial commitments.
            </div>
          </section>

          {/* Section 4 */}
          <section className="space-y-4">
            <h2 className="text-xl font-bold text-white flex items-center gap-2.5 border-b border-white/10 pb-2">
              <Copyright size={18} className="text-indigo-400" />
              4. Copyright, Data Ownership & Third-Party Embeds
            </h2>
            <ul className="list-disc pl-6 space-y-3 text-slate-300">
              <li>
                <strong className="text-white">Your Proprietary Data:</strong> You retain 100% full ownership, rights, title, and copyright to all CSV files, relational databases, business prompts, and derived business insights processed by the engine. Asklytics asserts zero ownership claims over your business records.
              </li>
              <li>
                <strong className="text-white">Platform Software & Source Code:</strong> The Asklytics engine, source code, visual components, algorithms, and documentation are protected by copyright and intellectual property laws and distributed under the terms of the MIT License where applicable.
              </li>
              <li>
                <strong className="text-white">Stock Imagery & Media Embeds:</strong> Visual assets, illustrations, animations, and icons utilized across the interface are sourced from vetted open and royalty-free repositories (such as the Unsplash License, CC0, and 21st.dev assets) or licensed under respective open-source terms. All third-party company names, logos, and trademarks (e.g., Google Gemini, Groq, PostgreSQL, SQLite) belong to their respective owners.
              </li>
            </ul>
          </section>

          {/* Section 5 */}
          <section className="space-y-4">
            <h2 className="text-xl font-bold text-white flex items-center gap-2.5 border-b border-white/10 pb-2">
              <Scale size={18} className="text-indigo-400" />
              5. Limitation of Liability & Warranties
            </h2>
            <p>
              To the maximum extent permitted by applicable law, the Asklytics platform is provided on an <strong>"AS IS" and "AS AVAILABLE"</strong> basis, without warranties of any kind, whether express, statutory, or implied.
            </p>
            <p>
              In no event shall Asklytics, its maintainers, or affiliates be liable for any indirect, incidental, special, consequential, or punitive damages, including loss of profits, data corruption, or business interruption, arising out of or related to your use of the platform.
            </p>
          </section>

          {/* Section 6 */}
          <section className="space-y-4">
            <h2 className="text-xl font-bold text-white flex items-center gap-2.5 border-b border-white/10 pb-2">
              6. Applicable Laws & Dispute Jurisdiction
            </h2>
            <p>
              These Terms and Conditions shall be governed by and construed in accordance with applicable commercial and digital service laws, without regard to conflict of law principles.
            </p>
            <p>
              For users located within the European Union, mandatory statutory consumer protections and GDPR regulations remain unaffected. Any unresolved dispute arising out of these terms shall be subject to confidential mediation or the competent courts of the applicable jurisdiction.
            </p>
          </section>

          {/* Section 7 */}
          <section className="space-y-4">
            <h2 className="text-xl font-bold text-white flex items-center gap-2.5 border-b border-white/10 pb-2">
              7. Changes to Terms & Contact
            </h2>
            <p>
              We reserve the right to revise or update these Terms periodically to reflect technical enhancements or statutory updates. Continued use of the platform following the posting of modifications constitutes your acceptance of the updated Terms.
            </p>
            <p className="text-xs text-slate-400">
              Questions regarding these Terms should be addressed to <span className="text-indigo-400">legal@asklytics.io</span>.
            </p>
          </section>
        </div>
      </main>

      {/* Footer */}
      <Footer />
    </div>
  );
}

