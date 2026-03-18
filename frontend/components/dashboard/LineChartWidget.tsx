"use client";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, Brush,
} from "recharts";
import type { ChartSpec } from "@/lib/types";

const COLORS = ["#6366f1", "#22d3ee", "#f59e0b", "#10b981", "#ef4444", "#8b5cf6", "#f97316"];

const fmtY = (v: unknown) =>
  typeof v === "number"
    ? v >= 1_000_000 ? `${(v / 1_000_000).toFixed(1)}M`
    : v >= 1000 ? `${(v / 1000).toFixed(0)}k`
    : String(v)
  : String(v);

export function LineChartWidget({ spec }: { spec: ChartSpec }) {
  const colors = spec.color_palette.length ? spec.color_palette : COLORS;
  const showBrush = spec.data.length > 12;
  const startIndex = Math.max(0, spec.data.length - 12);
  return (
    <ResponsiveContainer width="100%" height={showBrush ? 290 : 260}>
      <LineChart data={spec.data} margin={{ top: 5, right: 20, left: 0, bottom: showBrush ? 5 : 35 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
        <XAxis
          dataKey={spec.x_key}
          tick={{ fill: "#94a3b8", fontSize: 11 }}
          angle={-30}
          textAnchor="end"
          interval="preserveStartEnd"
        />
        <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} tickFormatter={fmtY} />
        <Tooltip
          contentStyle={{
            backgroundColor: "#1e293b",
            border: "1px solid #334155",
            borderRadius: 8,
            color: "#f1f5f9",
            fontSize: 12,
          }}
        />
        {spec.y_keys.length > 1 && (
          <Legend wrapperStyle={{ color: "#94a3b8", fontSize: 12 }} />
        )}
        {spec.y_keys.map((key, i) => (
          <Line
            key={key}
            type="monotone"
            dataKey={key}
            stroke={colors[i % colors.length]}
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 5 }}
          />
        ))}
        {showBrush && (
          <Brush
            dataKey={spec.x_key}
            height={20}
            stroke="#334155"
            fill="#0f172a"
            travellerWidth={6}
            startIndex={startIndex}
          />
        )}
      </LineChart>
    </ResponsiveContainer>
  );
}
