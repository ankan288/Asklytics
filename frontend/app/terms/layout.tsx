import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Terms and Conditions",
  description: "Terms of service, acceptable use guidelines, AI generation disclaimers, copyright policies, and governing laws for Asklytics.",
  openGraph: {
    title: "Terms and Conditions | Asklytics",
    description: "Terms of service, acceptable use guidelines, AI generation disclaimers, copyright policies, and governing laws for Asklytics.",
  },
};

export default function TermsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}

