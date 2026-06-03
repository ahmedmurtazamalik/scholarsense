"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import { authApi, User } from "@/lib/api";

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  // Validate session on mount
  useEffect(() => {
    async function checkUser() {
      const token = localStorage.getItem("token");
      if (!token) {
        setUser(null);
        setLoading(false);
        return;
      }

      try {
        const userData = await authApi.me();
        setUser(userData);
      } catch (err) {
        // Token invalid or expired
        localStorage.removeItem("token");
        setUser(null);
      } finally {
        setLoading(false);
      }
    }
    checkUser();
  }, []);

  // Route protection
  useEffect(() => {
    if (!loading) {
      if (!user && pathname !== "/login") {
        router.push("/login");
      } else if (user && pathname === "/login") {
        router.push("/");
      }
    }
  }, [user, loading, pathname, router]);

  const login = async (email: string, password: string) => {
    setLoading(true);
    try {
      const res = await authApi.login(email, password);
      localStorage.setItem("token", res.access_token);
      const userData = await authApi.me();
      setUser(userData);
      router.push("/");
    } catch (err) {
      localStorage.removeItem("token");
      setUser(null);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const register = async (name: string, email: string, password: string) => {
    setLoading(true);
    try {
      await authApi.register(name, email, password);
      // Auto login after signup
      const res = await authApi.login(email, password);
      localStorage.setItem("token", res.access_token);
      const userData = await authApi.me();
      setUser(userData);
      router.push("/");
    } catch (err) {
      localStorage.removeItem("token");
      setUser(null);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem("token");
    setUser(null);
    router.push("/login");
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
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
