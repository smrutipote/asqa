import clsx from 'clsx';

interface Props {
  output?: string;
  exitCode?: number;
  error?: string;
  passed?: boolean;
}

export function TerminalView({ output, exitCode, error, passed }: Props) {
  return (
    <div className="space-y-3">
      {/* Status badges */}
      <div className="flex items-center gap-3">
        <span className={clsx(
          'rounded-md px-2 py-0.5 text-xs font-semibold',
          passed ? 'bg-green-50 text-green-600 dark:bg-green-950 dark:text-green-400' : 'bg-red-50 text-red-600 dark:bg-red-950 dark:text-red-400'
        )}>
          {passed ? 'PASSED' : 'FAILED'}
        </span>
        {exitCode !== undefined && (
          <span className="rounded-md bg-gray-100 px-2 py-0.5 text-xs font-mono text-gray-600 dark:bg-gray-800 dark:text-gray-400">
            exit code: {exitCode}
          </span>
        )}
      </div>

      {/* Terminal output */}
      <div className="overflow-auto rounded-lg bg-[#1a1b26] p-4 font-mono text-xs leading-relaxed text-gray-300" style={{ maxHeight: '300px' }}>
        <pre className="whitespace-pre-wrap">
          {output || 'No output captured'}
        </pre>
      </div>

      {/* Execution error */}
      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-3 dark:border-red-900 dark:bg-red-950">
          <p className="text-xs font-semibold text-red-600 dark:text-red-400">Execution Error:</p>
          <pre className="mt-1 whitespace-pre-wrap font-mono text-xs text-red-600 dark:text-red-400">{error}</pre>
        </div>
      )}
    </div>
  );
}
