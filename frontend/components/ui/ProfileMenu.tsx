"use client";
import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useRouter } from "next/navigation";
import { Settings, LogOut, Pencil, LogIn } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";

function getInitials(name: string) {
  if (!name) return "U";
  return name.split(" ").map((w) => w[0]).join("").toUpperCase().slice(0, 2);
}

export function ProfileMenu() {
  const { user, logout, isAuthenticated, loading } = useAuth();
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const displayName = user?.full_name || user?.email?.split("@")[0] || "User";
  const displayEmail = user?.email || "";
  const initials = getInitials(displayName);

  const handleLogout = async () => {
    setOpen(false);
    try {
      await logout();
      // logout() handles the redirect
    } catch (err) {
      console.error("Logout failed:", err);
    }
  };

  const handleLogin = () => {
    setOpen(false);
    router.push("/login");
  };

  // Show login button if not authenticated
  if (!loading && !isAuthenticated) {
    return (
      <button
        onClick={handleLogin}
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition-colors"
      >
        <LogIn size={14} />
        Sign In
      </button>
    );
  }

  return (
    <div ref={ref} className="relative shrink-0 z-50">
      {/* Avatar button */}
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-8 h-8 rounded-full bg-indigo-600 hover:bg-indigo-500 flex items-center justify-center text-white text-xs font-bold transition-colors ring-2 ring-transparent hover:ring-indigo-400/40"
      >
        {initials}
      </button>

      {/* Dropdown */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: -6 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: -6 }}
            transition={{ duration: 0.15 }}
            className="absolute right-0 top-10 w-64 z-50 rounded-2xl shadow-2xl"
            style={{
              background: "rgba(15, 23, 42, 0.95)",
              backdropFilter: "blur(20px)",
              WebkitBackdropFilter: "blur(20px)",
              border: "1px solid rgba(255,255,255,0.08)",
            }}
          >
            {/* User info */}
            <div className="px-4 pt-4 pb-3 flex items-center gap-3 border-b border-white/[0.06]">
              <div className="w-10 h-10 rounded-full bg-indigo-600 flex items-center justify-center text-white text-sm font-bold shrink-0">
                {initials}
              </div>
              <div className="min-w-0">
                <p className="text-white text-sm font-semibold truncate">{displayName}</p>
                <p className="text-slate-400 text-xs truncate">{displayEmail}</p>
              </div>
            </div>

            {/* Menu items */}
            <div className="py-1.5">
              <MenuItem icon={<Pencil size={14} />} label="Edit Profile" />
              <MenuItem icon={<Settings size={14} />} label="Settings" />
            </div>

            {/* Log out */}
            <div className="border-t border-white/[0.06] py-1.5">
              <MenuItem
                icon={<LogOut size={14} />}
                label="Log Out"
                accent="text-red-400"
                onClick={handleLogout}
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function MenuItem({
  icon, label, accent, onClick,
}: {
  icon: React.ReactNode;
  label: string;
  accent?: string;
  onClick?: () => void;
}) {
  return (
    <button
      onClick={(e) => {
        e.preventDefault();
        e.stopPropagation();
        if (onClick) onClick();
      }}
      className={`w-full flex items-center gap-3 px-4 py-2 text-sm hover:bg-white/[0.06] transition-colors text-left ${accent ?? "text-slate-300"}`}
    >
      <span className={`shrink-0 ${accent ?? "text-slate-500"}`}>{icon}</span>
      <span className="flex-1">{label}</span>
    </button>
  );
}
