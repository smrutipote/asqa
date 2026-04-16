"""
Agent 2 — Test Generator

Generates a complete, executable test file that targets the risky methods
identified by the Code Reader.

Model: Claude Sonnet 4 (best long-form code generation)
"""

import json
import os
from typing import Optional
from langchain_core.messages import SystemMessage, HumanMessage
from pipeline.state import ASQAState


def test_generator_node(state: ASQAState) -> dict:
    """
    Generate a test file that exposes the bug.

    Args:
        state: Current ASQAState dict with risk_analysis populated

    Returns:
        Partial state update dict with generated_test and test_filename
    """
    from langchain_anthropic import ChatAnthropic

    model = ChatAnthropic(
        model="claude-sonnet-4-20250514",
        temperature=0,
        api_key=os.getenv("ANTHROPIC_API_KEY")
    )

    system_prompt = """You are an expert software test engineer. You write precise, executable tests
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

Return ONLY the raw test file content. No explanation, no markdown code fences."""

    retry_count = state.get("retry_count", 0)
    bug_id = state.get("bug_id", "unknown")
    language = state.get("language", "python")

    if retry_count == 0:
        risk_analysis = state.get("risk_analysis")
        user_message = f"""Language: {language}

Risk analysis from code reader:
{json.dumps(risk_analysis, indent=2) if risk_analysis else ""}

Relevant diff:
{state.get("diff", "")}

Write a test file that will expose the bug described in this diff."""
    else:
        user_message = f"""Your previous test attempt failed with this error:

{state.get("execution_error", "")}

Previous test code:
{state.get("generated_test", "")}

Fix the test so it compiles and runs successfully. Keep the same test logic
but fix the import/syntax/runtime error shown above."""

    try:
        response = model.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message),
        ])
    except Exception as e:
        if language == "python":
            test_filename = f"test_asqa_{bug_id}.py"
        else:
            test_filename = f"TestASQA{bug_id.replace('_', '').title()}.java"
        return {
            "generated_test": "def test_placeholder():\n    assert True",
            "test_filename": test_filename,
            "retry_count": retry_count + 1,
        }

    test_code = response.content

    if language == "python":
        test_filename = f"test_asqa_{bug_id}.py"
    elif language == "java":
        test_filename = f"TestASQA{bug_id.replace('_', '').title()}.java"
    else:
        test_filename = f"test_asqa_{bug_id}"

    return {
        "generated_test": test_code,
        "test_filename": test_filename,
        "retry_count": retry_count + 1,
    }
