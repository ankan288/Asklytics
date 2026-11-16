import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Components Showcase",
  description: "Interactive component showcase, animations, and design system demo for Asklytics.",
  openGraph: {
    title: "Components Showcase | Asklytics",
    description: "Interactive component showcase, animations, and design system demo for Asklytics.",
  },
};

export default function ComponentsDemoLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}

