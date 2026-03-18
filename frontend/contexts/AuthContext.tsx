"use client";

import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from "react";
import { login as apiLogin, register as apiRegister, logoutApi, setAuthToken, getCurrentUser, refreshToken } from "@/lib/api";
import type { User, LoginRequest, SignUpRequest } from "@/lib/types";

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (data: LoginRequest) => Promise<void>;
  register: (data: SignUpRequest) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const TOKEN_KEY = "bi_access_token";
const REFRESH_KEY = "bi_refresh_token";
const USER_KEY = "bi_user";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Restore auth state from localStorage on mount
  useEffect(() => {
    const storedToken = localStorage.getItem(TOKEN_KEY);
    const storedUser = localStorage.getItem(USER_KEY);

    if (storedToken && storedUser) {
      setAuthToken(storedToken);
      try {
        setUser(JSON.parse(storedUser));
      } catch {
        // Invalid stored user, clear everything
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(REFRESH_KEY);
        localStorage.removeItem(USER_KEY);
      }
    }
    setIsLoading(false);
  }, []);

  // Try to refresh token if we have a refresh token but no access token
  useEffect(() => {
    const tryRefresh = async () => {
      const storedRefresh = localStorage.getItem(REFRESH_KEY);
      const storedToken = localStorage.getItem(TOKEN_KEY);

      if (storedRefresh && !storedToken) {
        try {
          const response = await refreshToken(storedRefresh);
          localStorage.setItem(TOKEN_KEY, response.access_token);
          localStorage.setItem(REFRESH_KEY, response.refresh_token);
          localStorage.setItem(USER_KEY, JSON.stringify(response.user));
          setUser(response.user);
        } catch {
          // Refresh failed, clear everything
          localStorage.removeItem(TOKEN_KEY);
          localStorage.removeItem(REFRESH_KEY);
          localStorage.removeItem(USER_KEY);
        }
      }
    };

    if (!isLoading && !user) {
      tryRefresh();
    }
  }, [isLoading, user]);

  const login = useCallback(async (data: LoginRequest) => {
    const response = await apiLogin(data);
    localStorage.setItem(TOKEN_KEY, response.access_token);
    localStorage.setItem(REFRESH_KEY, response.refresh_token);
    localStorage.setItem(USER_KEY, JSON.stringify(response.user));
    setUser(response.user);
  }, []);

  const register = useCallback(async (data: SignUpRequest) => {
    const response = await apiRegister(data);
    localStorage.setItem(TOKEN_KEY, response.access_token);
    localStorage.setItem(REFRESH_KEY, response.refresh_token);
    localStorage.setItem(USER_KEY, JSON.stringify(response.user));
    setUser(response.user);
  }, []);

  const logout = useCallback(() => {
    logoutApi();
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_KEY);
    localStorage.removeItem(USER_KEY);
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
