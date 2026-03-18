'use client';
import React, { useState, useEffect, createContext, useContext, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CircleCheck, AlertCircle, AlertTriangle, Info } from 'lucide-react';

type ToastType = 'success' | 'error' | 'warning' | 'info';
type ToastPosition = 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right' | 'center';

interface Toast {
  id: number;
  message: string;
  type: ToastType;
}

interface ToastContextType {
  showToast: (message: string, type?: ToastType, position?: ToastPosition) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<{ toast: Toast; position: ToastPosition }[]>([]);
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => { setIsMounted(true); }, []);

  const showToast = useCallback((
    message: string,
    type: ToastType = 'info',
    position: ToastPosition = 'bottom-right',
  ) => {
    const id = Date.now();
    setToasts(prev => [...prev, { toast: { id, message, type }, position }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(({ toast }) => toast.id !== id));
    }, 4000);
  }, []);

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      {isMounted && (['top-left', 'top-right', 'bottom-left', 'bottom-right', 'center'] as ToastPosition[]).map((pos) => (
        <ToastContainer
          key={pos}
          toasts={toasts.filter(t => t.position === pos)}
          position={pos}
        />
      ))}
    </ToastContext.Provider>
  );
};

export const useToast = () => {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used within ToastProvider');
  return ctx;
};

const POSITION_CLASSES: Record<string, string> = {
  'top-left':     'top-4 left-4 items-start',
  'top-right':    'top-4 right-4 items-end',
  'bottom-left':  'bottom-4 left-4 items-start',
  'bottom-right': 'bottom-4 right-4 items-end',
  'center':       'top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 items-center',
};

const ToastContainer: React.FC<{ toasts: { toast: Toast; position: ToastPosition }[]; position: ToastPosition }> = ({ toasts, position }) => (
  <div className={`fixed z-[9999] flex flex-col gap-2 pointer-events-none ${POSITION_CLASSES[position] ?? POSITION_CLASSES['bottom-right']}`}>
    <AnimatePresence>
      {toasts.map(({ toast }) => (
        <motion.div
          key={toast.id}
          initial={{ opacity: 0, y: position.startsWith('bottom') ? 16 : -16, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: position.startsWith('bottom') ? 16 : -16, scale: 0.95 }}
          transition={{ duration: 0.3, ease: 'easeOut' }}
          className="pointer-events-auto"
        >
          <ToastItem {...toast} />
        </motion.div>
      ))}
    </AnimatePresence>
  </div>
);

const TYPE_STYLES = {
  success: { icon: CircleCheck, bg: 'bg-slate-900', border: 'border-green-800/60', icon_color: 'text-green-400', text: 'text-green-200' },
  error:   { icon: AlertCircle, bg: 'bg-slate-900', border: 'border-red-800/60',   icon_color: 'text-red-400',   text: 'text-red-200'   },
  warning: { icon: AlertTriangle, bg: 'bg-slate-900', border: 'border-yellow-800/60', icon_color: 'text-yellow-400', text: 'text-yellow-200' },
  info:    { icon: Info,         bg: 'bg-slate-900', border: 'border-indigo-800/60', icon_color: 'text-indigo-400', text: 'text-slate-200' },
};

const ToastItem: React.FC<Toast> = ({ message, type }) => {
  const { icon: Icon, bg, border, icon_color, text } = TYPE_STYLES[type];
  return (
    <div className={`${bg} ${border} border rounded-xl shadow-2xl px-4 py-3 flex items-center gap-3 min-w-[260px] max-w-sm`}>
      <Icon className={`${icon_color} shrink-0`} size={18} />
      <p className={`${text} text-sm font-medium`}>{message}</p>
    </div>
  );
};
