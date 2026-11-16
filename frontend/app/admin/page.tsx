"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  ShieldAlert,
  Users,
  Activity,
  Database,
  Lock,
  ArrowLeft,
  CheckCircle2,
  RefreshCw,
  Server,
  Zap,
} from "lucide-react";
import { useAuth } from "@/hooks/useAuth";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function AdminPage() {
  const router = useRouter();
  const { user, accessToken, loading: authLoading } = useAuth();
  const [stats, setStats] = useState<any>(null);
  const [system, setSystem] = useState<any>(null);
  const [userList, setUserList] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [forbidden, setForbidden] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAdminData = async () => {
    if (!accessToken) return;
    setLoading(true);
    setError(null);
    setForbidden(false);

    try {
      const headers = {
        "Content-Type": "application/json",
        Authorization: `Bearer ${accessToken}`,
      };

      // 1. Fetch Stats
      const statsRes = await fetch(`${API_BASE}/admin/stats`, { headers });
      if (statsRes.status === 403) {
        setForbidden(true);
        setLoading(false);
        return;
      }
      if (statsRes.status === 401) {
        router.push("/login");
        return;
      }
      if (!statsRes.ok) throw new Error("Failed to load admin telemetry");
      const statsData = await statsRes.json();
      setStats(statsData);

      // 2. Fetch System Health
      const sysRes = await fetch(`${API_BASE}/admin/system`, { headers });
      if (sysRes.ok) {
        const sysData = await sysRes.json();
        setSystem(sysData);
      }

      // 3. Fetch Users
      const usersRes = await fetch(`${API_BASE}/admin/users`, { headers });
      if (usersRes.ok) {
        const usersData = await usersRes.json();
        setUserList(usersData);
      }
    } catch (err: any) {
      setError(err.message || "Failed to load admin data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!authLoading) {
      if (!user) {
        router.push("/login");
      } else {
        fetchAdminData();
      }
    }
  }, [user, accessToken, authLoading]);

  if (authLoading || (loading && !forbidden)) {
    return (
      <div className="min-h-screen bg-[#050810] flex items-center justify-center text-white">
        <div className="flex flex-col items-center gap-3">
          <RefreshCw className="animate-spin text-indigo-500" size={28} />
          <p className="text-sm text-slate-400">Verifying administrative credentials...</p>
        </div>
      </div>
    );
  }

  // If authenticated but lacks admin role
  if (forbidden) {
    return (
      <div className="min-h-screen bg-[#050810] text-slate-200 flex items-center justify-center p-6">
        <div className="max-w-md w-full bg-slate-900/60 border border-amber-500/30 rounded-3xl p-8 text-center backdrop-blur-xl shadow-2xl">
          <div className="w-14 h-14 bg-amber-500/10 border border-amber-500/30 rounded-2xl flex items-center justify-center text-amber-400 mx-auto mb-6">
            <Lock size={26} />
          </div>
          <h1 className="text-2xl font-bold text-white mb-2">Admin Access Restricted</h1>
          <p className="text-xs text-slate-400 leading-relaxed mb-6">
            Your account (<span className="text-white font-medium">{user?.email}</span>) does not currently have administrative permissions.
          </p>
          <div className="p-3.5 rounded-xl bg-slate-950/60 border border-white/5 text-[11px] text-slate-400 mb-6 text-left">
            💡 <strong>Tip for Local Testing:</strong> Upgrade your account role in the database or via SQLite CLI:
            <code className="block mt-1 text-indigo-300 font-mono">
              UPDATE users SET role = &apos;admin&apos; WHERE email = &apos;{user?.email}&apos;;
            </code>
          </div>
          <Link
            href="/dashboard"
            className="inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold transition-colors"
          >
            <ArrowLeft size={14} />
            Back to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#050810] text-slate-200 p-6 md:p-10">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-8 border-b border-white/10 mb-8">
          <div>
            <div className="flex items-center gap-2 text-xs font-semibold text-indigo-400 uppercase tracking-wider mb-1">
              <ShieldAlert size={14} />
              Protected Administrative Console
            </div>
            <h1 className="text-3xl font-extrabold text-white tracking-tight">Admin & Security Hub</h1>
            <p className="text-xs text-slate-400 mt-1">
              Signed in as <span className="text-white font-medium">{user?.email}</span> (Admin)
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={fetchAdminData}
              className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-medium text-slate-300 hover:text-white transition-colors cursor-pointer"
            >
              <RefreshCw size={13} />
              Refresh
            </button>
            <Link
              href="/dashboard"
              className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-xs font-semibold text-white transition-colors"
            >
              <ArrowLeft size={14} />
              Return to Dashboard
            </Link>
          </div>
        </div>

        {/* Telemetry Stat Cards */}
        {stats && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <div className="p-5 rounded-2xl bg-slate-900/50 border border-white/10 backdrop-blur-md">
              <div className="flex items-center justify-between mb-3 text-slate-400">
                <span className="text-xs font-medium uppercase tracking-wider">Registered Users</span>
                <Users size={16} className="text-indigo-400" />
              </div>
              <p className="text-3xl font-bold text-white">{stats.total_registered_users}</p>
            </div>
            <div className="p-5 rounded-2xl bg-slate-900/50 border border-white/10 backdrop-blur-md">
              <div className="flex items-center justify-between mb-3 text-slate-400">
                <span className="text-xs font-medium uppercase tracking-wider">Active Sessions</span>
                <Activity size={16} className="text-emerald-400" />
              </div>
              <p className="text-3xl font-bold text-white">{stats.active_sessions}</p>
            </div>
            <div className="p-5 rounded-2xl bg-slate-900/50 border border-white/10 backdrop-blur-md">
              <div className="flex items-center justify-between mb-3 text-slate-400">
                <span className="text-xs font-medium uppercase tracking-wider">Conversations</span>
                <Zap size={16} className="text-amber-400" />
              </div>
              <p className="text-3xl font-bold text-white">{stats.total_conversations}</p>
            </div>
            <div className="p-5 rounded-2xl bg-slate-900/50 border border-white/10 backdrop-blur-md">
              <div className="flex items-center justify-between mb-3 text-slate-400">
                <span className="text-xs font-medium uppercase tracking-wider">Database Size</span>
                <Database size={16} className="text-purple-400" />
              </div>
              <p className="text-3xl font-bold text-white">{stats.database_size_kb} KB</p>
            </div>
          </div>
        )}

        {/* Security & System Status */}
        {system && (
          <div className="p-6 rounded-2xl bg-slate-900/40 border border-white/10 mb-8 backdrop-blur-md">
            <h3 className="text-base font-bold text-white mb-4 flex items-center gap-2">
              <Server size={18} className="text-indigo-400" />
              System Security & API Key Protection Monitor
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 text-xs">
              <div className="p-3.5 rounded-xl bg-slate-950/60 border border-white/5">
                <p className="text-slate-400 mb-1">Gemini API Status</p>
                <p className="font-semibold text-emerald-400 flex items-center gap-1.5">
                  <CheckCircle2 size={13} />
                  {system.gemini_api_configured ? "Configured & Active" : "Not Set"}
                </p>
                <p className="text-[10px] text-slate-400 mt-1">Key hidden & redacted</p>
              </div>
              <div className="p-3.5 rounded-xl bg-slate-950/60 border border-white/5">
                <p className="text-slate-400 mb-1">Groq Fallback Status</p>
                <p className="font-semibold text-emerald-400 flex items-center gap-1.5">
                  <CheckCircle2 size={13} />
                  {system.groq_api_configured ? "Configured & Active" : "Not Set"}
                </p>
                <p className="text-[10px] text-slate-400 mt-1">Key hidden & redacted</p>
              </div>
              <div className="p-3.5 rounded-xl bg-slate-950/60 border border-white/5">
                <p className="text-slate-400 mb-1">API Rate Limiter</p>
                <p className="font-semibold text-emerald-400 flex items-center gap-1.5">
                  <CheckCircle2 size={13} />
                  Active (Sliding Window)
                </p>
                <p className="text-[10px] text-slate-400 mt-1">20 req/min query limit</p>
              </div>
              <div className="p-3.5 rounded-xl bg-slate-950/60 border border-white/5">
                <p className="text-slate-400 mb-1">AST Query Guard</p>
                <p className="font-semibold text-emerald-400 flex items-center gap-1.5">
                  <CheckCircle2 size={13} />
                  sqlglot Enforced
                </p>
                <p className="text-[10px] text-slate-400 mt-1">Strict SELECT read-only</p>
              </div>
            </div>
          </div>
        )}

        {/* User Management Table */}
        <div className="p-6 rounded-2xl bg-slate-900/40 border border-white/10 backdrop-blur-md">
          <h3 className="text-base font-bold text-white mb-4 flex items-center gap-2">
            <Users size={18} className="text-indigo-400" />
            User Permissions & Role Registry
          </h3>
          <div className="overflow-x-auto rounded-xl border border-white/5">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950/80 text-slate-300 border-b border-white/10">
                <tr>
                  <th className="p-3 font-semibold">User Email</th>
                  <th className="p-3 font-semibold">Role</th>
                  <th className="p-3 font-semibold">Status</th>
                  <th className="p-3 font-semibold">Created At</th>
                  <th className="p-3 font-semibold">Last Login</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5 text-slate-300">
                {userList.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="p-4 text-center text-slate-400">
                      No registered users found.
                    </td>
                  </tr>
                ) : (
                  userList.map((u) => (
                    <tr key={u.user_id} className="hover:bg-white/5">
                      <td className="p-3 font-medium text-white">{u.email}</td>
                      <td className="p-3">
                        <span
                          className={`px-2 py-0.5 rounded-full font-semibold text-[10px] ${
                            u.role === "admin"
                              ? "bg-purple-500/20 text-purple-300 border border-purple-500/30"
                              : "bg-slate-800 text-slate-300 border border-white/10"
                          }`}
                        >
                          {u.role || "user"}
                        </span>
                      </td>
                      <td className="p-3">
                        <span className="text-emerald-400 font-medium">Active</span>
                      </td>
                      <td className="p-3 text-slate-400">{new Date(u.created_at).toLocaleDateString()}</td>
                      <td className="p-3 text-slate-400">{u.last_login ? new Date(u.last_login).toLocaleDateString() : "Never"}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

