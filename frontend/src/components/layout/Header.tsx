import { Shield } from 'lucide-react';

export function Header() {
  return (
    <header className="sticky top-0 z-50 border-b border-gray-800 bg-[#0a0a0f]/80 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
        <div className="flex items-center gap-2">
          <Shield className="h-7 w-7 text-primary" />
          <span className="text-xl font-bold tracking-tight text-white">
            ASQA
          </span>
        </div>
        <nav className="flex items-center gap-6">
          <a href="#analyze" className="text-sm font-medium text-gray-400 hover:text-white transition">
            Analyze
          </a>
          <span className="text-xs font-medium text-gray-500">NCI MSc AI</span>
        </nav>
      </div>
    </header>
  );
}
