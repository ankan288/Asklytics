import { User, Bot, AlertTriangle } from "lucide-react";
import type { ChatMessage } from "@/lib/types";
import { ClarificationChips } from "./ClarificationChips";

export function ChatBubble({
  message,
  onSelectOption,
}: {
  message: ChatMessage;
  onSelectOption?: (refinedPrompt: string) => void;
}) {
  const isUser = message.role === "user";
  return (
    <div className={`flex gap-2.5 ${isUser ? "flex-row-reverse" : ""}`}>
      <div
        className={`shrink-0 w-7 h-7 rounded-full flex items-center justify-center ${
          isUser ? "bg-indigo-600" : "bg-slate-700"
        }`}
      >
        {isUser ? <User size={14} /> : <Bot size={14} />}
      </div>
      <div className="max-w-[82%] flex flex-col gap-1.5">
        <div
          className={`rounded-2xl px-3.5 py-2.5 text-sm leading-relaxed ${
            isUser
              ? "bg-indigo-600 text-white rounded-tr-sm"
              : "bg-slate-800 text-slate-200 rounded-tl-sm"
          }`}
        >
          {message.content}
        </div>
        {message.clarification && onSelectOption && (
          <ClarificationChips
            clarification={message.clarification}
            onSelectOption={onSelectOption}
          />
        )}
        {message.warning && (
          <div className="flex items-start gap-1.5 bg-amber-950/60 border border-amber-700/40 rounded-xl px-3 py-2 text-xs text-amber-300 leading-snug">
            <AlertTriangle size={12} className="shrink-0 mt-0.5 text-amber-400" />
            <span>{message.warning}</span>
          </div>
        )}
      </div>
    </div>
  );
}
