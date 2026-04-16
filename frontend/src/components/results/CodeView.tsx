import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Copy, Check } from 'lucide-react';
import { useState } from 'react';

interface Props {
  code?: string;
  filename?: string;
}

export function CodeView({ code, filename }: Props) {
  const [copied, setCopied] = useState(false);

  if (!code) return <p className="text-sm text-gray-400">No test generated</p>;

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-2">
      {filename && (
        <div className="flex items-center justify-between">
          <span className="font-mono text-xs text-gray-500">{filename}</span>
          <button
            onClick={handleCopy}
            className="inline-flex items-center gap-1 rounded-md px-2 py-1 text-xs text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800"
          >
            {copied ? <Check className="h-3 w-3 text-success" /> : <Copy className="h-3 w-3" />}
            {copied ? 'Copied' : 'Copy'}
          </button>
        </div>
      )}
      <div className="overflow-hidden rounded-lg">
        <SyntaxHighlighter
          language="python"
          style={oneDark}
          showLineNumbers
          customStyle={{ margin: 0, borderRadius: '0.5rem', fontSize: '0.8rem', maxHeight: '400px' }}
        >
          {code}
        </SyntaxHighlighter>
      </div>
    </div>
  );
}
