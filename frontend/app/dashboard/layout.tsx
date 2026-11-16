import type { Metadata } from "next";
import { AuthGuard } from "@/components/AuthGuard";

export const metadata: Metadata = {
  title: "Analytics Dashboard",
  description: "Explore your business data with natural language queries, verifiable AST-guarded SQL, and interactive real-time visual charts.",
  openGraph: {
    title: "Analytics Dashboard | Asklytics",
    description: "Explore your business data with natural language queries, verifiable AST-guarded SQL, and interactive real-time visual charts.",
  },
};

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <AuthGuard>{children}</AuthGuard>;
}
