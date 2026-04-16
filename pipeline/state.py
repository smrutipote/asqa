"""
ASQA State object - the shared memory across all agents in the pipeline.

This TypedDict flows through every node in the LangGraph state machine.
LangGraph requires TypedDict (not dataclass) for StateGraph state schemas.
"""

from typing import Optional, List, Dict
from typing_extensions import TypedDict


class ASQAState(TypedDict, total=False):
    """
    The complete state object for ASQA pipeline.

    Attributes are organized into sections:
    - INPUT: Set once at pipeline start, never modified
    - AGENT 1 OUTPUT: Code Reader results
    - AGENT 2 OUTPUT: Test Generator results
    - AGENT 3 OUTPUT: Runner results
    - AGENT 4 OUTPUT: Bug Reporter results
    - AGENT 5 OUTPUT: Fix Suggester results
    - PIPELINE METADATA: Automatic tracking
    """

    # ── INPUT (set once by run_pipeline.py, never changed) ──────────────────
    bug_id: str
    source: str  # "bugsinpy" | "defects4j" | "swebench"
    language: str  # "python" | "java"
    repo_path: str  # absolute path to repo on disk
    buggy_commit: str
    fixed_commit: str
    diff: str  # raw unified diff — the main input
    bug_description: str
    failing_test: str  # ground truth (used only for evaluation)

    # ── AGENT 1 OUTPUT (Code Reader) ─────────────────────────────────────────
    risk_analysis: Optional[Dict]
    # {
    #   "risky_methods": [{"name": str, "file": str, "risk_score": float, "reason": str}],
    #   "summary": str,
    #   "language": str
    # }

    # ── AGENT 2 OUTPUT (Test Generator) ──────────────────────────────────────
    generated_test: Optional[str]  # full Python/Java test file as string
    test_filename: Optional[str]  # e.g. "test_asqa_generated.py"
    retry_count: int  # how many times we've retried generation

    # ── AGENT 3 OUTPUT (Runner) ───────────────────────────────────────────────
    test_passed: Optional[bool]
    test_output: Optional[str]  # full stdout + stderr from test run
    test_exit_code: Optional[int]  # 0 = pass, non-zero = fail
    execution_error: Optional[str]  # syntax errors, import errors, etc.

    # ── AGENT 4 OUTPUT (Bug Reporter) ─────────────────────────────────────────
    bug_report: Optional[Dict]
    # {
    #   "is_real_bug": bool,
    #   "severity": "critical" | "high" | "medium" | "low",
    #   "affected_method": str,
    #   "root_cause_hypothesis": str,
    #   "reproduction_steps": [str],
    #   "confidence": float   (0.0 – 1.0)
    # }

    # ── AGENT 5 OUTPUT (Fix Suggester) ────────────────────────────────────────
    fix_patch: Optional[str]  # unified diff patch string
    fix_explanation: Optional[str]  # plain English reasoning

    # ── PIPELINE METADATA (set automatically during runs) ────────────────────
    pipeline_start_time: Optional[float]  # time.time() at pipeline start
    pipeline_end_time: Optional[float]
    total_cost_usd: Optional[float]  # computed from LangSmith tokens
    langsmith_run_id: Optional[str]
    error_message: Optional[str]  # set if pipeline crashed
    final_status: str  # "pending"|"bug_found"|"no_bug"|"failed"
