import type { Metadata } from "next";
import { AuthGuard } from "@/components/AuthGuard";

export const metadata: Metadata = {
  title: "Admin Dashboard",
  description: "Administrative control center, system telemetry, user management, and security monitors for Asklytics.",
  openGraph: {
    title: "Admin Dashboard | Asklytics",
    description: "Administrative control center, system telemetry, user management, and security monitors for Asklytics.",
  },
};

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <AuthGuard>{children}</AuthGuard>;
}
