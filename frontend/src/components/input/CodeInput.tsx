import { useState } from 'react';
import CodeMirror from '@uiw/react-codemirror';
import { python } from '@codemirror/lang-python';
import { java } from '@codemirror/lang-java';
import { Play, Loader2 } from 'lucide-react';
import type { PipelineStatus } from '../../lib/types';

const SAMPLE_CODE = `# Example: Buggy Python function
def calculate_average(numbers):
    """Calculate the average of a list of numbers."""
    total = 0
    for num in numbers:
        total += num
    # Bug: doesn't handle empty list (division by zero)
    return total / len(numbers)

def merge_dicts(dict1, dict2):
    """Merge two dictionaries, preferring dict2 values."""
    result = dict1.copy()
    # Bug: should use dict2.items() to override
    for key, value in dict1.items():
        result[key] = value
    return result`;

interface CodeInputProps {
  onAnalyze: (code: string, language: string, description: string) => void;
  status: PipelineStatus;
}

export function CodeInput({ onAnalyze, status }: CodeInputProps) {
  const [code, setCode] = useState(SAMPLE_CODE);
  const [language, setLanguage] = useState('python');
  const [description, setDescription] = useState('');
  const isRunning = status === 'connecting' || status === 'streaming';

  return (
    <section id="analyze" className="mx-auto max-w-6xl px-6 py-16">
      <div className="mb-8 text-center">
        <h2 className="text-3xl font-bold text-white">
          Analyze Your Code
        </h2>
        <p className="mt-2 text-gray-400">
          Paste code with potential bugs and let ASQA's agents do the rest
        </p>
      </div>

      <div className="overflow-hidden rounded-2xl border border-gray-700 bg-gray-900 shadow-xl shadow-black/20">
        {/* Toolbar */}
        <div className="flex items-center justify-between border-b border-gray-700 px-4 py-3">
          <div className="flex items-center gap-3">
            <div className="flex gap-1.5">
              <div className="h-3 w-3 rounded-full bg-red-500/80" />
              <div className="h-3 w-3 rounded-full bg-yellow-500/80" />
              <div className="h-3 w-3 rounded-full bg-green-500/80" />
            </div>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="rounded-md border border-gray-600 bg-gray-800 px-3 py-1 text-sm text-gray-300"
            >
              <option value="python">Python</option>
              <option value="java">Java</option>
            </select>
          </div>
          <span className="text-xs text-gray-500">
            {code.split('\n').length} lines
          </span>
        </div>

        {/* Editor */}
        <CodeMirror
          value={code}
          onChange={setCode}
          extensions={[language === 'python' ? python() : java()]}
          theme="dark"
          minHeight="300px"
          maxHeight="500px"
          className="text-sm"
        />

        {/* Description + Button */}
        <div className="flex items-end gap-4 border-t border-gray-700 p-4">
          <div className="flex-1">
            <label className="mb-1 block text-xs font-medium text-gray-400">
              Bug Description (optional)
            </label>
            <input
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe the suspected bug..."
              className="w-full rounded-lg border border-gray-600 bg-gray-800 px-4 py-2.5 text-sm text-gray-200 outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 placeholder:text-gray-500"
            />
          </div>
          <button
            onClick={() => onAnalyze(code, language, description)}
            disabled={isRunning || !code.trim()}
            className="inline-flex items-center gap-2 rounded-lg bg-primary px-6 py-2.5 text-sm font-semibold text-white shadow-md transition hover:bg-primary-hover disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isRunning ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Play className="h-4 w-4" />
                Run Analysis
              </>
            )}
          </button>
        </div>
      </div>
    </section>
  );
}
