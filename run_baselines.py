"""
Run baseline systems on bug records for comparison with ASQA.

This script:
1. Loads the same test set bugs as the ASQA pipeline
2. Runs both single-agent baselines: GPT-4o and Claude Sonnet
3. Saves results to separate JSONL files for statistical comparison
"""

import json
import time
import os
import sys
from pathlib import Path
from typing import Generator, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

from baselines.single_agent_gpt4o import run_single_agent_gpt4o
from baselines.single_agent_claude import run_single_agent_claude


def load_bug_records(data_dir: str = None) -> Generator[Dict, None, None]:
    """
    Load bug records from processed JSONL files (test split only).

    Args:
        data_dir: Directory containing processed JSONL files

    Yields:
        Bug record dictionaries (test split only)
    """
    if data_dir is None:
        data_dir = os.getenv("PROCESSED_DATA_PATH", "./data/processed")

    data_path = Path(data_dir)

    for jsonl_file in data_path.glob("*_bugs.jsonl"):
        print(f"Loading from {jsonl_file.name}...")

        with open(jsonl_file) as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    if record.get("split") == "test":
                        yield record


def run_baseline_on_bug(baseline_func, bug_record: Dict) -> Dict:
    """
    Run a single baseline on a bug record.

    Args:
        baseline_func: Either run_single_agent_gpt4o or run_single_agent_claude
        bug_record: Bug record dictionary

    Returns:
        Result dictionary with key metrics
    """
    start_time = time.time()

    try:
        state_fields = {
            "bug_id": bug_record.get("bug_id", ""),
            "source": bug_record.get("source", ""),
            "language": bug_record.get("language", ""),
            "repo_path": bug_record.get("repo_path", ""),
            "buggy_commit": bug_record.get("buggy_commit", ""),
            "fixed_commit": bug_record.get("fixed_commit", ""),
            "diff": bug_record.get("diff", ""),
            "bug_description": bug_record.get("bug_description", ""),
            "failing_test": bug_record.get("failing_test", ""),
        }

        # Run baseline — returns a dict now
        final_state = baseline_func(state_fields)

        elapsed = time.time() - start_time

        result_dict = {
            "bug_id": final_state.get("bug_id", ""),
            "final_status": final_state.get("final_status", ""),
            "test_passed_on_buggy": final_state.get("test_passed"),
            "cost_usd": final_state.get("total_cost_usd"),
            "mttr_seconds": elapsed,
            "error_message": final_state.get("error_message"),
        }

    except Exception as e:
        elapsed = time.time() - start_time
        result_dict = {
            "bug_id": bug_record.get("bug_id", "unknown"),
            "final_status": "failed",
            "test_passed_on_buggy": None,
            "cost_usd": None,
            "mttr_seconds": elapsed,
            "error_message": str(e),
        }

    return result_dict


def save_baseline_result(result: Dict, output_path: str) -> None:
    """Save baseline result to JSONL file (append)."""
    with open(output_path, "a") as f:
        f.write(json.dumps(result) + "\n")


def main(baseline_name: str = "gpt4o", max_bugs: int = None):
    """
    Main entry point - run specified baseline on test bugs.

    Args:
        baseline_name: "gpt4o" or "claude"
        max_bugs: Maximum number of bugs to process (for testing)
    """
    results_dir = os.getenv("RESULTS_PATH", "./evaluation/results")
    os.makedirs(results_dir, exist_ok=True)

    if baseline_name == "gpt4o":
        output_path = os.path.join(results_dir, "baseline_gpt4o_outputs.jsonl")
        baseline_func = run_single_agent_gpt4o
        print("Running GPT-4o Single-Agent Baseline...")
    elif baseline_name == "claude":
        output_path = os.path.join(results_dir, "baseline_claude_outputs.jsonl")
        baseline_func = run_single_agent_claude
        print("Running Claude Sonnet Single-Agent Baseline...")
    else:
        raise ValueError(f"Unknown baseline: {baseline_name}")

    if os.path.exists(output_path):
        os.remove(output_path)

    bug_count = 0
    for bug_record in load_bug_records():
        if max_bugs and bug_count >= max_bugs:
            break

        print(f"\n[{bug_count + 1}] Processing {bug_record['bug_id']}...")

        try:
            result = run_baseline_on_bug(baseline_func, bug_record)
            save_baseline_result(result, output_path)

            print(f"  Status: {result['final_status']}")
            print(f"  Time: {result['mttr_seconds']:.1f}s")
            if result['cost_usd']:
                print(f"  Cost: ${result['cost_usd']:.4f}")

        except Exception as e:
            print(f"  ERROR: {e}")

        bug_count += 1

    print(f"\n\nCompleted {bug_count} bugs with {baseline_name} baseline.")
    print(f"Results saved to {output_path}")


if __name__ == "__main__":
    baseline = sys.argv[1] if len(sys.argv) > 1 else "gpt4o"
    max_bugs = int(sys.argv[2]) if len(sys.argv) > 2 else None

    main(baseline, max_bugs)
