import { useState, type ReactNode } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, Loader2, Check, X, RotateCcw } from 'lucide-react';
import type { AgentStatus } from '../../lib/types';
import clsx from 'clsx';

const STATUS_CONFIG: Record<AgentStatus, { label: string; color: string; icon: any }> = {
  idle: { label: 'Idle', color: 'bg-gray-800 text-gray-500', icon: null },
  running: { label: 'Running', color: 'bg-blue-950 text-blue-400', icon: Loader2 },
  completed: { label: 'Done', color: 'bg-green-950 text-green-400', icon: Check },
  error: { label: 'Error', color: 'bg-red-950 text-red-400', icon: X },
  retrying: { label: 'Retrying', color: 'bg-amber-950 text-amber-400', icon: RotateCcw },
};

interface AgentCardProps {
  name: string;
  model: string;
  status: AgentStatus;
  message?: string;
  defaultOpen?: boolean;
  children: ReactNode;
}

export function AgentCard({ name, model, status, message, defaultOpen = false, children }: AgentCardProps) {
  const [open, setOpen] = useState(defaultOpen);
  const config = STATUS_CONFIG[status];
  const StatusIcon = config.icon;

  return (
    <div className="overflow-hidden rounded-xl border border-gray-800 bg-gray-900 shadow-sm transition-shadow hover:shadow-md">
      <button
        onClick={() => setOpen(!open)}
        className="flex w-full items-center justify-between px-5 py-4 text-left"
      >
        <div className="flex items-center gap-3">
          <h4 className="font-semibold text-white">{name}</h4>
          <span className="rounded-md bg-gray-800 px-2 py-0.5 text-xs font-mono text-gray-400">
            {model}
          </span>
          <span className={clsx('inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium', config.color)}>
            {StatusIcon && (
              <StatusIcon className={clsx('h-3 w-3', status === 'running' && 'animate-spin', status === 'retrying' && 'animate-spin-slow')} />
            )}
            {config.label}
          </span>
        </div>
        <ChevronDown className={clsx('h-5 w-5 text-gray-500 transition-transform', open && 'rotate-180')} />
      </button>

      {status === 'running' && message && (
        <div className="border-t border-gray-800 px-5 py-3">
          <p className="text-sm italic text-primary">{message}</p>
        </div>
      )}

      <AnimatePresence initial={false}>
        {open && status === 'completed' && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="overflow-hidden"
          >
            <div className="border-t border-gray-800 px-5 py-4">
              {children}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Agent errors are hidden from the user */}
    </div>
  );
}
