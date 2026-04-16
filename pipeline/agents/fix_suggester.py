"""
Agent 5 — Fix Suggester

Performs root cause analysis and generates a minimal patch to fix the bug.

Model: Claude Sonnet 4 (best at reasoning-heavy tasks before code generation)
"""

import json
import os
from langchain_core.messages import SystemMessage, HumanMessage
from pipeline.state import ASQAState


def fix_suggester_node(state: ASQAState) -> dict:
    """
    Suggest a minimal fix patch for the identified bug.

    Args:
        state: Current ASQAState dict with bug_report populated

    Returns:
        Partial state update dict with fix_patch and fix_explanation
    """
    from langchain_anthropic import ChatAnthropic

    model = ChatAnthropic(
        model="claude-sonnet-4-20250514",
        temperature=0,
        api_key=os.getenv("ANTHROPIC_API_KEY")
    )

    system_prompt = """You are a principal software engineer specialising in debugging and patch generation.

Before writing any code, you MUST:
1. Identify the exact root cause (not just the symptom)
2. Reason about whether a fix at the symptom level or root level is appropriate
3. Consider whether the fix might break other functionality

Then produce:
- A MINIMAL unified diff patch that fixes only the root cause
- A plain-English explanation of your reasoning

Return valid JSON:
{
  "reasoning": "<your step-by-step analysis before writing the patch>",
  "fix_patch": "<unified diff string, starting with --- and +++>",
  "fix_explanation": "<plain English, 2-3 sentences>",
  "confidence": <float 0.0-1.0>
}"""

    bug_report = state.get("bug_report")
    user_message = f"""Language: {state.get("language", "")}

Original diff (what was changed that caused the bug):
{state.get("diff", "")}

Bug report:
{json.dumps(bug_report, indent=2) if bug_report else ""}

Test output that exposed the bug:
{state.get("test_output", "")}

Produce a minimal patch that fixes this bug."""

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
        fix_result = json.loads(response_text)
    except (json.JSONDecodeError, Exception):
        fix_result = {
            "reasoning": "Unable to analyze",
            "fix_patch": "",
            "fix_explanation": "Could not generate fix",
            "confidence": 0.0
        }

    return {
        "fix_patch": fix_result.get("fix_patch", ""),
        "fix_explanation": fix_result.get("fix_explanation", ""),
    }
