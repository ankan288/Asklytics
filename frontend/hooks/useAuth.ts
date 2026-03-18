'use client'

import { useEffect, useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { supabase } from '@/lib/supabaseClient'
import { setAuthToken } from '@/lib/api'

export interface AuthUser {
  id: string
  email: string
  full_name?: string
}

export function useAuth() {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [accessToken, setAccessToken] = useState<string | null>(null)
  const [refreshToken, setRefreshToken] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const router = useRouter()

  // Check for existing auth on mount
  useEffect(() => {
    async function checkAuth() {
      try {
        const { data: { session } } = await supabase.auth.getSession()

        if (session) {
          setUser({
            id: session.user.id,
            email: session.user.email || '',
            full_name: session.user.user_metadata?.full_name
          })
          setAccessToken(session.access_token)
          setRefreshToken(session.refresh_token)
          setAuthToken(session.access_token)  // Set token for API calls
        }
      } catch (err) {
        console.error('Auth check failed:', err)
      } finally {
        setLoading(false)
      }
    }

    checkAuth()

    // Subscribe to auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
      if (session) {
        setUser({
          id: session.user.id,
          email: session.user.email || '',
          full_name: session.user.user_metadata?.full_name
        })
        setAccessToken(session.access_token)
        setRefreshToken(session.refresh_token)
        setError(null)
      } else {
        setUser(null)
        setAccessToken(null)
        setRefreshToken(null)
      }
    })

    return () => subscription?.unsubscribe()
  }, [])

  const signup = useCallback(async (email: string, password: string, fullName?: string) => {
    try {
      setError(null)
      const { data, error: signupError } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: { full_name: fullName }
        }
      })

      if (signupError) throw signupError
      return data
    } catch (err: any) {
      const message = err.message || 'Signup failed'
      setError(message)
      throw err
    }
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    try {
      setError(null)
      const { data, error: loginError } = await supabase.auth.signInWithPassword({
        email,
        password
      })

      if (loginError) throw loginError

      if (data.session) {
        setAccessToken(data.session.access_token)
        setRefreshToken(data.session.refresh_token)
        setAuthToken(data.session.access_token)  // Set token for API calls
      }

      return data
    } catch (err: any) {
      const message = err.message || 'Login failed'
      setError(message)
      throw err
    }
  }, [])

  const logout = useCallback(async () => {
    try {
      setError(null)

      // Clear state first
      setUser(null)
      setAccessToken(null)
      setRefreshToken(null)
      setAuthToken(null)  // Clear token for API calls

      // Sign out from Supabase
      if (typeof supabase?.auth?.signOut === 'function') {
         await supabase.auth.signOut().catch(console.error);
      }

      // Force redirect
      router.push('/login')
    } catch (err: any) {
      console.error('Logout error:', err)
      // Even if Supabase fails, clear local state and redirect
      setUser(null)
      setAccessToken(null)
      setRefreshToken(null)
      setAuthToken(null)
      router.push('/login')
    }
  }, [router])

  return {
    user,
    accessToken,
    refreshToken,
    loading,
    error,
    signup,
    login,
    logout,
    isAuthenticated: !!user
  }
}
