import { AlertCircle, X } from "lucide-react";

interface Props {
  message: string;
  onDismiss?: () => void;
}

export function ErrorBanner({ message, onDismiss }: Props) {
  return (
    <div className="flex items-start gap-3 bg-red-950/50 border border-red-800/60 text-red-300 rounded-xl p-4">
      <AlertCircle className="shrink-0 mt-0.5" size={18} />
      <p className="text-sm flex-1 leading-relaxed">{message}</p>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="shrink-0 hover:text-red-100 transition-colors"
        >
          <X size={16} />
        </button>
      )}
    </div>
  );
}
