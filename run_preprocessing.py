#!/usr/bin/env python3
"""
Data Ingestion Pipeline Orchestrator

Loads bugs from all three benchmarks (BugsInPy, Defects4J, SWE-bench Verified)
and writes standardised bug records to JSONL files in data/processed/.

This is a one-time preprocessing step. Run this before run_pipeline.py.

Environment Variables:
    BUGSINPY_REPO_PATH: Path to cloned BugsInPy repository (default: ./data/raw/bugsinpy)
    PROCESSED_DATA_PATH: Path to write processed data (default: ./data/processed)
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from data.loaders.bugsinpy_loader import load_bugsinpy_bugs
from data.loaders.defects4j_loader import load_defects4j_bugs
from data.loaders.swebench_loader import load_swebench_bugs


def ensure_output_dir(output_path: str) -> None:
    """Create output directory if it doesn't exist."""
    os.makedirs(output_path, exist_ok=True)


def process_bugsinpy(output_path: str, bugsinpy_repo_path: Optional[str] = None) -> int:
    """
    Load BugsInPy bugs and write to JSONL.
    
    Args:
        output_path: Directory to write output files
        bugsinpy_repo_path: Path to BugsInPy repository (default from env or ./data/raw/bugsinpy)
        
    Returns:
        Count of bugs loaded
    """
    if bugsinpy_repo_path is None:
        bugsinpy_repo_path = os.getenv("BUGSINPY_REPO_PATH", "./data/raw/bugsinpy")
    
    if not Path(bugsinpy_repo_path).exists():
        print(f"⚠️  BugsInPy repo not found at {bugsinpy_repo_path}")
        print(f"   Clone with: git clone https://github.com/soarsmu/BugsInPy {bugsinpy_repo_path}")
        return 0
    
    output_file = os.path.join(output_path, "bugsinpy_bugs.jsonl")
    
    print(f"\n📦 Loading BugsInPy bugs from {bugsinpy_repo_path}...")
    
    bug_count = 0
    with open(output_file, "w") as f:
        for bug_record in load_bugsinpy_bugs(bugsinpy_repo_path):
            f.write(json.dumps(bug_record) + "\n")
            bug_count += 1
    
    print(f"✓ Wrote {bug_count} BugsInPy bugs to {output_file}")
    return bug_count


def process_defects4j(output_path: str) -> int:
    """
    Load Defects4J bugs and write to JSONL.
    
    Args:
        output_path: Directory to write output files
        
    Returns:
        Count of bugs loaded
    """
    print(f"\n📦 Loading Defects4J bugs...")
    
    try:
        output_file = os.path.join(output_path, "defects4j_bugs.jsonl")
        bug_count = 0
        
        with open(output_file, "w") as f:
            for bug_record in load_defects4j_bugs():
                f.write(json.dumps(bug_record) + "\n")
                bug_count += 1
        
        print(f"✓ Wrote {bug_count} Defects4J bugs to {output_file}")
        return bug_count
    except Exception as e:
        print(f"⚠️  Defects4J loader failed: {e}")
        print(f"   Make sure Defects4J is installed and initialized")
        return 0


def process_swebench(output_path: str) -> int:
    """
    Load SWE-bench Verified bugs and write to JSONL.
    
    Args:
        output_path: Directory to write output files
        
    Returns:
        Count of bugs loaded
    """
    print(f"\n📦 Loading SWE-bench Verified bugs from HuggingFace...")
    
    try:
        output_file = os.path.join(output_path, "swebench_bugs.jsonl")
        bug_count = 0
        
        with open(output_file, "w") as f:
            for bug_record in load_swebench_bugs():
                f.write(json.dumps(bug_record) + "\n")
                bug_count += 1
        
        print(f"✓ Wrote {bug_count} SWE-bench bugs to {output_file}")
        return bug_count
    except Exception as e:
        print(f"⚠️  SWE-bench loader failed: {e}")
        print(f"   Install with: pip install datasets")
        return 0


def main():
    """Main preprocessing orchestration."""
    parser = argparse.ArgumentParser(
        description="Run data ingestion pipeline for ASQA",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_preprocessing.py                    # Load all datasets
  python run_preprocessing.py --bugsinpy-only   # Load only BugsInPy
  python run_preprocessing.py --no-swebench      # Skip SWE-bench Verified
        """,
    )
    parser.add_argument(
        "--bugsinpy-only",
        action="store_true",
        help="Load only BugsInPy dataset",
    )
    parser.add_argument(
        "--defects4j-only",
        action="store_true",
        help="Load only Defects4J dataset",
    )
    parser.add_argument(
        "--swebench-only",
        action="store_true",
        help="Load only SWE-bench Verified dataset",
    )
    parser.add_argument(
        "--no-bugsinpy",
        action="store_true",
        help="Skip BugsInPy dataset",
    )
    parser.add_argument(
        "--no-defects4j",
        action="store_true",
        help="Skip Defects4J dataset",
    )
    parser.add_argument(
        "--no-swebench",
        action="store_true",
        help="Skip SWE-bench Verified dataset",
    )
    parser.add_argument(
        "--output-path",
        type=str,
        default=os.getenv("PROCESSED_DATA_PATH", "./data/processed"),
        help="Directory to write processed data (default: ./data/processed)",
    )
    parser.add_argument(
        "--bugsinpy-path",
        type=str,
        default=os.getenv("BUGSINPY_REPO_PATH", "./data/raw/bugsinpy"),
        help="Path to BugsInPy repository (default: ./data/raw/bugsinpy)",
    )
    
    args = parser.parse_args()
    
    # Determine which datasets to load
    load_bugsinpy = not args.no_bugsinpy
    load_defects4j = not args.no_defects4j
    load_swebench = not args.no_swebench
    
    if args.bugsinpy_only:
        load_defects4j = load_swebench = False
    elif args.defects4j_only:
        load_bugsinpy = load_swebench = False
    elif args.swebench_only:
        load_bugsinpy = load_defects4j = False
    
    # Ensure output directory exists
    ensure_output_dir(args.output_path)
    
    print("=" * 60)
    print("ASQA Data Ingestion Pipeline")
    print("=" * 60)
    print(f"Output path: {args.output_path}")
    
    total_bugs = 0
    
    if load_bugsinpy:
        total_bugs += process_bugsinpy(args.output_path, args.bugsinpy_path)
    
    if load_defects4j:
        total_bugs += process_defects4j(args.output_path)
    
    if load_swebench:
        total_bugs += process_swebench(args.output_path)
    
    print("\n" + "=" * 60)
    print(f"✓ Pipeline complete: {total_bugs} bugs loaded total")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
