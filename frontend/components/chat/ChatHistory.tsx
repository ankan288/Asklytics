"use client";
import { useEffect, useRef } from "react";
import { Bot } from "lucide-react";
import { ChatBubble } from "./ChatBubble";
import type { ChatMessage } from "@/lib/types";

interface Props {
  messages: ChatMessage[];
  isLoading: boolean;
  onSelectOption?: (prompt: string) => void;
}

export function ChatHistory({ messages, isLoading, onSelectOption }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  if (messages.length === 0) {
    return <div className="flex-1" />;
  }

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-3">
      {messages.map((m) => (
        <ChatBubble key={m.id} message={m} onSelectOption={onSelectOption} />
      ))}
      {isLoading && (
        <div className="flex gap-2.5">
          <div className="shrink-0 w-7 h-7 rounded-full bg-slate-700 flex items-center justify-center">
            <Bot size={14} className="text-slate-400" />
          </div>
          <div className="bg-slate-800 rounded-2xl rounded-tl-sm px-4 py-3 flex gap-1.5 items-center">
            <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce [animation-delay:-0.3s]" />
            <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce [animation-delay:-0.15s]" />
            <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" />
          </div>
        </div>
      )}
      <div ref={bottomRef} />
    </div>
  );
}
