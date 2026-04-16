# ASQA — Autonomous Software QA Agent
## Complete System Architecture & Data Flow

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Repository Structure](#2-repository-structure)
3. [Data Layer — Where Input Comes From](#3-data-layer--where-input-comes-from)
4. [Data Ingestion Pipeline](#4-data-ingestion-pipeline)
5. [LangGraph State Object — The Shared Memory](#5-langgraph-state-object--the-shared-memory)
6. [Agent 1 — Code Reader](#6-agent-1--code-reader)
7. [Agent 2 — Test Generator](#7-agent-2--test-generator)
8. [Agent 3 — Runner](#8-agent-3--runner)
9. [Agent 4 — Bug Reporter](#9-agent-4--bug-reporter)
10. [Agent 5 — Fix Suggester](#10-agent-5--fix-suggester)
11. [LangGraph Orchestration — The State Machine](#11-langgraph-orchestration--the-state-machine)
12. [LangSmith Observability Layer](#12-langsmith-observability-layer)
13. [Baseline Systems](#13-baseline-systems)
14. [KPI Collection & Evaluation](#14-kpi-collection--evaluation)
15. [Complete End-to-End Flow (Numbered Step by Step)](#15-complete-end-to-end-flow-numbered-step-by-step)
16. [Environment Variables & Configuration](#16-environment-variables--configuration)
17. [Key Data Contracts (Input/Output Schemas)](#17-key-data-contracts-inputoutput-schemas)
18. [Error Handling & Edge Cases](#18-error-handling--edge-cases)
19. [How Each File Talks to the Others](#19-how-each-file-talks-to-the-others)

---

## 1. System Overview

ASQA is a **five-agent LLM pipeline** that takes a software bug (as a code diff + metadata) as input and autonomously:

1. Reads and understands the code change
2. Writes an executable test that should expose the bug
3. Runs that test in an isolated Docker sandbox
4. Reports the bug in a structured format
5. Suggests a patch to fix the root cause

The pipeline is **orchestrated by LangGraph** (a directed state machine), **observed by LangSmith** (full trace logging), and **evaluated against three public benchmarks**: Defects4J (Java), BugsInPy (Python), SWE-bench Verified (Python/multi-language).

### Agent-to-Model Assignment

| Agent | Model | Why |
|---|---|---|
| Code Reader | GPT-4o | 128k context window handles large diffs; best code reasoning benchmarks |
| Test Generator | Claude Sonnet | Best long-form code generation; thinks before writing (less cosmetic fixes) |
| Runner | GPT-4o-mini | Only does routing/classification; 15× cheaper than GPT-4o; no deep reasoning needed |
| Bug Reporter | GPT-4o | Needs to reason about whether a failure is a real bug; structured JSON output |
| Fix Suggester | Claude Sonnet | Root cause analysis before patch generation; long reasoning chain |

---

## 2. Repository Structure

```
asqa/
│
├── .env                          # API keys — NEVER commit this
├── requirements.txt              # Pinned package versions
├── README.md
├── ARCHITECTURE.md               # This file
│
├── data/
│   ├── loaders/
│   │   ├── bugsinpy_loader.py    # Loads BugsInPy bugs into standard format
│   │   ├── defects4j_loader.py   # Loads Defects4J bugs into standard format
│   │   └── swebench_loader.py    # Loads SWE-bench Verified from HuggingFace
│   ├── raw/
│   │   ├── bugsinpy/             # BugsInPy repo cloned here
│   │   └── defects4j/            # Defects4J checkout here
│   └── processed/
│       ├── bugsinpy_bugs.jsonl   # Standardised bug records (one per line)
│       ├── defects4j_bugs.jsonl
│       └── swebench_bugs.jsonl
│
├── pipeline/
│   ├── state.py                  # ASQAState dataclass — the shared memory object
│   ├── graph.py                  # LangGraph graph definition — nodes + edges
│   ├── agents/
│   │   ├── code_reader.py        # Agent 1
│   │   ├── test_generator.py     # Agent 2
│   │   ├── runner.py             # Agent 3
│   │   ├── bug_reporter.py       # Agent 4
│   │   └── fix_suggester.py      # Agent 5
│   └── docker/
│       ├── sandbox.py            # Docker container management
│       └── Dockerfile.sandbox    # The test execution image
│
├── baselines/
│   ├── single_agent_gpt4o.py     # Baseline 1: single GPT-4o prompt
│   └── single_agent_claude.py    # Baseline 2: single Claude Sonnet prompt
│
├── evaluation/
│   ├── kpi_calculator.py         # Computes all 5 KPIs from LangSmith traces
│   ├── statistical_tests.py      # McNemar test, Wilcoxon signed-rank test
│   └── results/                  # Output CSVs and charts saved here
│
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_results_analysis.ipynb
│   └── 03_ablation_study.ipynb
│
└── tests/
    └── test_agents.py            # Unit tests for each agent in isolation
```

---

## 3. Data Layer — Where Input Comes From

### What is a "bug record"?

All three benchmarks are normalised into a single **standard bug record** format (a Python dataclass / dict) before any agent sees it. This is critical — agents never talk directly to raw benchmark files.

```python
# The standard bug record — every benchmark loader produces this
{
    "bug_id":           "bugsinpy_pandas_1",   # unique ID across all datasets
    "source":           "bugsinpy",            # "bugsinpy" | "defects4j" | "swebench"
    "language":         "python",              # "python" | "java"
    "repo_name":        "pandas",
    "repo_path":        "/data/raw/bugsinpy/pandas",   # absolute path on disk
    "buggy_commit":     "a3f91bc",             # git SHA of the broken version
    "fixed_commit":     "d72e041",             # git SHA of the working version
    "diff":             "--- a/pandas/...\n+++ b/pandas/...\n...",  # raw unified diff string
    "changed_files":    ["pandas/core/frame.py"],
    "bug_description":  "DataFrame.merge fails when...",
    "failing_test":     "pytest pandas/tests/test_frame.py::test_merge",  # ground truth
    "split":            "test"                 # "train" | "dev" | "test"
}
```

### Dataset 1 — BugsInPy

- **What it is**: A collection of real bugs in Python projects (pandas, numpy, scrapy, etc.)
- **Where to get it**: `git clone https://github.com/soarsmu/BugsInPy data/raw/bugsinpy`
- **Structure on disk**: Each bug lives in `data/raw/bugsinpy/projects/<project>/bugs/<bug_id>/`
  - `bug.info` — contains `buggy_commit_id` and `fixed_commit_id`
  - `run_test.sh` — the command that reproduces the failing test
- **How the loader works** (`bugsinpy_loader.py`):
  1. Walk the directory tree to find every `bug.info`
  2. Read `buggy_commit_id` and `fixed_commit_id`
  3. `git diff <buggy_commit>..<fixed_commit>` to generate the diff string
  4. Read `run_test.sh` to extract the failing test command
  5. Produce a standard bug record dict
  6. Write to `data/processed/bugsinpy_bugs.jsonl` (one JSON per line)

### Dataset 2 — Defects4J

- **What it is**: 835 real, reproducible bugs in 17 Java open-source projects
- **Where to get it**: Follow official install at `https://github.com/rjust/defects4j`
- **Setup**: Requires Java 8 + Perl. Run `./init.sh` then `defects4j checkout -p Lang -v 1b -w /tmp/Lang_1_buggy`
- **How the loader works** (`defects4j_loader.py`):
  1. Use `defects4j query -p <project> -q "bug.id"` to list all bug IDs
  2. For each bug: `defects4j diff` to get the patch diff, `defects4j export -p tests.trigger` to get the failing test name
  3. Checkout the buggy version to a temp directory
  4. Produce a standard bug record dict
  5. Write to `data/processed/defects4j_bugs.jsonl`

### Dataset 3 — SWE-bench Verified

- **What it is**: 500 human-verified GitHub issues with diffs and natural language descriptions
- **Where to get it**: HuggingFace datasets — one line: `load_dataset("princeton-nlp/SWE-bench_Verified")`
- **How the loader works** (`swebench_loader.py`):
  1. Call `load_dataset(...)` — returns a HuggingFace Dataset object
  2. Each row already has: `instance_id`, `repo`, `base_commit`, `patch` (the diff), `problem_statement`, `test_patch`
  3. Map columns to the standard bug record format
  4. Write to `data/processed/swebench_bugs.jsonl`

### Train / Dev / Test Split

| Dataset | Train | Dev | Test |
|---|---|---|---|
| BugsInPy | First 60% by bug_id | Next 20% | Last 20% |
| Defects4J | First 584 bugs | — | Last 251 bugs |
| SWE-bench | Not used for training | 100 bugs | 400 bugs |

**Rule**: The pipeline is never run on train or dev bugs during final evaluation. Prompt tuning and threshold calibration use only train/dev splits.

---

## 4. Data Ingestion Pipeline

Before the agents run, you need to load and prepare bugs. This is a one-time preprocessing step, separate from the agent pipeline.

```
run_preprocessing.py
    │
    ├── bugsinpy_loader.py  →  data/processed/bugsinpy_bugs.jsonl
    ├── defects4j_loader.py →  data/processed/defects4j_bugs.jsonl
    └── swebench_loader.py  →  data/processed/swebench_bugs.jsonl
                                      │
                                      ▼
                          run_pipeline.py reads from .jsonl files
                          one bug_record at a time, feeds into graph.py
```

`run_pipeline.py` is the entry point for the agent pipeline. It:
1. Reads `.jsonl` files line by line
2. Filters to the `"test"` split
3. For each bug record, constructs the initial `ASQAState`
4. Calls `graph.invoke(initial_state)` — this triggers the full LangGraph pipeline
5. Collects the returned final state
6. Appends the result to `evaluation/results/pipeline_outputs.jsonl`

---

## 5. LangGraph State Object — The Shared Memory

The `ASQAState` is **the most important data structure in the entire system**. It is the object that flows through every node in the LangGraph. Every agent reads from it and writes to it. Think of it as a baton that gets passed around.

```python
# pipeline/state.py

from dataclasses import dataclass, field
from typing import Optional, List

@dataclass
class ASQAState:
    # ── INPUT (set once by run_pipeline.py, never changed) ──────────────────
    bug_id:          str = ""
    source:          str = ""          # "bugsinpy" | "defects4j" | "swebench"
    language:        str = ""          # "python" | "java"
    repo_path:       str = ""          # absolute path to repo on disk
    buggy_commit:    str = ""
    fixed_commit:    str = ""
    diff:            str = ""          # raw unified diff — the main input
    bug_description: str = ""
    failing_test:    str = ""          # ground truth (used only for evaluation)

    # ── AGENT 1 OUTPUT (Code Reader) ─────────────────────────────────────────
    risk_analysis:   Optional[dict] = None
    # {
    #   "risky_methods": [{"name": str, "file": str, "risk_score": float, "reason": str}],
    #   "summary": str,
    #   "language": str
    # }

    # ── AGENT 2 OUTPUT (Test Generator) ──────────────────────────────────────
    generated_test:  Optional[str] = None    # full Python/Java test file as string
    test_filename:   Optional[str] = None    # e.g. "test_asqa_generated.py"
    retry_count:     int = 0                 # how many times we've retried generation

    # ── AGENT 3 OUTPUT (Runner) ───────────────────────────────────────────────
    test_passed:     Optional[bool] = None
    test_output:     Optional[str] = None    # full stdout + stderr from test run
    test_exit_code:  Optional[int] = None    # 0 = pass, non-zero = fail
    execution_error: Optional[str] = None   # syntax errors, import errors, etc.

    # ── AGENT 4 OUTPUT (Bug Reporter) ─────────────────────────────────────────
    bug_report:      Optional[dict] = None
    # {
    #   "is_real_bug": bool,
    #   "severity": "critical" | "high" | "medium" | "low",
    #   "affected_method": str,
    #   "root_cause_hypothesis": str,
    #   "reproduction_steps": [str],
    #   "confidence": float   (0.0 – 1.0)
    # }

    # ── AGENT 5 OUTPUT (Fix Suggester) ────────────────────────────────────────
    fix_patch:       Optional[str] = None    # unified diff patch string
    fix_explanation: Optional[str] = None   # plain English reasoning

    # ── PIPELINE METADATA (set automatically during runs) ────────────────────
    pipeline_start_time:  Optional[float] = None   # time.time() at pipeline start
    pipeline_end_time:    Optional[float] = None
    total_cost_usd:       Optional[float] = None   # computed from LangSmith tokens
    langsmith_run_id:     Optional[str] = None
    error_message:        Optional[str] = None     # set if pipeline crashed
    final_status: str = "pending"  # "pending"|"bug_found"|"no_bug"|"failed"
```

---

## 6. Agent 1 — Code Reader

**File**: `pipeline/agents/code_reader.py`
**Model**: GPT-4o
**Input from state**: `state.diff`, `state.bug_description`, `state.language`
**Output to state**: `state.risk_analysis`

### What it does

The Code Reader is the **entry point of intelligence** in the pipeline. It reads the raw git diff and produces a structured JSON that tells later agents where to focus their attention.

### System Prompt (what to give GPT-4o)

```
You are a senior software engineer specialising in code review and bug detection.

You will be given a git diff for a pull request. Your job is to:
1. Identify every method/function that was changed or is at risk due to nearby changes
2. Assign each a risk score from 0.0 (no risk) to 1.0 (almost certainly buggy)
3. Explain why each method is risky in one sentence
4. Write a two-sentence summary of the overall change

Return ONLY valid JSON matching this exact schema. No preamble, no markdown code fences.

{
  "risky_methods": [
    {
      "name": "<method name>",
      "file": "<file path>",
      "risk_score": <float 0.0-1.0>,
      "reason": "<one sentence>"
    }
  ],
  "summary": "<two sentences about the overall change>",
  "language": "<python or java>"
}
```

### User Message

```
Language: {state.language}
Bug description (if available): {state.bug_description}

Git diff:
{state.diff}
```

### What happens with the output

1. GPT-4o returns a JSON string
2. The agent parses it with `json.loads()`
3. If parsing fails (malformed JSON), retry once with a correction prompt
4. Sort `risky_methods` by `risk_score` descending — highest risk first
5. Store the parsed dict in `state.risk_analysis`
6. LangGraph moves to Agent 2

### Why GPT-4o specifically here

The diff can be thousands of lines. GPT-4o's 128,000 token context window ensures even the largest PR diffs won't be truncated. GPT-4o consistently ranks highest on HumanEval and SWE-bench for code comprehension tasks.

---

## 7. Agent 2 — Test Generator

**File**: `pipeline/agents/test_generator.py`
**Model**: Claude Sonnet (claude-sonnet-4-5 or latest)
**Input from state**: `state.risk_analysis`, `state.diff`, `state.language`, `state.retry_count`, `state.execution_error`
**Output to state**: `state.generated_test`, `state.test_filename`

### What it does

Takes the risk analysis from Agent 1 and writes a **complete, runnable test file** targeting the risky methods. The test is designed so that it will FAIL on the buggy version and PASS on the fixed version — this is the definition of a useful bug-exposing test.

### System Prompt (what to give Claude Sonnet)

```
You are an expert software test engineer. You write precise, executable tests
that expose real bugs rather than testing trivial cases.

Rules you must always follow:
- Write a COMPLETE, self-contained test file. Include all necessary imports.
- Tests must be runnable with `pytest` (Python) or `mvn test` (Java) with no modification.
- Target the high-risk methods identified in the risk analysis.
- Each test function must have a meaningful assertion — not just `assert True`.
- Do NOT use mocking unless absolutely necessary.
- Do NOT write tests that always pass — the point is to expose a bug.
- For Python: use pytest conventions (functions named test_*, no TestCase class needed)
- For Java: use JUnit 4 or JUnit 5 conventions

Return ONLY the raw test file content. No explanation, no markdown code fences.
```

### User Message (with retry context)

On **first attempt** (`retry_count == 0`):
```
Language: {state.language}

Risk analysis from code reader:
{json.dumps(state.risk_analysis, indent=2)}

Relevant diff:
{state.diff}

Write a test file that will expose the bug described in this diff.
```

On **retry** (`retry_count >= 1`, triggered by Runner failure):
```
Your previous test attempt failed with this error:

{state.execution_error}

Previous test code:
{state.generated_test}

Fix the test so it compiles and runs successfully. Keep the same test logic
but fix the import/syntax/runtime error shown above.
```

### What happens with the output

1. Claude returns the raw test file as a string
2. Save the string to `state.generated_test`
3. Determine filename: `test_asqa_{bug_id}.py` (Python) or `TestASQA{BugId}.java` (Java)
4. Save filename to `state.test_filename`
5. LangGraph moves to Agent 3 (Runner)

### Why Claude Sonnet specifically here

Claude Sonnet is consistently stronger than GPT-4o at generating long-form, syntactically correct code files. Critically, Sonnet's "extended thinking" style (it reasons internally before outputting) reduces cosmetic fixes — tests that look valid but don't actually probe the bug. This was the finding in Liu et al. [2023] that directly motivated this design.

---

## 8. Agent 3 — Runner

**File**: `pipeline/agents/runner.py` + `pipeline/docker/sandbox.py`
**Model**: GPT-4o-mini (for interpreting results) + Docker (for execution)
**Input from state**: `state.generated_test`, `state.test_filename`, `state.repo_path`, `state.buggy_commit`, `state.language`
**Output to state**: `state.test_passed`, `state.test_output`, `state.test_exit_code`, `state.execution_error`

### What it does

This agent has **two sub-components**:
1. A **Docker sandbox** that physically executes the test
2. A **GPT-4o-mini classifier** that reads the output and decides what went wrong

### Sub-component A: Docker Sandbox

```python
# pipeline/docker/sandbox.py

def run_test_in_sandbox(repo_path: str, test_file_content: str,
                        test_filename: str, language: str,
                        buggy_commit: str) -> dict:
    """
    1. Pull/build the sandbox Docker image
    2. Mount the repo at the buggy commit as read-only
    3. Write the test file into the container
    4. Run pytest (Python) or mvn test (Java)
    5. Return stdout, stderr, exit_code
    """
```

**Dockerfile.sandbox** (Python version):
```dockerfile
FROM python:3.11-slim
RUN pip install pytest pytest-cov
WORKDIR /repo
# The repo is mounted at runtime — not baked in
CMD ["pytest", "--tb=short", "-v"]
```

**Execution flow inside sandbox.py**:
```
1. docker.from_env()  — connect to local Docker daemon
2. client.containers.run(
       image="asqa-sandbox:python",
       volumes={repo_path: {"bind": "/repo", "mode": "rw"}},
       command=f"bash -c 'git checkout {buggy_commit} && pytest {test_filename} -v'",
       detach=False,      ← wait for completion
       timeout=120,       ← 2 minutes max per test run
       mem_limit="512m",  ← memory safety limit
       network_disabled=True  ← no internet inside sandbox
   )
3. Capture logs (stdout + stderr combined)
4. Capture exit code
5. Remove the container immediately after
6. Return {"stdout": str, "exit_code": int}
```

### Sub-component B: GPT-4o-mini Result Classifier

After the Docker run, GPT-4o-mini reads the test output and classifies it into one of three categories:

| Category | Meaning | LangGraph action |
|---|---|---|
| `"test_failure"` | Test ran but assertions failed — this is the desired outcome (bug exposed) | → Route to Agent 4 |
| `"execution_error"` | Test couldn't even run (syntax error, import error, missing dependency) | → Route BACK to Agent 2 (retry) |
| `"test_pass"` | Test ran and passed on the buggy version — test is not useful | → Route to Agent 4 (but flagged as low confidence) |

**GPT-4o-mini prompt** for classification:
```
You are classifying the output of a test run.

Test output:
{stdout_and_stderr}

Exit code: {exit_code}

Classify this result as EXACTLY ONE of:
- "test_failure" — the test ran successfully but assertions failed (bug exposed)
- "execution_error" — the test could not run at all (syntax/import/dependency error)
- "test_pass" — the test ran and all assertions passed

Return ONLY the classification string. Nothing else.
```

### Retry Logic (controlled by LangGraph, not this agent)

- If result is `"execution_error"` AND `state.retry_count < 2`: increment `retry_count`, copy stderr to `state.execution_error`, route back to Agent 2
- If result is `"execution_error"` AND `state.retry_count >= 2`: route forward to Agent 4 with `test_passed = False`, `final_status = "failed"`
- If result is `"test_failure"`: route to Agent 4 with `test_passed = False` (good — this means the bug was exposed)
- If result is `"test_pass"`: route to Agent 4 with `test_passed = True` (bad — test didn't find the bug)

---

## 9. Agent 4 — Bug Reporter

**File**: `pipeline/agents/bug_reporter.py`
**Model**: GPT-4o
**Input from state**: `state.diff`, `state.risk_analysis`, `state.test_output`, `state.test_passed`, `state.bug_description`
**Output to state**: `state.bug_report`

### What it does

Synthesises everything seen so far — the original diff, the risk analysis, and the test execution result — into a **structured bug report**. This is the output a real engineering team would use to understand and prioritise the bug.

### System Prompt

```
You are a senior QA engineer writing a formal bug report.

You have access to:
1. The original git diff
2. A risk analysis of the changed code
3. The result of running a test against the buggy version

Your job is to determine:
- Whether this is a genuine bug (not a false positive)
- Its severity
- The most likely root cause
- Clear reproduction steps

Return ONLY valid JSON. No preamble. Schema:

{
  "is_real_bug": <true | false>,
  "severity": "<critical | high | medium | low>",
  "affected_method": "<fully qualified method name>",
  "root_cause_hypothesis": "<one paragraph, be specific>",
  "reproduction_steps": ["<step 1>", "<step 2>", ...],
  "confidence": <float 0.0-1.0>
}
```

### User Message

```
Diff:
{state.diff}

Risk analysis:
{json.dumps(state.risk_analysis, indent=2)}

Test execution result:
- Test passed on buggy version: {state.test_passed}
- Exit code: {state.test_exit_code}
- Output:
{state.test_output}

Bug description (if available):
{state.bug_description}
```

### What happens with the output

1. Parse JSON into a dict
2. Store in `state.bug_report`
3. Set `state.final_status`:
   - If `is_real_bug == True` AND `test_passed == False`: `"bug_found"` ← ideal outcome
   - If `is_real_bug == True` AND `test_passed == True`: `"bug_found_test_weak"` ← bug real but test missed it
   - If `is_real_bug == False`: `"no_bug"` ← false positive
4. LangGraph always moves to Agent 5 next (regardless of is_real_bug)

---

## 10. Agent 5 — Fix Suggester

**File**: `pipeline/agents/fix_suggester.py`
**Model**: Claude Sonnet
**Input from state**: `state.diff`, `state.bug_report`, `state.risk_analysis`, `state.test_output`, `state.language`
**Output to state**: `state.fix_patch`, `state.fix_explanation`

### What it does

This is the final intelligence step. Claude Sonnet performs **root cause analysis** — not just looking at the failing line, but reasoning about *why* it fails — and then produces a unified diff patch that would fix the bug without changing unrelated code.

### System Prompt

```
You are a principal software engineer specialising in debugging and patch generation.

Before writing any code, you MUST:
1. Identify the exact root cause (not just the symptom)
2. Reason about whether a fix at the symptom level or root level is appropriate
3. Consider whether the fix might break other functionality

Then produce:
- A MINIMAL unified diff patch that fixes only the root cause
- A plain-English explanation of your reasoning

Return valid JSON:
{
  "reasoning": "<your step-by-step analysis before writing the patch>",
  "fix_patch": "<unified diff string, starting with --- and +++>",
  "fix_explanation": "<plain English, 2-3 sentences>",
  "confidence": <float 0.0-1.0>
}
```

### User Message

```
Language: {state.language}

Original diff (what was changed that caused the bug):
{state.diff}

Bug report:
{json.dumps(state.bug_report, indent=2)}

Test output that exposed the bug:
{state.test_output}

Produce a minimal patch that fixes this bug.
```

### What happens with the output

1. Parse JSON
2. Store `fix_patch` and `fix_explanation` in state
3. Record `state.pipeline_end_time = time.time()`
4. LangGraph reaches the terminal node — pipeline is complete
5. The final state is returned to `run_pipeline.py`

---

## 11. LangGraph Orchestration — The State Machine

**File**: `pipeline/graph.py`

LangGraph models the pipeline as a directed graph where:
- **Nodes** = agents (Python functions)
- **Edges** = flow from one agent to the next
- **Conditional edges** = the retry loop from Runner back to Test Generator

### Graph Definition

```python
# pipeline/graph.py

from langgraph.graph import StateGraph, END
from pipeline.state import ASQAState
from pipeline.agents.code_reader import code_reader_node
from pipeline.agents.test_generator import test_generator_node
from pipeline.agents.runner import runner_node
from pipeline.agents.bug_reporter import bug_reporter_node
from pipeline.agents.fix_suggester import fix_suggester_node

def build_graph():
    graph = StateGraph(ASQAState)

    # Add all nodes
    graph.add_node("code_reader",    code_reader_node)
    graph.add_node("test_generator", test_generator_node)
    graph.add_node("runner",         runner_node)
    graph.add_node("bug_reporter",   bug_reporter_node)
    graph.add_node("fix_suggester",  fix_suggester_node)

    # Set entry point
    graph.set_entry_point("code_reader")

    # Linear edges
    graph.add_edge("code_reader",    "test_generator")
    graph.add_edge("bug_reporter",   "fix_suggester")
    graph.add_edge("fix_suggester",  END)

    # Conditional edge from runner — retry or continue
    graph.add_conditional_edges(
        "runner",
        decide_after_runner,           # ← the routing function
        {
            "retry":        "test_generator",   # go back to regenerate test
            "continue":     "bug_reporter",     # proceed normally
        }
    )

    return graph.compile()


def decide_after_runner(state: ASQAState) -> str:
    """
    Called by LangGraph after the Runner node.
    Returns "retry" or "continue".
    """
    if state.execution_error and state.retry_count < 2:
        return "retry"
    return "continue"
```

### Visual Flow of the State Machine

```
[START]
   │
   ▼
┌─────────────────┐
│  Code Reader    │  ← GPT-4o reads diff, produces risk_analysis JSON
└─────────────────┘
   │
   ▼
┌─────────────────┐  ◄─────────────────────────────────────────────┐
│  Test Generator │  ← Claude Sonnet writes test file              │
└─────────────────┘                                                 │
   │                                                                │
   ▼                                                                │
┌─────────────────┐                                           (if execution_error
│     Runner      │  ← Docker executes test                   AND retry_count < 2)
└─────────────────┘                                                 │
   │                                                                │
   ├── execution_error + retry_count < 2  ──────────────────────────┘
   │
   ├── execution_error + retry_count >= 2 ──┐
   │                                         │
   └── test_failure OR test_pass ────────────┤
                                             │
                                             ▼
                                    ┌─────────────────┐
                                    │  Bug Reporter   │  ← GPT-4o writes structured report
                                    └─────────────────┘
                                             │
                                             ▼
                                    ┌─────────────────┐
                                    │  Fix Suggester  │  ← Claude Sonnet writes patch
                                    └─────────────────┘
                                             │
                                             ▼
                                          [END]
```

---

## 12. LangSmith Observability Layer

**Every single LLM call is automatically logged** when these environment variables are set:

```
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=<your key>
LANGCHAIN_PROJECT=asqa-experiments
```

You do NOT need to write any special logging code. LangGraph + LangChain automatically send traces to LangSmith.

### What LangSmith records per agent invocation

- Agent name and model name
- Full prompt (system + user messages)
- Full model response
- Input token count
- Output token count
- Latency in milliseconds
- Whether it succeeded or raised an exception
- The `bug_id` you pass as metadata (so you can group runs by bug)

### How to add bug_id to traces

```python
# In run_pipeline.py, wrap each pipeline run with LangSmith metadata
from langsmith import traceable

@traceable(name="asqa_pipeline", metadata={"bug_id": bug_record["bug_id"]})
def run_one_bug(bug_record):
    initial_state = ASQAState(**bug_record)
    final_state = compiled_graph.invoke(initial_state)
    return final_state
```

### How to export data for KPI calculation

After all runs are complete, use the LangSmith Python SDK:

```python
from langsmith import Client

client = Client()
runs = client.list_runs(project_name="asqa-experiments")

# Each run has: .total_tokens, .total_cost, .end_time - .start_time
# Export to a DataFrame for KPI calculation
```

---

## 13. Baseline Systems

**Purpose**: To answer the research question, you must show that ASQA outperforms single-agent alternatives.

### Baseline 1 — Single Agent GPT-4o

**File**: `baselines/single_agent_gpt4o.py`

One GPT-4o call with a mega-prompt containing the full diff and asking for:
1. A test
2. A bug report
3. A fix patch

All in one response. Same input data, same evaluation. Logs to a separate LangSmith project: `asqa-baseline-gpt4o`.

### Baseline 2 — Single Agent Claude Sonnet

**File**: `baselines/single_agent_claude.py`

Same approach but with Claude Sonnet instead of GPT-4o. Logs to `asqa-baseline-claude`.

### What you compare

| Metric | ASQA | GPT-4o Single | Claude Single |
|---|---|---|---|
| Bug Detection Rate | ? | ? | ? |
| False Positive Rate | ? | ? | ? |
| Test Gen Accuracy | ? | ? | ? |
| Cost per PR | ? | ? | ? |
| MTTR (seconds) | ? | ? | ? |

(Fill in after experiments)

---

## 14. KPI Collection & Evaluation

**File**: `evaluation/kpi_calculator.py`

### KPI 1 — Bug Detection Rate (BDR)

```
BDR = (bugs where test_passed == False on buggy version) / (total bugs run)
```

For each bug in your test set, check: did the generated test actually fail on the buggy commit?
- `state.test_exit_code != 0` AND `state.final_status in ["bug_found", "bug_found_test_weak"]` → detected
- Anything else → missed

**Target from proposal**: > 60%

### KPI 2 — False Positive Rate (FPR)

```
FPR = (bug_report.is_real_bug == True, but ground truth says no bug) / total reports
```

Randomly sample 50 bug reports from your runs. You and one other person independently label each as "real bug" or "false positive" by checking the ground truth patch. Compute Cohen's Kappa (must be > 0.7 to be valid).

**Target from proposal**: < 15%

### KPI 3 — Test Generation Accuracy (TGA)

```
TGA = (tests with exit_code != 127 and no SyntaxError in output) / total tests generated
```

A test "compiled and ran" if the Runner did not get an `execution_error` on the very first attempt (before retries).

**Target**: As high as possible; baseline is Yuan et al.'s 68%.

### KPI 4 — Cost per PR Review

```
Cost = Σ(tokens_in × price_per_input_token + tokens_out × price_per_output_token)
       for all 3 models across all 5 agents for one bug
```

Use LangSmith's `run.total_cost` field (it calculates this automatically if you set the model names correctly).

**Target from proposal**: < $0.05 per PR

### KPI 5 — Mean Time to Report (MTTR)

```
MTTR = mean(state.pipeline_end_time - state.pipeline_start_time)
       measured across all test set bugs
```

Includes all retries and Docker execution time.

**Target**: < 120 seconds

### Statistical Tests

**File**: `evaluation/statistical_tests.py`

For BDR and FPR (binary outcomes): **McNemar's test** (paired, two-sided, α = 0.05)
```python
from statsmodels.stats.contingency_tables import mcnemar
# Compare ASQA detected/missed vs GPT-4o single-agent detected/missed
# on the SAME set of bugs — this is why it's "paired"
```

For Cost and MTTR (continuous): **Wilcoxon signed-rank test** (non-parametric, α = 0.05)
```python
from scipy.stats import wilcoxon
# Compare per-bug costs: ASQA vs baseline
```

Report: statistic, p-value, and effect size for every comparison.

---

## 15. Complete End-to-End Flow (Numbered Step by Step)

This section traces the journey of ONE bug from raw dataset to final result.

```
Step 0.  PREPROCESSING (run once, offline)
         bugsinpy_loader.py reads pandas/bugs/1/bug.info
         → extracts buggy_commit = "a3f91bc", fixed_commit = "d72e041"
         → runs: git diff a3f91bc..d72e041 (inside the cloned repo)
         → extracts failing_test from run_test.sh: "pytest pandas/tests/test_merge.py"
         → writes standard bug record to data/processed/bugsinpy_bugs.jsonl

Step 1.  PIPELINE ENTRY (run_pipeline.py)
         Reads one line from bugsinpy_bugs.jsonl
         Creates ASQAState(bug_id="bugsinpy_pandas_1", diff="--- a/pandas...", ...)
         Sets state.pipeline_start_time = time.time()
         Calls compiled_graph.invoke(state)

Step 2.  LANGGRAPH starts — routes to code_reader node

Step 3.  CODE READER NODE (code_reader.py)
         Builds prompt with state.diff (the raw git diff string)
         Calls GPT-4o via langchain_openai.ChatOpenAI
         GPT-4o returns JSON: {"risky_methods": [...], "summary": "..."}
         Agent parses JSON, stores in state.risk_analysis
         Returns updated state to LangGraph

Step 4.  LANGGRAPH routes to test_generator node

Step 5.  TEST GENERATOR NODE — FIRST ATTEMPT (test_generator.py)
         state.retry_count is 0, so uses first-attempt prompt
         Builds prompt with state.risk_analysis + state.diff
         Calls Claude Sonnet via langchain_anthropic.ChatAnthropic
         Claude returns a raw Python test file string
         Agent stores in state.generated_test, state.test_filename
         Returns updated state to LangGraph

Step 6.  LANGGRAPH routes to runner node

Step 7.  RUNNER NODE (runner.py + sandbox.py)
         sandbox.py: docker.from_env()
         Writes state.generated_test to a temp file inside the container
         Runs: git checkout {state.buggy_commit} inside the repo volume
         Runs: pytest test_asqa_bugsinpy_pandas_1.py -v
         Captures stdout + stderr + exit_code
         
         --- SCENARIO A: test has a syntax error ---
         stdout contains "SyntaxError: unexpected indent"
         GPT-4o-mini classifies as "execution_error"
         Agent sets state.execution_error = "SyntaxError: unexpected indent"
         Returns state to LangGraph
         
         LANGGRAPH: decide_after_runner sees execution_error + retry_count=0 < 2
         Routes back to test_generator node
         
Step 8.  TEST GENERATOR NODE — RETRY (test_generator.py)
         state.retry_count is now 1, so uses retry prompt
         Prompt includes state.execution_error + state.generated_test
         Claude Sonnet returns a fixed test file
         Agent stores new test in state.generated_test, increments retry_count to 1
         Returns to LangGraph → routes to runner again
         
Step 9.  RUNNER NODE — SECOND ATTEMPT
         Docker runs the fixed test
         
         --- SCENARIO B: test runs, assertions fail ---
         stdout: "FAILED test_asqa_..::test_merge_behavior - AssertionError"
         exit_code: 1
         GPT-4o-mini classifies as "test_failure"
         Agent sets state.test_passed = False, state.test_exit_code = 1
         state.execution_error = None (no execution error this time)
         Returns to LangGraph
         
         LANGGRAPH: decide_after_runner sees no execution_error → "continue"
         Routes to bug_reporter node

Step 10. BUG REPORTER NODE (bug_reporter.py)
         Builds prompt with diff + risk_analysis + test_output
         Calls GPT-4o
         GPT-4o returns: {"is_real_bug": true, "severity": "high", ...}
         Agent parses, stores in state.bug_report
         Sets state.final_status = "bug_found"
         Returns to LangGraph

Step 11. LANGGRAPH routes to fix_suggester node

Step 12. FIX SUGGESTER NODE (fix_suggester.py)
         Builds prompt with diff + bug_report + test_output
         Calls Claude Sonnet
         Claude returns: {"reasoning": "...", "fix_patch": "--- a/...", ...}
         Agent parses, stores state.fix_patch + state.fix_explanation
         Sets state.pipeline_end_time = time.time()
         Returns final state to LangGraph

Step 13. LANGGRAPH reaches END node

Step 14. compiled_graph.invoke() returns final ASQAState to run_pipeline.py

Step 15. run_pipeline.py appends result to evaluation/results/pipeline_outputs.jsonl:
         {
           "bug_id": "bugsinpy_pandas_1",
           "final_status": "bug_found",
           "test_passed_on_buggy": false,   ← this is what counts for BDR
           "retry_count": 1,
           "cost_usd": 0.031,
           "mttr_seconds": 47.3,
           "langsmith_run_id": "abc123"
         }
```

---

## 16. Environment Variables & Configuration

```bash
# .env — copy this to your local .env, fill in values, NEVER commit to git

# LLM API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# LangSmith (observability)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls__...
LANGCHAIN_PROJECT=asqa-experiments

# Pipeline configuration
ASQA_MAX_RETRIES=2              # how many times Runner can send back to Test Generator
ASQA_DOCKER_TIMEOUT=120         # seconds before Docker kills the test run
ASQA_DOCKER_MEM_LIMIT=512m      # memory cap per container
ASQA_MAX_DIFF_TOKENS=80000      # truncate diffs longer than this before sending to GPT-4o

# Dataset paths
BUGSINPY_REPO_PATH=./data/raw/bugsinpy
DEFECTS4J_REPO_PATH=./data/raw/defects4j
PROCESSED_DATA_PATH=./data/processed
RESULTS_PATH=./evaluation/results
```

---

## 17. Key Data Contracts (Input/Output Schemas)

### Code Reader output schema

```json
{
  "risky_methods": [
    {
      "name": "DataFrame.merge",
      "file": "pandas/core/frame.py",
      "risk_score": 0.92,
      "reason": "Logic change in merge key resolution can produce silent wrong output"
    }
  ],
  "summary": "This diff changes how merge handles duplicate keys. The new logic may produce duplicate rows that were previously deduplicated.",
  "language": "python"
}
```

### Bug Reporter output schema

```json
{
  "is_real_bug": true,
  "severity": "high",
  "affected_method": "pandas.core.frame.DataFrame.merge",
  "root_cause_hypothesis": "The deduplication guard was removed from the merge key resolution path on line 4821. When both DataFrames have the same key column, the cross-product is now computed before deduplication rather than after, causing O(n²) row explosion.",
  "reproduction_steps": [
    "Create two DataFrames with overlapping key column 'id'",
    "Call df1.merge(df2, on='id')",
    "Observe that the result has more rows than expected"
  ],
  "confidence": 0.87
}
```

### Fix Suggester output schema

```json
{
  "reasoning": "The root cause is on line 4821 of frame.py where the dedup call was removed. The fix should restore the deduplication call before the cross-product computation. This is safe because the deduplication only affects the merge key column, not any data columns.",
  "fix_patch": "--- a/pandas/core/frame.py\n+++ b/pandas/core/frame.py\n@@ -4819,6 +4819,7 @@\n     def _merge_keys(self, right, ...):\n+        left_keys = left_keys.drop_duplicates()\n         result = ...",
  "fix_explanation": "Restored the drop_duplicates() call on merge keys that was accidentally removed. Without this, merging DataFrames with duplicate keys creates a Cartesian product instead of the expected result.",
  "confidence": 0.91
}
```

---

## 18. Error Handling & Edge Cases

### Case 1: Diff is too large for context window

```python
# In code_reader.py, before calling GPT-4o:
MAX_DIFF_CHARS = 300000  # roughly 80k tokens at 4 chars/token
if len(state.diff) > MAX_DIFF_CHARS:
    # Take first 150k chars (changed lines) + last 50k (context)
    state.diff = state.diff[:150000] + "\n[DIFF TRUNCATED]\n" + state.diff[-50000:]
```

Log this truncation to LangSmith as a warning tag on the trace.

### Case 2: JSON parsing fails (model returned malformed JSON)

```python
# In any agent that parses JSON:
try:
    result = json.loads(response_text)
except json.JSONDecodeError:
    # One retry with an explicit correction prompt
    correction_prompt = f"Your last response was not valid JSON. Return ONLY the JSON object, no other text:\n\n{response_text}"
    response_text = call_llm(correction_prompt)
    result = json.loads(response_text)   # if this fails too, raise and mark pipeline as failed
```

### Case 3: Docker daemon not running

```python
# In sandbox.py:
try:
    client = docker.from_env()
    client.ping()
except docker.errors.DockerException:
    raise RuntimeError("Docker is not running. Start Docker Desktop and retry.")
```

### Case 4: Test runs but is not conclusive (passes on both buggy AND fixed version)

This is detected during evaluation, not during the pipeline. After collecting all results, for each bug you run the generated test on BOTH commits:
- Test fails on buggy + passes on fixed = **perfect** (counts toward BDR)
- Test passes on both = **inconclusive** (does not count toward BDR)
- Test fails on both = **bad test** (does not count toward BDR)

### Case 5: Max retries exceeded with execution error

If after 2 retries the test still won't run, LangGraph continues forward anyway. The bug_reporter will receive `test_passed = False` and `execution_error != None`. GPT-4o is instructed to set `confidence` very low in this case, and the bug is flagged `final_status = "failed"`. Exclude these from KPI calculations.

---

## 19. How Each File Talks to the Others

```
run_pipeline.py
    │   reads from ─────────────────── data/processed/*.jsonl
    │   creates ──────────────────────  ASQAState  (pipeline/state.py)
    │   calls ───────────────────────── compiled_graph  (pipeline/graph.py)
    │   writes to ───────────────────── evaluation/results/pipeline_outputs.jsonl
    │
pipeline/graph.py
    │   imports all agents from ────── pipeline/agents/*.py
    │   uses state type from ─────────  pipeline/state.py
    │   routing function ────────────── decide_after_runner() defined inline
    │
pipeline/agents/code_reader.py
    │   reads ───────────────────────── state.diff, state.language
    │   calls ───────────────────────── OpenAI GPT-4o (via langchain_openai)
    │   writes ──────────────────────── state.risk_analysis
    │
pipeline/agents/test_generator.py
    │   reads ───────────────────────── state.risk_analysis, state.diff, state.execution_error
    │   calls ───────────────────────── Anthropic Claude Sonnet (via langchain_anthropic)
    │   writes ──────────────────────── state.generated_test, state.test_filename
    │
pipeline/agents/runner.py
    │   reads ───────────────────────── state.generated_test, state.repo_path, state.buggy_commit
    │   calls ───────────────────────── pipeline/docker/sandbox.py
    │   calls ───────────────────────── OpenAI GPT-4o-mini (classification only)
    │   writes ──────────────────────── state.test_passed, state.test_output, state.execution_error
    │
pipeline/docker/sandbox.py
    │   reads ───────────────────────── repo_path (mounted as Docker volume)
    │   calls ───────────────────────── docker Python SDK
    │   uses ────────────────────────── pipeline/docker/Dockerfile.sandbox
    │   returns ─────────────────────── {"stdout": str, "exit_code": int}
    │
pipeline/agents/bug_reporter.py
    │   reads ───────────────────────── state.diff, state.risk_analysis, state.test_output
    │   calls ───────────────────────── OpenAI GPT-4o
    │   writes ──────────────────────── state.bug_report, state.final_status
    │
pipeline/agents/fix_suggester.py
    │   reads ───────────────────────── state.diff, state.bug_report, state.test_output
    │   calls ───────────────────────── Anthropic Claude Sonnet
    │   writes ──────────────────────── state.fix_patch, state.fix_explanation
    │
evaluation/kpi_calculator.py
    │   reads ───────────────────────── evaluation/results/pipeline_outputs.jsonl
    │   reads ───────────────────────── LangSmith API (token counts, latencies)
    │   computes ─────────────────────── all 5 KPIs
    │   writes ──────────────────────── evaluation/results/kpi_summary.csv
    │
evaluation/statistical_tests.py
    │   reads ───────────────────────── evaluation/results/kpi_summary.csv
    │   computes ─────────────────────── McNemar test, Wilcoxon test
    │   writes ──────────────────────── evaluation/results/statistical_tests.txt
```

---

*End of ARCHITECTURE.md*
*Last updated: ASQA v1.0 — NCI MSc AI, Machine Learning Project*