"""
Main entry point for running the ASQA pipeline on bug records.

This script:
1. Reads bug records from data/processed/*.jsonl
2. Filters to the "test" split
3. For each bug, creates an ASQAState dict and runs the LangGraph pipeline
4. Saves results to evaluation/results/pipeline_outputs.jsonl
"""

import json
import time
import os
from pathlib import Path
from typing import Generator, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

from pipeline.graph import build_graph


def load_bug_records(data_dir: str = None) -> Generator[Dict, None, None]:
    """
    Load bug records from processed JSONL files.

    Args:
        data_dir: Directory containing processed JSONL files

    Yields:
        Bug record dictionaries (test split only)
    """
    if data_dir is None:
        data_dir = os.getenv("PROCESSED_DATA_PATH", "./data/processed")

    data_path = Path(data_dir)

    # Load from all *.jsonl files in the directory
    for jsonl_file in data_path.glob("*_bugs.jsonl"):
        print(f"Loading from {jsonl_file.name}...")

        with open(jsonl_file) as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    # Filter to test split
                    if record.get("split") == "test":
                        yield record


def run_pipeline_on_bug(graph, bug_record: Dict) -> Dict:
    """
    Run the complete pipeline on a single bug.

    Args:
        graph: Compiled LangGraph graph
        bug_record: Bug record dictionary

    Returns:
        Final state dict with all results
    """
    initial_state = {
        "bug_id": bug_record.get("bug_id", ""),
        "source": bug_record.get("source", ""),
        "language": bug_record.get("language", ""),
        "repo_path": bug_record.get("repo_path", ""),
        "buggy_commit": bug_record.get("buggy_commit", ""),
        "fixed_commit": bug_record.get("fixed_commit", ""),
        "diff": bug_record.get("diff", ""),
        "bug_description": bug_record.get("bug_description", ""),
        "failing_test": bug_record.get("failing_test", ""),
        "pipeline_start_time": time.time(),
        "retry_count": 0,
        "final_status": "pending",
    }

    try:
        result_dict = graph.invoke(initial_state)
        result_dict["pipeline_end_time"] = time.time()

    except Exception as e:
        result_dict = dict(initial_state)
        result_dict["error_message"] = str(e)
        result_dict["final_status"] = "failed"
        result_dict["pipeline_end_time"] = time.time()

    return result_dict


def save_result(result: Dict, output_path: str) -> None:
    """
    Save pipeline result to JSONL file (append).

    Args:
        result: Final state dict
        output_path: Path to pipeline_outputs.jsonl
    """
    start = result.get("pipeline_start_time")
    end = result.get("pipeline_end_time")

    result_dict = {
        "bug_id": result.get("bug_id", ""),
        "final_status": result.get("final_status", "pending"),
        "test_passed_on_buggy": result.get("test_passed"),
        "retry_count": result.get("retry_count", 0),
        "cost_usd": result.get("total_cost_usd"),
        "mttr_seconds": (end - start) if end and start else None,
        "langsmith_run_id": result.get("langsmith_run_id"),
        "error_message": result.get("error_message"),
    }

    with open(output_path, "a") as f:
        f.write(json.dumps(result_dict) + "\n")


def main(max_bugs: int = None):
    """
    Main entry point - run pipeline on all bugs in test split.

    Args:
        max_bugs: Maximum number of bugs to process (for testing)
    """
    # Create results directory if needed
    results_dir = os.getenv("RESULTS_PATH", "./evaluation/results")
    os.makedirs(results_dir, exist_ok=True)

    output_path = os.path.join(results_dir, "pipeline_outputs.jsonl")

    # Build graph
    print("Building LangGraph pipeline...")
    graph = build_graph()

    # Process bugs
    bug_count = 0
    for bug_record in load_bug_records():
        if max_bugs and bug_count >= max_bugs:
            break

        print(f"\n[{bug_count + 1}] Processing {bug_record['bug_id']}...")

        try:
            result = run_pipeline_on_bug(graph, bug_record)
            save_result(result, output_path)

            print(f"  Status: {result.get('final_status', 'unknown')}")
            start = result.get("pipeline_start_time")
            end = result.get("pipeline_end_time")
            if start and end:
                elapsed = end - start
                print(f"  Time: {elapsed:.1f}s")

        except Exception as e:
            print(f"  ERROR: {e}")

        bug_count += 1

    print(f"\n\nCompleted {bug_count} bugs.")
    print(f"Results saved to {output_path}")


if __name__ == "__main__":
    import sys

    max_bugs = int(sys.argv[1]) if len(sys.argv) > 1 else None
    main(max_bugs)
