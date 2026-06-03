"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "./AuthContext";
import * as Icons from "./Icons";

const NAV_ITEMS = [
  { href: "/", label: "Dashboard", Icon: Icons.Dashboard },
  { href: "/papers", label: "Papers", Icon: Icons.FileText },
  { href: "/screening", label: "Screening", Icon: Icons.Search },
  { href: "/evaluation", label: "Evaluation", Icon: Icons.Flask },
  { href: "/synthesis", label: "Synthesis", Icon: Icons.TrendingUp },
  { href: "/extraction", label: "Extraction", Icon: Icons.Settings },
  { href: "/matrix", label: "Matrix", Icon: Icons.Table },
  { href: "/zotero", label: "Zotero", Icon: Icons.BookOpen },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  return (
    <aside
      style={{
        width: 260,
        position: "fixed",
        top: 0,
        left: 0,
        bottom: 0,
        background: "var(--bg-secondary)",
        borderRight: "1px solid var(--border-color)",
        display: "flex",
        flexDirection: "column",
        padding: "24px 0",
        zIndex: 50,
      }}
    >
      {/* Logo */}
      <div style={{ padding: "0 24px", marginBottom: 40 }}>
        <h1 style={{ fontSize: 22, fontWeight: 800, margin: 0 }}>
          <span className="gradient-text">Scholar</span>{" "}
          <span style={{ color: "var(--text-secondary)", fontWeight: 500 }}>Sense</span>
        </h1>
        <p style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 4, letterSpacing: "0.05em" }}>
          SYSTEMATIC LITERATURE REVIEW
        </p>
      </div>

      {/* Pipeline label */}
      <div style={{ padding: "0 24px", marginBottom: 8 }}>
        <p style={{ fontSize: 10, fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em" }}>
          Pipeline
        </p>
      </div>

      {/* Nav items */}
      <nav style={{ flex: 1 }}>
        {NAV_ITEMS.map((item) => {
          const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
          const Icon = item.Icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 12,
                padding: "12px 24px",
                fontSize: 14,
                fontWeight: isActive ? 600 : 400,
                color: isActive ? "var(--accent-blue)" : "var(--text-secondary)",
                background: isActive ? "rgba(79, 142, 255, 0.08)" : "transparent",
                borderRight: isActive ? "3px solid var(--accent-blue)" : "3px solid transparent",
                textDecoration: "none",
                transition: "all 0.2s",
              }}
            >
              <Icon size={18} color={isActive ? "var(--accent-blue)" : "var(--text-secondary)"} />
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Footer with user info & logout */}
      <div style={{ padding: "16px 24px", borderTop: "1px solid var(--border-color)", display: "flex", flexDirection: "column", gap: 12 }}>
        {user && (
          <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
            <p style={{
              fontSize: 13,
              fontWeight: 600,
              color: "var(--text-primary)",
              margin: 0,
              overflow: "hidden",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
              display: "flex",
              alignItems: "center",
              gap: 6
            }}>
              <Icons.User size={14} color="var(--text-secondary)" />
              {user.name}
            </p>
            <p style={{ fontSize: 11, color: "var(--text-muted)", margin: 0, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", paddingLeft: 20 }}>
              {user.email}
            </p>
          </div>
        )}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <p style={{ fontSize: 10, color: "var(--text-muted)", margin: 0 }}>v2.0.0 • AI</p>
          <button
            onClick={logout}
            style={{
              background: "transparent",
              border: "none",
              color: "var(--accent-rose)",
              fontSize: 12,
              fontWeight: 600,
              cursor: "pointer",
              padding: "4px 8px",
              borderRadius: 4,
              transition: "background 0.2s",
              display: "flex",
              alignItems: "center",
              gap: 4
            }}
            onMouseEnter={(e) => (e.currentTarget.style.background = "rgba(244, 114, 182, 0.08)")}
            onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
          >
            Logout
            <Icons.LogOut size={12} color="var(--accent-rose)" />
          </button>
        </div>
      </div>
    </aside>
  );
}
