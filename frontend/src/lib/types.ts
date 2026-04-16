export interface RiskMethod {
  name: string;
  file: string;
  risk_score: number;
  reason: string;
}

export interface RiskAnalysis {
  risky_methods: RiskMethod[];
  summary: string;
  language: string;
}

export interface BugReport {
  is_real_bug: boolean;
  severity: 'critical' | 'high' | 'medium' | 'low';
  affected_method: string;
  root_cause_hypothesis: string;
  reproduction_steps: string[];
  confidence: number;
}

export type AgentStatus = 'idle' | 'running' | 'completed' | 'error' | 'retrying';

export interface AgentEvent {
  agent: string;
  status: AgentStatus;
  data?: any;
  message?: string;
  retry_count?: number;
}

export interface AgentState {
  status: AgentStatus;
  data?: any;
  message?: string;
}

export type PipelineStatus = 'idle' | 'connecting' | 'streaming' | 'done' | 'error';

export const AGENT_IDS = ['code_reader', 'test_generator', 'runner', 'bug_reporter', 'fix_suggester'] as const;
export type AgentId = typeof AGENT_IDS[number];

export const AGENT_META: Record<AgentId, { name: string; description: string; model: string }> = {
  code_reader: { name: 'Code Reader', description: 'Analyzes diff and identifies risky methods', model: 'GPT-4.1-mini' },
  test_generator: { name: 'Test Generator', description: 'Generates executable test to expose bug', model: 'Claude Sonnet 4' },
  runner: { name: 'Runner', description: 'Executes test and classifies result', model: 'GPT-4.1-mini' },
  bug_reporter: { name: 'Bug Reporter', description: 'Synthesizes structured bug report', model: 'GPT-4.1-mini' },
  fix_suggester: { name: 'Fix Suggester', description: 'Root cause analysis and fix patch', model: 'Claude Sonnet 4' },
};
