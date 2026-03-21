"use client";
import {
  ScatterChart, Scatter, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer,
} from "recharts";
import type { ChartSpec } from "@/lib/types";

const COLORS = ["#6366f1", "#22d3ee", "#f59e0b", "#10b981", "#ef4444", "#8b5cf6", "#f97316"];

const fmtY = (v: unknown) =>
  typeof v === "number"
    ? v >= 1_000_000 ? `${(v / 1_000_000).toFixed(1)}M`
    : v >= 1000 ? `${(v / 1000).toFixed(0)}k`
    : String(v)
  : String(v);

export function ScatterChartWidget({ spec }: { spec: ChartSpec }) {
  const colors = spec.color_palette?.length ? spec.color_palette : COLORS;
  
  // Automatically identify the first Y key
  const yKey = spec.y_keys.length > 0 ? spec.y_keys[0] : "";
  
  // Safely parse values to numbers (e.g. "15%" -> 15, "$1,000" -> 1000)
  const parseNum = (val: unknown) => {
    if (typeof val === "number") return val;
    if (typeof val === "string") {
      const clean = val.replace(/[^0-9.-]/g, '');
      const n = parseFloat(clean);
      return isNaN(n) ? 0 : n;
    }
    return 0;
  };

  const chartData = spec.data.map(d => ({
    ...d,
    [spec.x_key!]: parseNum(d[spec.x_key!]),
    [yKey]: parseNum(d[yKey])
  }));

  return (
    <ResponsiveContainer width="100%" height={260}>
      <ScatterChart margin={{ top: 10, right: 20, left: 0, bottom: 25 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
        <XAxis
          dataKey={spec.x_key}
          type="number"
          name={spec.x_key}
          tick={{ fill: "#94a3b8", fontSize: 11 }}
          tickFormatter={fmtY}
          domain={['auto', 'auto']}
        />
        <YAxis 
          dataKey={yKey} 
          type="number" 
          name={yKey}
          tick={{ fill: "#94a3b8", fontSize: 11 }} 
          tickFormatter={fmtY} 
          domain={['auto', 'auto']}
        />
        <Tooltip
          cursor={{ strokeDasharray: "3 3", stroke: "#475569" }}
          contentStyle={{
            backgroundColor: "#1e293b",
            border: "1px solid #334155",
            borderRadius: 8,
            color: "#f1f5f9",
            fontSize: 12,
          }}
        />
        <Scatter name={spec.title} data={chartData} fill={colors[0]} />
      </ScatterChart>
    </ResponsiveContainer>
  );
}
