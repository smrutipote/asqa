import { motion } from 'framer-motion';
import { FileSearch, TestTube2, Play, Bug, Wrench, Check, X, Loader2, RotateCcw, ArrowRight } from 'lucide-react';
import { AGENT_IDS, AGENT_META } from '../../lib/types';
import type { AgentState, AgentId, AgentStatus } from '../../lib/types';
import clsx from 'clsx';

const AGENT_ICONS: Record<AgentId, any> = {
  code_reader: FileSearch,
  test_generator: TestTube2,
  runner: Play,
  bug_reporter: Bug,
  fix_suggester: Wrench,
};

const STATUS_STYLES: Record<AgentStatus, { ring: string; bg: string; text: string }> = {
  idle: { ring: 'border-gray-700', bg: 'bg-gray-800', text: 'text-gray-500' },
  running: { ring: 'border-primary', bg: 'bg-primary/10', text: 'text-primary' },
  completed: { ring: 'border-success', bg: 'bg-success/10', text: 'text-success' },
  error: { ring: 'border-error', bg: 'bg-error/10', text: 'text-error' },
  retrying: { ring: 'border-warning', bg: 'bg-warning/10', text: 'text-warning' },
};

function StatusIcon({ status }: { status: AgentStatus }) {
  switch (status) {
    case 'running':
      return <Loader2 className="h-4 w-4 animate-spin text-primary" />;
    case 'completed':
      return <Check className="h-4 w-4 text-success" />;
    case 'error':
      return <X className="h-4 w-4 text-error" />;
    case 'retrying':
      return <RotateCcw className="h-4 w-4 animate-spin-slow text-warning" />;
    default:
      return null;
  }
}

interface PipelineFlowProps {
  agents: Record<string, AgentState>;
}

export function PipelineFlow({ agents }: PipelineFlowProps) {
  return (
    <section className="mx-auto max-w-6xl px-6 py-12">
      <h3 className="mb-8 text-center text-sm font-semibold uppercase tracking-wider text-gray-500">
        Pipeline Status
      </h3>

      <div className="hidden items-center justify-center gap-2 md:flex">
        {AGENT_IDS.map((id, i) => {
          const agent = agents[id];
          const Icon = AGENT_ICONS[id];
          const meta = AGENT_META[id];
          const styles = STATUS_STYLES[agent?.status || 'idle'];

          return (
            <div key={id} className="flex items-center gap-2">
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: i * 0.08 }}
                className="relative flex flex-col items-center"
              >
                {agent?.status === 'running' && (
                  <div className="absolute inset-0 flex items-start justify-center pt-1">
                    <div className="h-12 w-12 rounded-full border-2 border-primary animate-pulse-ring" />
                  </div>
                )}

                <div className={clsx(
                  'relative flex h-14 w-14 items-center justify-center rounded-2xl border-2 transition-all duration-300',
                  styles.ring, styles.bg,
                )}>
                  <Icon className={clsx('h-6 w-6', styles.text)} />
                  {agent?.status && agent.status !== 'idle' && (
                    <div className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-gray-900 shadow-sm">
                      <StatusIcon status={agent.status} />
                    </div>
                  )}
                </div>

                <div className="mt-2 text-center">
                  <p className="text-xs font-semibold text-gray-300">{meta.name}</p>
                  <p className="text-[10px] text-gray-500">{meta.model}</p>
                </div>

                {agent?.status === 'running' && agent.message && (
                  <motion.p
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="mt-1 max-w-[120px] text-center text-[10px] text-primary"
                  >
                    {agent.message.split('...')[0]}...
                  </motion.p>
                )}
              </motion.div>

              {i < AGENT_IDS.length - 1 && (
                <ArrowRight className="h-4 w-4 flex-shrink-0 text-gray-600" />
              )}
            </div>
          );
        })}
      </div>

      {/* Mobile: vertical */}
      <div className="flex flex-col items-center gap-4 md:hidden">
        {AGENT_IDS.map((id, i) => {
          const agent = agents[id];
          const Icon = AGENT_ICONS[id];
          const meta = AGENT_META[id];
          const styles = STATUS_STYLES[agent?.status || 'idle'];

          return (
            <motion.div
              key={id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.08 }}
              className="flex items-center gap-3"
            >
              <div className={clsx(
                'relative flex h-10 w-10 items-center justify-center rounded-xl border-2 transition-all',
                styles.ring, styles.bg,
              )}>
                <Icon className={clsx('h-5 w-5', styles.text)} />
              </div>
              <div>
                <p className="text-sm font-semibold text-gray-300">{meta.name}</p>
                <p className="text-xs text-gray-500">{meta.model}</p>
              </div>
            </motion.div>
          );
        })}
      </div>
    </section>
  );
}
