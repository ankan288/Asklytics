'use client'

import { useEffect, useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { login as apiLogin, register as apiRegister, getCurrentUser, setAuthToken, logoutApi } from '@/lib/api'
import type { User } from '@/lib/types'

export interface AuthUser {
  id: string
  email: string
  role?: string
  full_name?: string
}

export function useAuth() {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [accessToken, setAccessToken] = useState<string | null>(null)
  const [refreshToken, setRefreshToken] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const router = useRouter()

  // Check for existing token and restore session on mount with backend validation
  useEffect(() => {
    async function restoreSession() {
      try {
        if (typeof window === 'undefined') return

        const storedToken = localStorage.getItem('asklytics_token')
        const storedRefreshToken = localStorage.getItem('asklytics_refresh_token')
        const storedUser = localStorage.getItem('asklytics_user')

        if (storedToken) {
          setAuthToken(storedToken)
          setAccessToken(storedToken)
          if (storedRefreshToken) setRefreshToken(storedRefreshToken)

          if (storedUser) {
            try {
              setUser(JSON.parse(storedUser))
            } catch (e) {
              // Ignore parse error
            }
          }

          // Live backend verification: check user session against backend database
          try {
            const liveUser = await getCurrentUser()
            if (liveUser && liveUser.id) {
              const formatted: AuthUser = {
                id: liveUser.id,
                email: liveUser.email,
                role: liveUser.role || 'user',
                full_name: liveUser.display_name || liveUser.full_name,
              }
              setUser(formatted)
              localStorage.setItem('asklytics_user', JSON.stringify(formatted))
            } else {
              throw new Error('User not found on backend')
            }
          } catch (verifyErr) {
            console.warn('Backend login verification failed:', verifyErr)
            // If token invalid/expired, wipe session cleanly
            localStorage.removeItem('asklytics_token')
            localStorage.removeItem('asklytics_refresh_token')
            localStorage.removeItem('asklytics_user')
            setAuthToken(null)
            setUser(null)
            setAccessToken(null)
          }
        } else {
          setUser(null)
          setAuthToken(null)
          setAccessToken(null)
        }
      } catch (err) {
        console.error('Session restore failed:', err)
      } finally {
        setLoading(false)
      }
    }

    restoreSession()
  }, [])

  const signup = useCallback(async (email: string, password: string, fullName?: string) => {
    try {
      setLoading(true)
      setError(null)
      const res = await apiRegister({
        email,
        password,
        display_name: fullName,
      })

      if (res && res.access_token) {
        const authUser: AuthUser = {
          id: res.user.id,
          email: res.user.email,
          role: res.user.role || 'user',
          full_name: res.user.display_name || res.user.full_name || fullName,
        }
        setUser(authUser)
        setAccessToken(res.access_token)
        setRefreshToken(res.refresh_token)
        setAuthToken(res.access_token)

        if (typeof window !== 'undefined') {
          localStorage.setItem('asklytics_token', res.access_token)
          localStorage.setItem('asklytics_refresh_token', res.refresh_token)
          localStorage.setItem('asklytics_user', JSON.stringify(authUser))
        }
        return res
      }
      throw new Error('Registration failed')
    } catch (err: any) {
      const message = err.message || 'Registration failed. Please try again.'
      setError(message)
      throw new Error(message)
    } finally {
      setLoading(false)
    }
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    try {
      setLoading(true)
      setError(null)
      const res = await apiLogin({
        email,
        password,
      })

      if (res && res.access_token) {
        const authUser: AuthUser = {
          id: res.user.id,
          email: res.user.email,
          role: res.user.role || 'user',
          full_name: res.user.display_name || res.user.full_name,
        }
        setUser(authUser)
        setAccessToken(res.access_token)
        setRefreshToken(res.refresh_token)
        setAuthToken(res.access_token)

        if (typeof window !== 'undefined') {
          localStorage.setItem('asklytics_token', res.access_token)
          localStorage.setItem('asklytics_refresh_token', res.refresh_token)
          localStorage.setItem('asklytics_user', JSON.stringify(authUser))
        }
        return res
      }
      throw new Error('Login failed')
    } catch (err: any) {
      const message = err.message || 'Invalid email or password'
      setError(message)
      throw new Error(message)
    } finally {
      setLoading(false)
    }
  }, [])

  const logout = useCallback(async () => {
    try {
      setError(null)
      setUser(null)
      setAccessToken(null)
      setRefreshToken(null)
      setAuthToken(null)
      logoutApi()

      if (typeof window !== 'undefined') {
        localStorage.removeItem('asklytics_token')
        localStorage.removeItem('asklytics_refresh_token')
        localStorage.removeItem('asklytics_user')
      }

      router.push('/login')
    } catch (err: any) {
      console.error('Logout error:', err)
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
    isAuthenticated: !!user,
  }
}
