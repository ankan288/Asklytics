import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Sign In",
  description: "Sign in to your Asklytics account to access your conversational analytics dashboards and datasets.",
  openGraph: {
    title: "Sign In | Asklytics",
    description: "Sign in to your Asklytics account to access your conversational analytics dashboards and datasets.",
  },
};

export default function LoginLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}

