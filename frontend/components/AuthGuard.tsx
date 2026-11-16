'use client'

import { useEffect, useState } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()
  const router = useRouter()
  const pathname = usePathname()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    if (mounted && !loading && !user) {
      const redirectUrl = pathname ? `/login?redirect=${encodeURIComponent(pathname)}` : '/login'
      router.push(redirectUrl)
    }
  }, [user, loading, mounted, router, pathname])

  if (!mounted || loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-[#050810] text-white">
        <div className="relative flex flex-col items-center">
          <div className="w-12 h-12 rounded-2xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center mb-4 animate-pulse shadow-lg shadow-indigo-600/20">
            <div className="w-6 h-6 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin" />
          </div>
          <h2 className="text-sm font-semibold tracking-wide text-slate-200 mb-1">Checking Authentication</h2>
          <p className="text-xs text-slate-400">Verifying session with Asklytics backend...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return null
  }

  return <>{children}</>
}
