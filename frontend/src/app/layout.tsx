import type { Metadata } from "next";
import "./globals.css";
import AppWrapper from "@/components/AppWrapper";

export const metadata: Metadata = {
  title: "Scholar Sense — AI-Powered Systematic Literature Review",
  description: "Structured, verifiable, multi-document analysis platform for systematic literature reviews",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
      </head>
      <body style={{ margin: 0, minHeight: "100vh" }}>
        <AppWrapper>{children}</AppWrapper>
      </body>
    </html>
  );
}
