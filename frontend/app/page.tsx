import type { Metadata } from 'next'
import LandingPageClient from './LandingPageClient'

export const metadata: Metadata = {
  title: "Asklytics — Verifiable Conversational BI & Analytics Platform",
  description: "Transform business questions into AST-guarded SQL, mathematically verified insights, and interactive charts in seconds. No SQL required.",
  openGraph: {
    title: "Asklytics — Verifiable Conversational BI & Analytics Platform",
    description: "Transform business questions into AST-guarded SQL, mathematically verified insights, and interactive charts in seconds.",
    url: "https://asklytics.io",
    siteName: "Asklytics",
    type: "website",
  },
}

export default function Page() {
  return <LandingPageClient />
}
