export function LoadingSpinner({ size = 24 }: { size?: number }) {
  return (
    <div
      className="animate-spin rounded-full border-2 border-slate-600 border-t-indigo-500"
      style={{ width: size, height: size }}
    />
  );
}

export function DashboardSkeleton() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 animate-pulse">
      {[1, 2, 3, 4].map((i) => (
        <div key={i} className="bg-slate-800 rounded-xl p-6 h-72">
          <div className="h-4 bg-slate-700 rounded w-1/3 mb-4" />
          <div className="h-52 bg-slate-700 rounded" />
        </div>
      ))}
    </div>
  );
}
