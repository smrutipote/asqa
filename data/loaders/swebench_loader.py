"""
SWE-bench Verified data loader.

Loads SWE-bench Verified from HuggingFace into standard bug record format.
"""

import json
from typing import Dict, Iterator


def load_swebench_bugs() -> Iterator[Dict]:
    """
    Load bugs from SWE-bench Verified dataset.
    
    Yields:
        Standard bug record dictionaries
    """
    try:
        from datasets import load_dataset
    except ImportError:
        raise ImportError("datasets package required: pip install datasets")
    
    # Load the dataset from HuggingFace
    dataset = load_dataset("princeton-nlp/SWE-bench_Verified")
    
    for split_name, split_data in dataset.items():
        for row in split_data:
            bug_record = {
                "bug_id": row["instance_id"],
                "source": "swebench",
                "language": "python",  # most are Python, some multi-language
                "repo_name": row["repo"].split("/")[-1],
                "repo_path": "",  # not available in dataset
                "buggy_commit": row["base_commit"],
                "fixed_commit": "",  # would need to extract from patch
                "diff": row["patch"],
                "changed_files": [],
                "bug_description": row["problem_statement"],
                "failing_test": row.get("test_patch", ""),
                "split": split_name,
            }
            
            yield bug_record


if __name__ == "__main__":
    import os
    
    output_path = os.getenv("PROCESSED_DATA_PATH", "./data/processed") + "/swebench_bugs.jsonl"
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w") as out_f:
        for bug_record in load_swebench_bugs():
            out_f.write(json.dumps(bug_record) + "\n")
    
    print(f"Written to {output_path}")
