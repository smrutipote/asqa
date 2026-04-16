"""
Baseline 1 - Single Agent GPT-4o

A single GPT-4o call with a mega-prompt asking for:
1. A test file
2. A bug report
3. A fix patch

All in one response, to compare against the 5-agent ASQA pipeline.
Also includes test execution to determine if tests expose bugs.
"""

import json
import time
from typing import Dict
from pipeline.docker.sandbox import run_test_in_sandbox


def run_single_agent_gpt4o(bug_record: Dict) -> Dict:
    """
    Run single-agent baseline with GPT-4o (via Azure OpenAI).

    Args:
        bug_record: Standard bug record dict

    Returns:
        Result dict with all fields populated
    """
    from langchain_openai import AzureChatOpenAI
    import os

    # Initialize state as a dict
    state = dict(bug_record)
    state["pipeline_start_time"] = time.time()
    state["final_status"] = "pending"

    # Single-agent GPT-4.1-mini baseline
    model = AzureChatOpenAI(
        deployment_name="gpt-4.1-mini",
        temperature=0,
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2025-04-01-preview",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )

    system_prompt = """You are an expert software engineer and QA specialist.

Given a git diff, you must produce:
1. A complete, executable test file that exposes any bug in the diff
2. A structured bug report analyzing the diff
3. A minimal patch to fix any bug found

Return ONLY valid JSON:
{
  "generated_test": "<complete test file content>",
  "bug_report": {
    "is_real_bug": <bool>,
    "severity": "<critical|high|medium|low>",
    "affected_method": "<method name>",
    "root_cause_hypothesis": "<description>",
    "reproduction_steps": ["<step1>", "<step2>", ...],
    "confidence": <float 0.0-1.0>
  },
  "fix_patch": "<unified diff patch>",
  "fix_explanation": "<plain English explanation>"
}"""

    user_message = f"""Language: {state.get("language", "")}
Bug description: {state.get("bug_description", "")}

Git diff:
{state.get("diff", "")}

Produce a test, bug report, and fix patch for this change."""

    try:
        # Add retry logic for API errors
        import random
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = model.invoke([
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ])
                break
            except Exception as e:
                if any(err in str(e).lower() for err in ["overloaded", "rate_limit", "timeout"]) and attempt < max_retries - 1:
                    wait_time = 2 ** attempt + random.uniform(0, 1)
                    print(f"    API error, retrying in {wait_time:.1f}s...")
                    time.sleep(wait_time)
                else:
                    raise

        result = json.loads(response.content)

        state["generated_test"] = result.get("generated_test", "")
        state["bug_report"] = result.get("bug_report", {})
        state["fix_patch"] = result.get("fix_patch", "")
        state["fix_explanation"] = result.get("fix_explanation", "")
        state["test_filename"] = f"test_baseline_gpt4o_{state.get('bug_id', '')}.py"

        # Execute the generated test in sandbox
        if state["generated_test"] and state.get("language") == "python":
            try:
                sandbox_result = run_test_in_sandbox(
                    repo_path=state.get("repo_path", ""),
                    test_file_content=state["generated_test"],
                    test_filename=state["test_filename"],
                    language="python",
                    buggy_commit=state.get("buggy_commit", "")
                )
                state["test_exit_code"] = sandbox_result.get("exit_code", None)
                state["test_output"] = sandbox_result.get("stdout", "")
                state["test_passed"] = (state["test_exit_code"] == 0)
            except Exception as e:
                state["execution_error"] = str(e)
                state["test_passed"] = None

        state["final_status"] = "completed"

    except Exception as e:
        state["error_message"] = str(e)
        state["final_status"] = "failed"

    state["pipeline_end_time"] = time.time()
    return state
