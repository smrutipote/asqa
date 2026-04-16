"""
Agent 3 — Runner

Executes the generated test in an isolated Docker sandbox and classifies the result.

Components:
- Docker sandbox execution (pipeline/docker/sandbox.py)
- GPT-4.1-mini result classification
"""

import json
import os
from typing import Literal
from langchain_core.messages import HumanMessage
from pipeline.state import ASQAState
from pipeline.docker.sandbox import run_test_in_sandbox


def runner_node(state: ASQAState) -> dict:
    """
    Execute test in sandbox and classify the result.

    Args:
        state: Current ASQAState dict with generated_test populated

    Returns:
        Partial state update dict with test execution results
    """
    from langchain_openai import AzureChatOpenAI

    # Execute test in Docker sandbox
    try:
        result = run_test_in_sandbox(
            repo_path=state.get("repo_path", ""),
            test_file_content=state.get("generated_test", ""),
            test_filename=state.get("test_filename", ""),
            language=state.get("language", ""),
            buggy_commit=state.get("buggy_commit", ""),
        )
    except Exception as e:
        return {
            "test_passed": False,
            "test_exit_code": 1,
            "test_output": str(e),
            "execution_error": str(e),
        }

    stdout = result.get("stdout", "")
    stderr = result.get("stderr", "")
    exit_code = result.get("exit_code", 1)

    test_output = f"{stdout}\n{stderr}"

    # Classify the result with GPT-4.1-mini
    model = AzureChatOpenAI(
        deployment_name="gpt-4.1-mini",
        temperature=0,
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2025-04-01-preview",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )

    classification_prompt = f"""You are classifying the output of a test run.

Test output:
{test_output}

Exit code: {exit_code}

Classify this result as EXACTLY ONE of:
- "test_failure" - the test ran successfully but assertions failed (bug exposed)
- "execution_error" - the test could not run at all (syntax/import/dependency error)
- "test_pass" - the test ran and all assertions passed

Return ONLY the classification string. Nothing else."""

    try:
        response = model.invoke([HumanMessage(content=classification_prompt)])
        classification = response.content.strip().strip('"').lower()
    except Exception:
        classification = "test_failure" if exit_code != 0 else "test_pass"

    # Return partial state update based on classification
    if classification == "test_failure" or (classification not in ["execution_error", "test_pass"] and exit_code != 0):
        return {
            "test_passed": False,
            "test_exit_code": exit_code,
            "test_output": test_output,
            "execution_error": None,
        }
    elif classification == "execution_error":
        return {
            "test_passed": False,
            "test_exit_code": exit_code,
            "test_output": test_output,
            "execution_error": test_output,
        }
    elif classification == "test_pass":
        return {
            "test_passed": True,
            "test_exit_code": 0,
            "test_output": test_output,
            "execution_error": None,
        }

    return {
        "test_passed": False,
        "test_exit_code": exit_code,
        "test_output": test_output,
        "execution_error": None,
    }
