import { BarChartWidget } from "./BarChartWidget";
import { LineChartWidget } from "./LineChartWidget";
import { PieChartWidget } from "./PieChartWidget";
import { AreaChartWidget } from "./AreaChartWidget";
import { KPICard } from "./KPICard";
import { BarChart2 } from "lucide-react";
import type { ChartSpec } from "@/lib/types";

const WIDGETS = {
  bar: BarChartWidget,
  line: LineChartWidget,
  pie: PieChartWidget,
  area: AreaChartWidget,
  kpi: KPICard,
} as const;

// Decode HTML entities like &amp; -> &
function decodeHtmlEntities(str: string): string {
  if (typeof str !== "string") return str;
  return str
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&nbsp;/g, " ");
}

// Recursively decode HTML entities in data
function decodeDataEntities(data: Record<string, unknown>[]): Record<string, unknown>[] {
  return data.map((row) => {
    const decoded: Record<string, unknown> = {};
    for (const [key, value] of Object.entries(row)) {
      decoded[key] = typeof value === "string" ? decodeHtmlEntities(value) : value;
    }
    return decoded;
  });
}

export function ChartCard({ spec }: { spec: ChartSpec }) {
  const Widget = WIDGETS[spec.type as keyof typeof WIDGETS] ?? BarChartWidget;

  // Empty data guard
  if (!spec.data || spec.data.length === 0) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
        <h3 className="text-slate-300 font-medium text-sm mb-4 leading-snug">{spec.title}</h3>
        <div className="flex flex-col items-center justify-center h-52 text-slate-600 gap-2">
          <BarChart2 size={28} />
          <p className="text-sm">No data returned for this query.</p>
        </div>
      </div>
    );
  }

  // Decode HTML entities in data (e.g., &amp; -> &)
  const decodedData = decodeDataEntities(spec.data);
  const decodedSpec = { ...spec, data: decodedData };

  // Validate x_key / y_keys exist in the actual SQL result rows (skip for KPI)
  if (spec.type !== "kpi") {
    const resultKeys = Object.keys(decodedData[0]);
    const xInvalid = spec.x_key && !resultKeys.includes(spec.x_key);
    const invalidY = spec.y_keys.filter((k) => !resultKeys.includes(k));
    if (xInvalid || invalidY.length > 0) {
      return (
        <div className="bg-slate-900 border border-red-900/50 rounded-xl p-5">
          <h3 className="text-slate-300 font-medium text-sm mb-4 leading-snug">{spec.title}</h3>
          <div className="flex flex-col items-center justify-center h-52 text-red-400 gap-2 text-center px-4">
            <p className="text-sm font-medium">Column mismatch</p>
            <p className="text-xs text-red-500">
              AI referenced columns that don&apos;t exist in the results. Try rephrasing your query.
            </p>
          </div>
        </div>
      );
    }
  }

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition-colors">
      <h3 className="text-slate-300 font-medium text-sm mb-4 leading-snug">
        {decodeHtmlEntities(spec.title)}
      </h3>
      <Widget spec={decodedSpec} />
    </div>
  );
}
