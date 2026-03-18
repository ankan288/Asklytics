"use client";
import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { BarChart2, Mail, Lock, ArrowRight, AlertCircle } from "lucide-react";
import dynamic from "next/dynamic";
import { useAuth } from "@/hooks/useAuth";

const LightRays = dynamic(() => import("@/components/ui/LightRays"), { ssr: false });

export default function RegisterPage() {
  const router = useRouter();
  const { signup, loading } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!email || !password || !confirm) {
      setError("Please fill in all fields");
      return;
    }

    if (password !== confirm) {
      setError("Passwords do not match");
      return;
    }

    if (password.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }

    try {
      await signup(email, password);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Signup failed");
    }
  };

  return (
    <div className="relative h-screen w-screen overflow-hidden bg-[#050810] flex items-center justify-center">
      {/* Background */}
      <div className="absolute inset-0 z-0">
        <LightRays
          raysOrigin="top-center"
          raysColor="#ffffff"
          raysSpeed={1}
          lightSpread={0.5}
          rayLength={3}
          followMouse={true}
          mouseInfluence={0.1}
          noiseAmount={0}
          distortion={0}
          pulsating={false}
          fadeDistance={1}
          saturation={1}
        />
      </div>

      {/* Card — Glassmorphism */}
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative z-10 w-full max-w-md px-4"
      >
        <div
          className="relative overflow-hidden rounded-3xl p-8"
          style={{
            background: "rgba(255, 255, 255, 0.04)",
            backdropFilter: "blur(48px) saturate(180%) brightness(1.08)",
            WebkitBackdropFilter: "blur(48px) saturate(180%) brightness(1.08)",
            border: "1px solid rgba(255, 255, 255, 0.14)",
            boxShadow:
              "0 32px 64px rgba(0,0,0,0.55), inset 0 1px 0 rgba(255,255,255,0.28), inset 0 -1px 0 rgba(255,255,255,0.05), inset 1px 0 0 rgba(255,255,255,0.10), inset -1px 0 0 rgba(255,255,255,0.05)",
          }}
        >
          {/* Shimmer refraction overlay */}
          <div
            className="absolute inset-0 pointer-events-none rounded-3xl"
            style={{
              background:
                "linear-gradient(135deg, rgba(255,255,255,0.11) 0%, rgba(255,255,255,0.03) 40%, transparent 70%)",
            }}
          />

          {/* Logo */}
          <div className="relative flex items-center gap-2.5 mb-8">
            <div className="w-8 h-8 bg-white/20 backdrop-blur-sm rounded-lg flex items-center justify-center border border-white/20">
              <BarChart2 size={17} className="text-white" />
            </div>
            <span className="text-white/90 font-semibold text-sm">Asklytics</span>
          </div>

          <h1 className="relative text-2xl font-bold text-white mb-1">Create an account</h1>
          <p className="relative text-white/50 text-sm mb-8">Start building dashboards in seconds</p>

          {error && (
            <div className="relative mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/20 flex items-start gap-2">
              <AlertCircle size={16} className="text-red-400 mt-0.5 flex-shrink-0" />
              <p className="text-red-400 text-xs">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="relative space-y-4">
            <div>
              <label className="text-white/50 text-xs mb-1.5 block">Email</label>
              <div className="relative">
                <Mail size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-white/40" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  style={{
                    background: "rgba(255,255,255,0.07)",
                    border: "1px solid rgba(255,255,255,0.14)",
                    WebkitBackdropFilter: "blur(10px)",
                    backdropFilter: "blur(10px)",
                  }}
                  className="w-full text-white placeholder-white/30 rounded-xl pl-9 pr-4 py-2.5 text-sm outline-none focus:border-white/30 transition-colors"
                />
              </div>
            </div>

            <div>
              <label className="text-white/50 text-xs mb-1.5 block">Password</label>
              <div className="relative">
                <Lock size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-white/40" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  style={{
                    background: "rgba(255,255,255,0.07)",
                    border: "1px solid rgba(255,255,255,0.14)",
                    WebkitBackdropFilter: "blur(10px)",
                    backdropFilter: "blur(10px)",
                  }}
                  className="w-full text-white placeholder-white/30 rounded-xl pl-9 pr-4 py-2.5 text-sm outline-none focus:border-white/30 transition-colors"
                />
              </div>
            </div>

            <div>
              <label className="text-white/50 text-xs mb-1.5 block">Confirm Password</label>
              <div className="relative">
                <Lock size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-white/40" />
                <input
                  type="password"
                  value={confirm}
                  onChange={(e) => setConfirm(e.target.value)}
                  placeholder="••••••••"
                  style={{
                    background: "rgba(255,255,255,0.07)",
                    border: "1px solid rgba(255,255,255,0.14)",
                    WebkitBackdropFilter: "blur(10px)",
                    backdropFilter: "blur(10px)",
                  }}
                  className="w-full text-white placeholder-white/30 rounded-xl pl-9 pr-4 py-2.5 text-sm outline-none focus:border-white/30 transition-colors"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              style={{
                background: loading ? "rgba(255,255,255,0.5)" : "rgba(255,255,255,0.92)",
                boxShadow: "0 4px 20px rgba(255,255,255,0.15), inset 0 1px 0 rgba(255,255,255,0.8)",
              }}
              className="w-full flex items-center justify-center gap-2 text-slate-900 font-semibold py-2.5 rounded-xl transition-all hover:bg-white text-sm mt-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? "Creating account..." : "Create Account"}
              <ArrowRight size={15} />
            </button>
          </form>

          <p className="relative text-white/35 text-xs text-center mt-6">
            Already have an account?{" "}
            <Link href="/login" className="text-white/70 hover:text-white transition-colors">
              Sign in
            </Link>
          </p>
        </div>
      </motion.div>
    </div>
  );
}
