import type { BugReport } from '../../lib/types';
import clsx from 'clsx';

interface Props {
  report?: BugReport;
  finalStatus?: string;
}

const SEVERITY_STYLES: Record<string, string> = {
  critical: 'bg-red-950 text-red-400',
  high: 'bg-orange-950 text-orange-400',
  medium: 'bg-amber-950 text-amber-400',
  low: 'bg-blue-950 text-blue-400',
};

export function BugReportView({ report, finalStatus }: Props) {
  if (!report) return <p className="text-sm text-gray-500">No report available</p>;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-3">
        <span className={clsx(
          'rounded-full px-3 py-1 text-xs font-bold',
          report.is_real_bug ? 'bg-red-950 text-red-400' : 'bg-green-950 text-green-400'
        )}>
          {report.is_real_bug ? 'BUG CONFIRMED' : 'NO BUG'}
        </span>
        <span className={clsx('rounded-full px-3 py-1 text-xs font-bold', SEVERITY_STYLES[report.severity] || SEVERITY_STYLES.medium)}>
          {report.severity.toUpperCase()}
        </span>
        {finalStatus && (
          <span className="rounded-full bg-gray-800 px-3 py-1 text-xs font-medium text-gray-400">
            {finalStatus}
          </span>
        )}
      </div>

      <div>
        <div className="mb-1 flex items-center justify-between">
          <span className="text-xs font-medium text-gray-500">Confidence</span>
          <span className="text-xs font-bold text-gray-300">{(report.confidence * 100).toFixed(0)}%</span>
        </div>
        <div className="h-2 w-full overflow-hidden rounded-full bg-gray-800">
          <div className="h-full rounded-full bg-primary transition-all" style={{ width: `${report.confidence * 100}%` }} />
        </div>
      </div>

      <div>
        <label className="text-xs font-medium text-gray-500">Affected Method</label>
        <p className="mt-0.5 font-mono text-sm text-gray-200">{report.affected_method}</p>
      </div>

      <div>
        <label className="text-xs font-medium text-gray-500">Root Cause Hypothesis</label>
        <p className="mt-1 text-sm leading-relaxed text-gray-300">{report.root_cause_hypothesis}</p>
      </div>

      {report.reproduction_steps?.length > 0 && (
        <div>
          <label className="text-xs font-medium text-gray-500">Reproduction Steps</label>
          <ol className="mt-1 list-inside list-decimal space-y-1 text-sm text-gray-300">
            {report.reproduction_steps.map((step, i) => (
              <li key={i}>{step}</li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
}
