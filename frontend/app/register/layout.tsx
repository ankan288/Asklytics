import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Create Account",
  description: "Create an Asklytics account to turn your business questions into verified SQL queries and visual dashboards.",
  openGraph: {
    title: "Create Account | Asklytics",
    description: "Create an Asklytics account to turn your business questions into verified SQL queries and visual dashboards.",
  },
};

export default function RegisterLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}

