# ASQA — Autonomous Software QA Agent

A five-agent LLM pipeline that autonomously detects bugs, generates tests, and suggests fixes for software changes.

## Quick Start

### Installation

1. Clone the repository
2. Copy `.env.example` to `.env` and fill in your API keys:
   ```bash
   cp .env.example .env
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Pipeline

```bash
python run_pipeline.py
```

This will:
1. Load bug records from `data/processed/*.jsonl`
2. Execute the 5-agent pipeline on each bug
3. Save results to `evaluation/results/pipeline_outputs.jsonl`

## Architecture

For a complete system architecture, data flow, and detailed documentation, see [ARCHITECTURE.md](ARCHITECTURE.md).

## Project Structure

```
asqa/
├── data/             # Raw and processed bug datasets
├── pipeline/         # Core 5-agent LangGraph pipeline
├── baselines/        # Single-agent baseline systems
├── evaluation/       # KPI calculation and statistical tests
├── notebooks/        # Jupyter notebooks for analysis
└── tests/            # Unit tests
```

## Key Files

- **[ARCHITECTURE.md](ARCHITECTURE.md)** — Complete system design, data contracts, and flow
- **pipeline/state.py** — ASQAState dataclass (shared memory across agents)
- **pipeline/graph.py** — LangGraph orchestration (state machine)
- **pipeline/agents/** — Five independent agents (Code Reader, Test Generator, Runner, Bug Reporter, Fix Suggester)
- **evaluation/kpi_calculator.py** — Computes 5 KPIs from results

## Datasets

- **BugsInPy** — Python bugs in open-source projects
- **Defects4J** — Java bugs with ground truth
- **SWE-bench Verified** — GitHub issues from HuggingFace

## Environment Variables

See `.env` file for configuration options.

## Citation

If you use ASQA in your research, please cite:

```bibtex
@misc{asqa2024,
  title={ASQA: Autonomous Software QA Agent},
  author={...},
  year={2024}
}
```

## License

MIT
