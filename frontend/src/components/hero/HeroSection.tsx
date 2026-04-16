import { motion } from 'framer-motion';
import { ArrowDown, Bot, FileSearch, TestTube2, Bug, Wrench } from 'lucide-react';

export function HeroSection() {
  return (
    <section className="relative overflow-hidden bg-gradient-to-b from-gray-950 to-[#0a0a0f] py-24">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(67,83,255,0.08),transparent_50%)]" />
      <div className="relative mx-auto max-w-4xl px-6 text-center">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7 }}
        >
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-4 py-1.5 text-sm font-medium text-primary">
            <Bot className="h-4 w-4" />
            5-Agent LLM Pipeline
          </div>

          <h1 className="text-5xl font-bold leading-tight tracking-tight text-white sm:text-6xl lg:text-7xl">
            Autonomous Software{' '}
            <span className="bg-gradient-to-r from-primary to-blue-400 bg-clip-text text-transparent">
              Quality Assurance
            </span>
          </h1>

          <p className="mx-auto mt-6 max-w-2xl text-lg text-gray-400">
            Paste your code. ASQA's five specialised AI agents will analyze it,
            generate tests, execute them, report bugs, and suggest fixes — all in real time.
          </p>

          <div className="mt-8 flex items-center justify-center gap-8 text-sm text-gray-500">
            {[
              { icon: FileSearch, label: 'Analyze' },
              { icon: TestTube2, label: 'Test' },
              { icon: Bug, label: 'Report' },
              { icon: Wrench, label: 'Fix' },
            ].map(({ icon: Icon, label }) => (
              <div key={label} className="flex items-center gap-1.5">
                <Icon className="h-4 w-4" />
                <span>{label}</span>
              </div>
            ))}
          </div>

          <motion.a
            href="#analyze"
            className="mt-10 inline-flex items-center gap-2 rounded-lg bg-primary px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-primary/25 transition hover:bg-primary-hover hover:shadow-xl hover:shadow-primary/30"
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.97 }}
          >
            Start Analyzing
            <ArrowDown className="h-4 w-4" />
          </motion.a>
        </motion.div>
      </div>
    </section>
  );
}
