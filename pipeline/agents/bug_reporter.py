"""
Agent 4 — Bug Reporter

Synthesizes all evidence (diff, risk analysis, test execution, etc.) into
a structured bug report.

Model: GPT-4.1-mini (Azure OpenAI)
"""

import json
import os
from langchain_core.messages import SystemMessage, HumanMessage
from pipeline.state import ASQAState


def bug_reporter_node(state: ASQAState) -> dict:
    """
    Generate a structured bug report based on all pipeline data.

    Args:
        state: Current ASQAState dict with all agent results so far

    Returns:
        Partial state update dict with bug_report and final_status
    """
    from langchain_openai import AzureChatOpenAI

    model = AzureChatOpenAI(
        deployment_name="gpt-4.1-mini",
        temperature=0,
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2025-04-01-preview",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )

    system_prompt = """You are a senior QA engineer writing a formal bug report.

You have access to:
1. The original git diff
2. A risk analysis of the changed code
3. The result of running a test against the buggy version

Your job is to determine:
- Whether this is a genuine bug (not a false positive)
- Its severity
- The most likely root cause
- Clear reproduction steps

Return ONLY valid JSON. No preamble. No markdown code fences. Schema:

{
  "is_real_bug": <true | false>,
  "severity": "<critical | high | medium | low>",
  "affected_method": "<fully qualified method name>",
  "root_cause_hypothesis": "<one paragraph, be specific>",
  "reproduction_steps": ["<step 1>", "<step 2>", ...],
  "confidence": <float 0.0-1.0>
}"""

    risk_analysis = state.get("risk_analysis")
    user_message = f"""Diff:
{state.get("diff", "")}

Risk analysis:
{json.dumps(risk_analysis, indent=2) if risk_analysis else ""}

Test execution result:
- Test passed on buggy version: {state.get("test_passed")}
- Exit code: {state.get("test_exit_code")}
- Output:
{state.get("test_output", "")}

Bug description (if available):
{state.get("bug_description", "")}"""

    try:
        response = model.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message),
        ])
        response_text = response.content
        # Strip markdown code fences if present
        if response_text.startswith("```"):
            response_text = response_text.split("\n", 1)[1]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
        bug_report = json.loads(response_text)
    except (json.JSONDecodeError, Exception):
        bug_report = {
            "is_real_bug": state.get("test_passed") == False,
            "severity": "medium",
            "affected_method": "unknown",
            "root_cause_hypothesis": "Unable to analyze",
            "reproduction_steps": ["Run the generated test"],
            "confidence": 0.5
        }

    # Determine final_status
    is_real_bug = bug_report.get("is_real_bug", False)
    test_passed = state.get("test_passed")

    if is_real_bug and test_passed == False:
        final_status = "bug_found"
    elif is_real_bug and test_passed == True:
        final_status = "bug_found_test_weak"
    else:
        final_status = "no_bug"

    return {
        "bug_report": bug_report,
        "final_status": final_status,
    }
