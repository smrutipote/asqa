import { useState, useCallback } from 'react';
import { streamAnalysis } from '../lib/api';
import { AGENT_IDS } from '../lib/types';
import type { AgentState, PipelineStatus } from '../lib/types';

const initialAgents: Record<string, AgentState> = Object.fromEntries(
  AGENT_IDS.map((id) => [id, { status: 'idle' as const }]),
);

export function useAnalysis() {
  const [pipelineStatus, setPipelineStatus] = useState<PipelineStatus>('idle');
  const [agents, setAgents] = useState<Record<string, AgentState>>(initialAgents);
  const [pipelineSummary, setPipelineSummary] = useState<any>(null);

  const updateAgent = useCallback((id: string, update: Partial<AgentState>) => {
    setAgents((prev) => ({
      ...prev,
      [id]: { ...prev[id], ...update },
    }));
  }, []);

  const analyze = useCallback(
    async (code: string, language: string, description: string) => {
      setPipelineStatus('connecting');
      setAgents(initialAgents);
      setPipelineSummary(null);

      try {
        setPipelineStatus('streaming');

        for await (const event of streamAnalysis(code, language, description)) {
          if (event.agent === 'pipeline') {
            setPipelineSummary(event.data);
            setPipelineStatus('done');
            continue;
          }

          const status = event.status as AgentState['status'];

          if (status === 'running' || status === 'retrying') {
            updateAgent(event.agent, { status, message: event.message });
          } else if (status === 'completed') {
            updateAgent(event.agent, { status: 'completed', data: event.data });
          } else if (status === 'error') {
            updateAgent(event.agent, { status: 'error', message: event.message });
          }
        }

        setPipelineStatus((prev) => (prev === 'done' ? 'done' : 'done'));
      } catch (err: any) {
        setPipelineStatus('error');
        console.error('Pipeline error:', err);
      }
    },
    [updateAgent],
  );

  const reset = useCallback(() => {
    setPipelineStatus('idle');
    setAgents(initialAgents);
    setPipelineSummary(null);
  }, []);

  return { pipelineStatus, agents, pipelineSummary, analyze, reset };
}
