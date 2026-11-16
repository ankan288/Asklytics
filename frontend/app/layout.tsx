import type { Metadata } from "next";
import "./globals.css";
import { ToastProvider } from "@/components/ui/Toast";
import { CookieConsent } from "@/components/ui/CookieConsent";
import { StickyMobileCTA } from "@/components/ui/StickyMobileCTA";

export const metadata: Metadata = {
  metadataBase: new URL("http://localhost:3000"),
  title: {
    default: "Asklytics — Verifiable Conversational BI & Analytics Platform",
    template: "%s | Asklytics",
  },
  description: "Ask business questions in plain English, get AST-guarded SQL, mathematically verified insights, and interactive charts in seconds.",
  keywords: [
    "Conversational Analytics",
    "Text to SQL",
    "Business Intelligence",
    "AI Dashboard",
    "Data Analytics",
    "Verified Insights",
  ],
  authors: [{ name: "Asklytics" }],
  openGraph: {
    title: "Asklytics — Verifiable Conversational BI & Analytics Platform",
    description: "Ask business questions in plain English, get instant verified dashboards.",
    siteName: "Asklytics",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        <ToastProvider>
          {children}
          <StickyMobileCTA />
          <CookieConsent />
        </ToastProvider>
      </body>
    </html>
  );
}
