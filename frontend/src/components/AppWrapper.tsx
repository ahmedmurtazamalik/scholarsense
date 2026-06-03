"use client";

import React from "react";
import { usePathname } from "next/navigation";
import { AuthProvider, useAuth } from "./AuthContext";
import Sidebar from "./Sidebar";

function AppContent({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { loading } = useAuth();
  const isLoginPage = pathname === "/login";

  if (loading) {
    return (
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          minHeight: "100vh",
          background: "radial-gradient(circle at center, #121225 0%, #0a0a0f 100%)",
          color: "var(--text-secondary)",
          gap: 16,
        }}
      >
        <div
          style={{
            width: 36,
            height: 36,
            border: "3px solid rgba(79, 142, 255, 0.1)",
            borderTopColor: "var(--accent-blue)",
            borderRadius: "50%",
            animation: "spin 1s linear infinite",
          }}
        />
        <span style={{ fontSize: 13, fontWeight: 500, letterSpacing: "0.05em" }}>
          Authenticating pipeline...
        </span>
        <style jsx global>{`
          @keyframes spin {
            to { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", minHeight: "100vh", width: "100%" }}>
      {!isLoginPage && <Sidebar />}
      <main
        style={{
          flex: 1,
          padding: "32px",
          overflowY: "auto",
          marginLeft: isLoginPage ? 0 : "260px",
          transition: "margin-left 0.2s ease-in-out",
        }}
      >
        <div className="page-enter">{children}</div>
      </main>
    </div>
  );
}

export default function AppWrapper({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <AppContent>{children}</AppContent>
    </AuthProvider>
  );
}
