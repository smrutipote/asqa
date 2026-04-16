"""
Defects4J data loader.

Loads Defects4J bugs into standard bug record format.
Requires Defects4J to be installed and initialized.
"""

import os
import csv
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Iterator, Optional, List


DEFECTS4J_BIN = None  # Set during initialization

def _find_defects4j_bin() -> str:
    """Find the defects4j executable path."""
    # Try environment variable first
    if env_path := os.getenv("DEFECTS4J_HOME"):
        bin_path = os.path.join(env_path, "framework", "bin", "defects4j")
        if os.path.exists(bin_path):
            return bin_path
    
    # Try default installation in data/raw
    default_path = "./data/raw/defects4j/framework/bin/defects4j"
    if os.path.exists(default_path):
        return os.path.abspath(default_path)
    
    # Try absolute path
    abs_path = "/Users/akshaysmruti/Downloads/asqa/data/raw/defects4j/framework/bin/defects4j"
    if os.path.exists(abs_path):
        return abs_path
    
    raise RuntimeError("Cannot find defects4j executable. Set DEFECTS4J_HOME or ensure it's in ./data/raw/defects4j")


def _run_defects4j_command(args: List[str]) -> str:
    """Run a defects4j command and return stdout."""
    global DEFECTS4J_BIN
    if DEFECTS4J_BIN is None:
        DEFECTS4J_BIN = _find_defects4j_bin()
    
    try:
        result = subprocess.run(
            [DEFECTS4J_BIN] + args,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return ""


def _get_project_ids() -> List[str]:
    """Get all available Defects4J project IDs."""
    output = _run_defects4j_command(["pids"])
    return [line.strip() for line in output.split("\n") if line.strip()]


def _get_bug_ids(project_id: str) -> List[int]:
    """Get all bug IDs for a project."""
    output = _run_defects4j_command(["bids", "-p", project_id])
    try:
        return [int(line.strip()) for line in output.split("\n") if line.strip()]
    except ValueError:
        return []


def _get_diff(project_id: str, bug_id: int, buggy_commit: str, fixed_commit: str, work_dir: str) -> str:
    """Get unified diff between buggy and fixed commits."""
    try:
        # Get git repository path
        repo_info = _run_defects4j_command(["info", "-p", project_id])
        # Parse repo path from info output
        repo_path = None
        for line in repo_info.split("\n"):
            if "Repository:" in line:
                repo_path = line.split("Repository:")[-1].strip()
                break
        
        if not repo_path or not os.path.exists(repo_path):
            return ""
        
        # Generate diff using git
        cmd = f"cd {repo_path} && git diff {buggy_commit}..{fixed_commit} --no-ext-diff"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout if result.returncode == 0 else ""
    except Exception as e:
        return ""


def _get_failing_test(project_id: str, bug_id: int, work_dir: str) -> str:
    """Get the triggering test for a bug by checking out and examining."""
    try:
        # Use the defects4j export command to get trigger tests
        cmd = f"cd {work_dir} && {DEFECTS4J_BIN if DEFECTS4J_BIN else _find_defects4j_bin()} export -p tests.trigger"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            tests = result.stdout.strip().split("\n")
            return tests[0] if tests else ""
        return ""
    except Exception as e:
        return ""


def _get_bug_description(project_id: str, bug_id: int) -> str:
    """Get bug description from info command."""
    try:
        output = _run_defects4j_command(["info", "-p", project_id, "-b", str(bug_id)])
        if "Root cause in triggering tests:" in output:
            lines = output.split("Root cause in triggering tests:")[-1].split("\n")
            # Extract the exception info
            for line in lines[:5]:
                line = line.strip()
                if line and line.startswith("-"):
                    return line[1:].strip()
        return ""
    except Exception:
        return ""


def load_defects4j_bugs() -> Iterator[Dict]:
    """
    Load all bugs from Defects4J and yield standard bug records.
    
    Requires Defects4J to be installed. See:
    https://github.com/rjust/defects4j
    
    Yields:
        Standard bug record dictionaries
    """
    try:
        project_ids = _get_project_ids()
    except Exception as e:
        print(f"Error getting Defects4J projects: {e}")
        return
    
    global DEFECTS4J_BIN
    if DEFECTS4J_BIN is None:
        DEFECTS4J_BIN = _find_defects4j_bin()
    
    for project_id in sorted(project_ids):
        try:
            bug_ids = _get_bug_ids(project_id)
        except Exception:
            continue
        
        for bug_id in bug_ids:
            try:
                bug_id_str = str(bug_id)
                
                # Read metadata from CSV
                framework_path = os.path.dirname(DEFECTS4J_BIN)
                csv_path = os.path.join(framework_path, "..", "projects", project_id, "active-bugs.csv")
                csv_path = os.path.abspath(csv_path)
                
                buggy_commit = None
                fixed_commit = None
                report_id = None
                report_url = None
                
                if os.path.exists(csv_path):
                    with open(csv_path) as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            if row.get("bug.id") == bug_id_str:
                                buggy_commit = row.get("revision.id.buggy", "")
                                fixed_commit = row.get("revision.id.fixed", "")
                                report_id = row.get("report.id", "")
                                report_url = row.get("report.url", "")
                                break
                
                if not buggy_commit or not fixed_commit:
                    continue
                
                # Create a persistent checkout directory for this bug
                checkouts_base = os.path.join(os.path.dirname(DEFECTS4J_BIN), "..", "checkouts")
                os.makedirs(checkouts_base, exist_ok=True)
                work_dir = os.path.join(checkouts_base, f"{project_id}_{bug_id_str}b")
                
                repo_path_abs = ""  # Will be set if checkout succeeds
                diff = ""
                failing_test = ""
                
                try:
                    # Clean up previous checkout if exists
                    if os.path.exists(work_dir):
                        import shutil
                        shutil.rmtree(work_dir)
                    
                    # Checkout buggy version
                    checkout_cmd = f"{DEFECTS4J_BIN} checkout -p {project_id} -v {bug_id_str}b -w {work_dir}"
                    result = subprocess.run(checkout_cmd, shell=True, capture_output=True, text=True, timeout=60)
                    
                    if result.returncode == 0:
                        # Checkout succeeded - set repo_path and get additional info
                        repo_path_abs = os.path.abspath(work_dir)
                        diff = _get_diff(project_id, bug_id, buggy_commit, fixed_commit, work_dir)
                        failing_test = _get_failing_test(project_id, bug_id, work_dir)
                    # else: checkout failed - keep repo_path empty, will be handled downstream
                except Exception as e:
                    # Checkout error - keep repo_path empty
                    repo_path_abs = ""
                
                # Always yield the bug record, even if checkout failed
                bug_record = {
                    "bug_id": f"defects4j_{project_id}_{bug_id}",
                    "source": "defects4j",
                    "language": "java",
                    "repo_name": project_id,
                    "repo_path": repo_path_abs,  # Empty if checkout failed, absolute path if succeeded
                    "buggy_commit": buggy_commit,
                    "fixed_commit": fixed_commit,
                    "diff": diff,
                    "changed_files": [],
                    "bug_description": report_id or _get_bug_description(project_id, bug_id),
                    "failing_test": failing_test,
                    "split": "test",
                }
                    
                    yield bug_record
                    
            except Exception as e:
                continue


if __name__ == "__main__":
    output_path = os.getenv("PROCESSED_DATA_PATH", "./data/processed") + "/defects4j_bugs.jsonl"
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    count = 0
    with open(output_path, "w") as out_f:
        for bug_record in load_defects4j_bugs():
            out_f.write(json.dumps(bug_record) + "\n")
            count += 1
            if count % 50 == 0:
                print(f"Loaded {count} Defects4J bugs...")
    
    print(f"Written {count} Defects4J bugs to {output_path}")
