import type { AgentEvent } from './types';

const API_URL = import.meta.env.VITE_API_URL || '';

export async function* streamAnalysis(
  code: string,
  language: string,
  description: string,
): AsyncGenerator<AgentEvent> {
  const response = await fetch(`${API_URL}/api/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ code, language, description }),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  const reader = response.body?.getReader();
  if (!reader) throw new Error('No response body');

  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const event: AgentEvent = JSON.parse(line.slice(6));
          yield event;
        } catch {
          // skip malformed lines
        }
      }
    }
  }
}
