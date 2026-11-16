import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Cookie Policy",
  description: "Learn about the essential cookies, local storage tokens, session identifiers, and user consent choices used across Asklytics.",
  openGraph: {
    title: "Cookie Policy | Asklytics",
    description: "Learn about the essential cookies, local storage tokens, session identifiers, and user consent choices used across Asklytics.",
  },
};

export default function CookiesLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}

