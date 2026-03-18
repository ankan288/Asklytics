"use client";
import { useState, useRef, type KeyboardEvent } from "react";
import { Paperclip, CornerDownLeft } from "lucide-react";
import { LoadingSpinner } from "../ui/LoadingSpinner";

interface Props {
  onSend: (prompt: string) => void;
  onUploadClick: () => void;
  isLoading: boolean;
  disabled?: boolean;
}

export function ChatInput({ onSend, onUploadClick, isLoading, disabled }: Props) {
  const [value, setValue] = useState("");
  const ref = useRef<HTMLTextAreaElement>(null);

  const send = () => {
    const t = value.trim();
    if (!t || isLoading) return;
    onSend(t);
    setValue("");
    if (ref.current) ref.current.style.height = "auto";
  };

  const onKey = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); }
  };

  const onInput = () => {
    if (!ref.current) return;
    ref.current.style.height = "auto";
    ref.current.style.height = Math.min(ref.current.scrollHeight, 120) + "px";
  };

  return (
    <div className="p-3">
      {/* Input card */}
      <div className="bg-slate-900 border border-slate-700 rounded-2xl px-3 pt-2.5 pb-2 space-y-1.5 focus-within:border-slate-600 transition-colors">
        <textarea
          ref={ref}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={onKey}
          onInput={onInput}
          placeholder="Type your message here..."
          rows={1}
          disabled={isLoading || disabled}
          className="w-full bg-transparent text-white text-sm placeholder-slate-500 resize-none outline-none min-h-[28px] max-h-[100px] leading-relaxed disabled:opacity-50"
        />

        {/* Toolbar */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-0.5">
            <button
              onClick={onUploadClick}
              disabled={isLoading}
              title="Attach CSV"
              className="p-1.5 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition-colors disabled:opacity-50"
            >
              <Paperclip size={16} />
            </button>
          </div>

          <button
            onClick={send}
            disabled={!value.trim() || isLoading || disabled}
            className="flex items-center justify-center bg-white hover:bg-slate-100 disabled:opacity-40 disabled:cursor-not-allowed text-slate-900 rounded-xl p-2 transition-colors"
          >
            {isLoading ? (
              <LoadingSpinner size={14} />
            ) : (
              <CornerDownLeft size={13} />
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
