"use client";
import React, { useMemo, useState } from "react";
import type { ChartSpec } from "@/lib/types";

export function HeatMapChartWidget({ spec }: { spec: ChartSpec }) {
  const { data, x_key, y_keys, z_key } = spec;
  const yKey = y_keys?.[0]; // Usually heatmap compares X and Y categories
  const zKey = z_key || y_keys?.[1]; // If AI forgot z_key, fallback to second y_key

  const [hoveredCell, setHoveredCell] = useState<{ x: string; y: string; z: number } | null>(null);

  const { xVals, yVals, cellMap, maxZ } = useMemo(() => {
    if (!x_key || !yKey || !zKey || data.length === 0) {
      return { xVals: [], yVals: [], cellMap: new Map(), maxZ: 0 };
    }

    const xSet = new Set<string>();
    const ySet = new Set<string>();
    const map = new Map<string, number>();
    let maximum = 0;

    data.forEach((row) => {
      const x = String(row[x_key] || "N/A");
      const y = String(row[yKey] || "N/A");
      const z = Number(row[zKey]) || 0;

      xSet.add(x);
      ySet.add(y);
      map.set(`${x}-${y}`, z);

      if (z > maximum) maximum = z;
    });

    return {
      xVals: Array.from(xSet).sort(),
      yVals: Array.from(ySet).sort(),
      cellMap: map,
      maxZ: maximum,
    };
  }, [data, x_key, yKey, zKey]);

  if (xVals.length === 0 || yVals.length === 0) {
    return <div className="text-slate-500 text-sm p-4">Invalid heatmap data structure.</div>;
  }

  // Base highlight color
  const baseColor = spec.color_palette?.[0] || "#6366f1"; 

  // Simple formatter
  const fmt = (v: number) => 
    v >= 1000000 ? `${(v/1000000).toFixed(1)}M` : v >= 1000 ? `${(v/1000).toFixed(1)}k` : v.toLocaleString();

  return (
    <div className="relative w-full h-[260px] overflow-auto select-none rounded-lg border border-slate-800/60 bg-slate-900/50 p-2 scrollbar-thin scrollbar-thumb-slate-700">
      <div className="min-w-fit pb-4 pr-4">
        <div className="flex mb-2 items-end min-h-[40px]">
          {/* Top-left corner gap */}
          <div className="w-32 shrink-0 p-1" />
          {/* X axis labels */}
          <div className="flex gap-1">
            {xVals.map((x) => (
              <div key={x} className="w-14 sm:w-20 shrink-0 text-center text-xs text-slate-400 truncate px-1 pb-1" title={x}>
                {x}
              </div>
            ))}
          </div>
        </div>

        {/* Heatmap Grid rows */}
        <div className="space-y-1">
          {yVals.map((y) => (
            <div key={y} className="flex gap-1">
              {/* Y axis label */}
              <div className="w-32 shrink-0 text-right text-xs text-slate-400 pr-3 my-auto truncate" title={y}>
                {y}
              </div>
              
              {/* Row cells */}
              <div className="flex gap-1">
                {xVals.map((x) => {
                  const z = cellMap.get(`${x}-${y}`) || 0;
                  const intensity = maxZ > 0 ? Math.max(0.1, z / maxZ) : 0.1; // minimum 0.1 for visibility
                  
                  return (
                    <div
                      key={`${x}-${y}`}
                      onMouseEnter={() => setHoveredCell({ x, y, z })}
                      onMouseLeave={() => setHoveredCell(null)}
                      className="w-14 sm:w-20 shrink-0 h-8 rounded-sm transition-all duration-200 cursor-pointer hover:ring-2 hover:ring-white"
                      style={{
                        backgroundColor: baseColor,
                        opacity: intensity,
                      }}
                    />
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Tooltip */}
      {hoveredCell && (
        <div className="absolute top-2 right-2 bg-slate-800 border border-slate-700 text-slate-200 rounded-lg p-3 shadow-xl z-10 pointer-events-none fade-in">
          <p className="text-xs text-slate-400 mb-1">{x_key}: <span className="text-white">{hoveredCell.x}</span></p>
          <p className="text-xs text-slate-400 mb-1">{yKey}: <span className="text-white">{hoveredCell.y}</span></p>
          <p className="text-xs font-semibold text-indigo-300 mt-2">{zKey}: {fmt(hoveredCell.z)}</p>
        </div>
      )}
    </div>
  );
}
