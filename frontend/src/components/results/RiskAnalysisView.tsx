import type { RiskAnalysis } from '../../lib/types';
import clsx from 'clsx';

interface Props {
  analysis?: RiskAnalysis;
}

function riskColor(score: number): string {
  if (score >= 0.7) return 'bg-red-500';
  if (score >= 0.4) return 'bg-amber-500';
  return 'bg-green-500';
}

function riskBadge(score: number): string {
  if (score >= 0.7) return 'text-red-400 bg-red-950';
  if (score >= 0.4) return 'text-amber-400 bg-amber-950';
  return 'text-green-400 bg-green-950';
}

export function RiskAnalysisView({ analysis }: Props) {
  if (!analysis) return <p className="text-sm text-gray-500">No analysis available</p>;

  return (
    <div className="space-y-4">
      <p className="text-sm text-gray-400">{analysis.summary}</p>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-800 text-left">
              <th className="pb-2 font-medium text-gray-500">Method</th>
              <th className="pb-2 font-medium text-gray-500">File</th>
              <th className="pb-2 font-medium text-gray-500">Risk</th>
              <th className="pb-2 font-medium text-gray-500">Reason</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800">
            {analysis.risky_methods.map((m, i) => (
              <tr key={i}>
                <td className="py-2.5 font-mono text-xs text-gray-200">{m.name}</td>
                <td className="py-2.5 font-mono text-xs text-gray-500">{m.file}</td>
                <td className="py-2.5">
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-16 overflow-hidden rounded-full bg-gray-800">
                      <div className={clsx('h-full rounded-full transition-all', riskColor(m.risk_score))} style={{ width: `${m.risk_score * 100}%` }} />
                    </div>
                    <span className={clsx('rounded-md px-1.5 py-0.5 text-xs font-semibold', riskBadge(m.risk_score))}>
                      {(m.risk_score * 100).toFixed(0)}%
                    </span>
                  </div>
                </td>
                <td className="py-2.5 text-xs text-gray-400">{m.reason}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
