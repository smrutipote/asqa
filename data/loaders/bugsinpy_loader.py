"""
BugsInPy data loader.

Loads BugsInPy bugs into standard bug record format.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Iterator


def load_bugsinpy_bugs(bugsinpy_repo_path: str) -> Iterator[Dict]:
    """
    Load all bugs from BugsInPy repository and yield standard bug records.
    
    Args:
        bugsinpy_repo_path: Path to cloned BugsInPy repository
        
    Yields:
        Standard bug record dictionaries
    """
    bugsinpy_path = Path(bugsinpy_repo_path)
    
    # Walk the directory tree to find all bug.info files
    for bug_info_path in bugsinpy_path.glob("projects/*/bugs/*/bug.info"):
        bug_dir = bug_info_path.parent
        project_dir = bug_dir.parent.parent
        project_name = project_dir.name
        
        try:
            # Read bug.info to get metadata (format: key="value")
            with open(bug_info_path) as f:
                bug_info = {}
                for line in f:
                    line = line.strip()
                    if not line or "=" not in line:
                        continue
                    key, value = line.split("=", 1)
                    # Remove quotes from value if present
                    value = value.strip()
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    bug_info[key.strip()] = value
            
            buggy_commit = bug_info.get("buggy_commit_id")
            fixed_commit = bug_info.get("fixed_commit_id")
            
            if not buggy_commit or not fixed_commit:
                continue
            
            # Read bug_patch.txt to get the diff
            bug_patch_path = bug_dir / "bug_patch.txt"
            diff = ""
            if bug_patch_path.exists():
                with open(bug_patch_path) as f:
                    diff = f.read()
            
            # Read run_test.sh to get the test command
            run_test_path = bug_dir / "run_test.sh"
            failing_test = ""
            if run_test_path.exists():
                with open(run_test_path) as f:
                    failing_test = f.read().strip()
            
            bug_id = f"bugsinpy_{project_name}_{bug_dir.name}"
            
            # Use absolute path for repo_path if it exists, empty string otherwise
            repo_path_abs = str(project_dir.resolve())
            if not os.path.exists(repo_path_abs):
                repo_path_to_use = ""
            else:
                repo_path_to_use = repo_path_abs
            
            bug_record = {
                "bug_id": bug_id,
                "source": "bugsinpy",
                "language": "python",
                "repo_name": project_name,
                "repo_path": repo_path_to_use,
                "buggy_commit": buggy_commit,
                "fixed_commit": fixed_commit,
                "diff": diff,
                "changed_files": [],
                "bug_description": "",
                "failing_test": failing_test,
                "split": "test",
            }
            
            yield bug_record
            
        except Exception as e:
            print(f"Error processing {bug_dir}: {e}")
            continue


if __name__ == "__main__":
    import sys
    
    bugsinpy_path = os.getenv("BUGSINPY_REPO_PATH", "./data/raw/bugsinpy")
    output_path = os.getenv("PROCESSED_DATA_PATH", "./data/processed") + "/bugsinpy_bugs.jsonl"
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w") as out_f:
        for bug_record in load_bugsinpy_bugs(bugsinpy_path):
            out_f.write(json.dumps(bug_record) + "\n")
    
    print(f"Written to {output_path}")
