import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Privacy Policy",
  description: "Learn how Asklytics collects, safeguards, and processes your business data, CSV datasets, and analytical queries in compliance with GDPR and CCPA.",
  openGraph: {
    title: "Privacy Policy | Asklytics",
    description: "Learn how Asklytics collects, safeguards, and processes your business data, CSV datasets, and analytical queries in compliance with GDPR and CCPA.",
  },
};

export default function PrivacyLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}

