import clsx from 'clsx';

interface Props {
  patch?: string;
  explanation?: string;
}

export function DiffView({ patch, explanation }: Props) {
  if (!patch && !explanation) return <p className="text-sm text-gray-500">No fix suggested</p>;

  const lines = (patch || '').split('\n');

  return (
    <div className="space-y-4">
      {explanation && (
        <div className="rounded-lg bg-blue-950/50 p-4">
          <p className="text-xs font-semibold text-blue-400">Fix Explanation</p>
          <p className="mt-1 text-sm leading-relaxed text-blue-300">{explanation}</p>
        </div>
      )}

      {patch && (
        <div className="overflow-auto rounded-lg bg-[#1a1b26] p-4 font-mono text-xs leading-relaxed" style={{ maxHeight: '400px' }}>
          {lines.map((line, i) => (
            <div
              key={i}
              className={clsx(
                'px-2',
                line.startsWith('+') && !line.startsWith('+++') && 'bg-green-900/30 text-green-400',
                line.startsWith('-') && !line.startsWith('---') && 'bg-red-900/30 text-red-400',
                line.startsWith('@@') && 'text-blue-400',
                line.startsWith('---') && 'text-red-300',
                line.startsWith('+++') && 'text-green-300',
                !line.startsWith('+') && !line.startsWith('-') && !line.startsWith('@@') && 'text-gray-400',
              )}
            >
              {line || '\u00A0'}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
