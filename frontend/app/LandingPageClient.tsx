'use client'

import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { motion } from 'framer-motion'
import dynamic from 'next/dynamic'
import { BarChart2, Sparkles, ArrowRight, ShieldCheck, Zap, Database, Lock } from 'lucide-react'
import { Footer } from '@/components/ui/Footer'
import { useAuth } from '@/hooks/useAuth'

const ColorBends = dynamic(() => import('@/components/ui/ColorBends'), { ssr: false })

const PRELOADED_QUERIES = [
  "What is the total revenue by product category?",
  "Show me monthly sales trends for 2022",
  "Compare average rating and revenue by payment method",
]

export default function LandingPageClient() {
  const router = useRouter()
  const { user } = useAuth()

  return (
    <div className="relative w-full min-h-screen overflow-hidden bg-black flex flex-col justify-between">
      {/* Dynamic Background */}
      <div className="absolute inset-0 w-full h-full pointer-events-none">
        <ColorBends
          colors={['#ff5c7a', '#8a5cff', '#00ffd1']}
          rotation={0}
          speed={0.2}
          scale={1}
          frequency={1}
          warpStrength={1}
          mouseInfluence={1}
          parallax={0.5}
          noise={0.1}
          transparent
          autoRotate={0}
        />
      </div>

      {/* Main Content Area */}
      <div className="relative z-10 w-full flex-1 flex flex-col justify-between">
        {/* Navigation Bar Above the Fold */}
        <header className="border-b border-white/10 bg-black/40 backdrop-blur-md px-6 py-4 sticky top-0 z-20">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            {/* Logo */}
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center shadow-lg shadow-indigo-600/30">
                <BarChart2 size={18} className="text-white" />
              </div>
              <span className="text-white font-bold text-lg tracking-tight">Asklytics</span>
              <span className="hidden sm:inline-block px-2 py-0.5 rounded-full text-[10px] font-semibold bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                v1.0 Verifiable BI
              </span>
            </div>

            {/* Nav Links */}
            <nav className="hidden md:flex items-center gap-6 text-xs font-medium text-slate-300">
              <Link href="/dashboard" className="hover:text-white transition-colors">
                Live Dashboard
              </Link>
              <Link href="/components-demo" className="hover:text-white transition-colors">
                Showcase
              </Link>
              <Link href="/privacy" className="hover:text-white transition-colors">
                Privacy & Security
              </Link>
            </nav>

            {/* Top Right Action Buttons */}
            <div className="flex items-center gap-3">
              {user ? (
                <>
                  <span className="text-xs text-slate-300 hidden sm:inline">{user.email}</span>
                  <Link
                    href="/dashboard"
                    className="flex items-center gap-1.5 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold rounded-xl transition-all shadow-md shadow-indigo-600/30 cursor-pointer"
                  >
                    <span>Dashboard</span>
                    <ArrowRight size={13} />
                  </Link>
                </>
              ) : (
                <>
                  <Link
                    href="/login"
                    className="text-xs font-semibold text-slate-200 hover:text-white px-3 py-2 rounded-lg transition-colors"
                  >
                    Sign In
                  </Link>
                  <Link
                    href="/login?redirect=/dashboard"
                    className="flex items-center gap-1.5 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold rounded-xl transition-all shadow-md shadow-indigo-600/30 cursor-pointer"
                  >
                    <span>Launch App</span>
                    <ArrowRight size={13} />
                  </Link>
                </>
              )}
            </div>
          </div>
        </header>

        {/* Hero Section — Explicitly Designed Above The Fold */}
        <section className="flex-1 flex items-center justify-center px-4 py-12 md:py-16">
          <div className="text-center max-w-4xl mx-auto">
            {/* Above the Fold Trust Pill */}
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/25 text-indigo-300 text-xs font-semibold mb-6 shadow-sm"
            >
              <Sparkles size={14} className="text-indigo-400" />
              <span>Verifiable Conversational Analytics • Zero Hallucinations</span>
            </motion.div>

            {/* High-Impact Headline */}
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, delay: 0.1 }}
              className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-extrabold text-white mb-6 leading-tight tracking-tight"
            >
              Ask Business Questions. <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-300 to-pink-400">
                Get Verified SQL & BI Charts.
              </span>
            </motion.h1>

            {/* Subtitle */}
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, delay: 0.2 }}
              className="text-sm sm:text-base md:text-lg text-slate-300 max-w-2xl mx-auto mb-8 leading-relaxed font-normal"
            >
              Upload any CSV or connect your database. Asklytics combines AST query safety, dual-model consensus, and claim-level mathematical verification so you never make decisions on invented metrics.
            </motion.p>

            {/* Primary Action CTAs — Prominently Above the Fold */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, delay: 0.3 }}
              className="flex flex-col sm:flex-row items-center justify-center gap-3.5 mb-10"
            >
              <button
                onClick={() => router.push('/dashboard')}
                className="w-full sm:w-auto px-7 py-3.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl transition-all shadow-xl shadow-indigo-600/30 flex items-center justify-center gap-2 text-sm cursor-pointer"
              >
                <span>Launch Live Dashboard</span>
                <ArrowRight size={16} />
              </button>
              <button
                onClick={() => router.push('/register')}
                className="w-full sm:w-auto px-7 py-3.5 bg-white/10 hover:bg-white/20 text-white font-semibold rounded-xl border border-white/15 backdrop-blur-md transition-all text-sm cursor-pointer"
              >
                Create Free Account
              </button>
            </motion.div>

            {/* Interactive Query Chips Above the Fold */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, delay: 0.4 }}
              className="pt-2"
            >
              <p className="text-[11px] uppercase tracking-wider text-slate-400 font-semibold mb-3">
                Try asking in the dashboard:
              </p>
              <div className="flex flex-wrap items-center justify-center gap-2">
                {PRELOADED_QUERIES.map((q, idx) => (
                  <button
                    key={idx}
                    onClick={() => router.push('/dashboard')}
                    className="text-xs bg-slate-900/70 hover:bg-indigo-950/60 border border-white/10 hover:border-indigo-500/40 text-slate-300 hover:text-white px-3.5 py-1.5 rounded-full transition-all cursor-pointer shadow-sm"
                  >
                    💡 &ldquo;{q}&rdquo;
                  </button>
                ))}
              </div>
            </motion.div>

            {/* Trust Badges */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.9, delay: 0.5 }}
              className="flex flex-wrap items-center justify-center gap-6 mt-10 pt-6 border-t border-white/5 text-[11px] text-slate-400"
            >
              <span className="flex items-center gap-1.5">
                <ShieldCheck size={14} className="text-emerald-400" />
                AST-Guarded SQL (sqlglot)
              </span>
              <span className="flex items-center gap-1.5">
                <Lock size={14} className="text-emerald-400" />
                Read-Only Engine Isolation
              </span>
              <span className="flex items-center gap-1.5">
                <Zap size={14} className="text-emerald-400" />
                Under 2s Sub-Second Latency
              </span>
              <span className="flex items-center gap-1.5">
                <Database size={14} className="text-emerald-400" />
                100% Deterministic Claim Check
              </span>
            </motion.div>
          </div>
        </section>

        {/* Global Footer */}
        <Footer />
      </div>
    </div>
  )
}
