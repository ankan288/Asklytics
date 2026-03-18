"use client";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer,
} from "recharts";
import type { ChartSpec } from "@/lib/types";

const COLORS = ["#6366f1", "#22d3ee", "#f59e0b", "#10b981", "#ef4444", "#8b5cf6", "#f97316"];

export function BarChartWidget({ spec }: { spec: ChartSpec }) {
  const colors = spec.color_palette.length ? spec.color_palette : COLORS;
  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={spec.data} margin={{ top: 5, right: 20, left: 0, bottom: 35 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
        <XAxis
          dataKey={spec.x_key}
          tick={{ fill: "#94a3b8", fontSize: 11 }}
          angle={-30}
          textAnchor="end"
          interval={0}
        />
        <YAxis
          tick={{ fill: "#94a3b8", fontSize: 11 }}
          tickFormatter={(v) =>
            typeof v === "number" && v >= 1000 ? `${(v / 1000).toFixed(0)}k` : v
          }
        />
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
          <Bar
            key={key}
            dataKey={key}
            fill={colors[i % colors.length]}
            radius={[4, 4, 0, 0]}
            maxBarSize={50}
          />
        ))}
      </BarChart>
    </ResponsiveContainer>
  );
}
