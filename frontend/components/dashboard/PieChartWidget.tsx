"use client";
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from "recharts";
import type { ChartSpec } from "@/lib/types";

const COLORS = ["#6366f1", "#22d3ee", "#f59e0b", "#10b981", "#ef4444", "#8b5cf6", "#f97316"];

export function PieChartWidget({ spec }: { spec: ChartSpec }) {
  const colors = spec.color_palette.length ? spec.color_palette : COLORS;
  const valueKey = spec.y_keys[0] || "value";
  const labelKey = spec.x_key || "name";

  return (
    <ResponsiveContainer width="100%" height={260}>
      <PieChart>
        <Pie
          data={spec.data}
          dataKey={valueKey}
          nameKey={labelKey}
          cx="50%"
          cy="50%"
          outerRadius={90}
          innerRadius={42}
          paddingAngle={2}
          label={({ name, percent }: { name: string; percent: number }) =>
            `${name} ${(percent * 100).toFixed(0)}%`
          }
          labelLine={{ stroke: "#475569" }}
        >
          {spec.data.map((_, i) => (
            <Cell key={i} fill={colors[i % colors.length]} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{
            backgroundColor: "#1e293b",
            border: "1px solid #334155",
            borderRadius: 8,
            color: "#f1f5f9",
            fontSize: 12,
          }}
          formatter={(v: unknown) =>
            typeof v === "number" ? v.toLocaleString() : String(v)
          }
        />
        <Legend wrapperStyle={{ color: "#94a3b8", fontSize: 12 }} />
      </PieChart>
    </ResponsiveContainer>
  );
}
