import { Header } from './components/layout/Header';
import { HeroSection } from './components/hero/HeroSection';
import { CodeInput } from './components/input/CodeInput';
import { PipelineFlow } from './components/pipeline/PipelineFlow';
import { ResultsSection } from './components/results/ResultsSection';
import { useAnalysis } from './hooks/useAnalysis';

function App() {
  const { pipelineStatus, agents, pipelineSummary, analyze } = useAnalysis();

  return (
    <div className="min-h-screen bg-[#0a0a0f]">
      <Header />
      <HeroSection />
      <CodeInput onAnalyze={analyze} status={pipelineStatus} />

      {pipelineStatus !== 'idle' && (
        <>
          <PipelineFlow agents={agents} />
          <ResultsSection
            agents={agents}
            pipelineStatus={pipelineStatus}
            pipelineSummary={pipelineSummary}
          />
        </>
      )}

      <footer className="border-t border-gray-800 py-8 text-center text-sm text-gray-500">
        <p>ASQA — Autonomous Software Quality Assurance</p>
        <p className="mt-1">NCI MSc AI, Machine Learning Project</p>
      </footer>
    </div>
  );
}

export default App;
