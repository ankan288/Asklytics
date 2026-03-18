import type { ChartSpec } from "@/lib/types";

function formatNumber(raw: unknown): string {
  const n = Number(raw);
  if (isNaN(n)) return String(raw ?? "—");
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(2)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toLocaleString(undefined, { maximumFractionDigits: 2 });
}

export function KPICard({ spec }: { spec: ChartSpec }) {
  const row = spec.data[0] ?? {};
  const raw = row["value"] ?? row[spec.y_keys[0]] ?? 0;

  return (
    <div className="flex flex-col items-center justify-center h-full min-h-[180px] text-center gap-3">
      <p className="text-slate-400 text-sm">{spec.title}</p>
      <p className="text-5xl font-bold tracking-tight text-indigo-400">
        {formatNumber(raw)}
      </p>
    </div>
  );
}
