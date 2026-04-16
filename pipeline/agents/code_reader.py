"""
Agent 1 — Code Reader

Reads a git diff and produces a risk analysis identifying which methods
are most likely to contain the bug.

Model: GPT-4.1-mini (Azure OpenAI)
"""

import json
import os
from typing import Dict
from langchain_core.messages import SystemMessage, HumanMessage
from pipeline.state import ASQAState


def code_reader_node(state: ASQAState) -> dict:
    """
    Analyze the diff and identify risky methods.

    Args:
        state: Current ASQAState dict with diff populated

    Returns:
        Partial state update dict with risk_analysis populated
    """
    from langchain_openai import AzureChatOpenAI

    model = AzureChatOpenAI(
        deployment_name="gpt-4.1-mini",
        temperature=0,
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2025-04-01-preview",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )

    system_prompt = """You are a senior software engineer specialising in code review and bug detection.

You will be given a git diff for a pull request. Your job is to:
1. Identify every method/function that was changed or is at risk due to nearby changes
2. Assign each a risk score from 0.0 (no risk) to 1.0 (almost certainly buggy)
3. Explain why each method is risky in one sentence
4. Write a two-sentence summary of the overall change

Return ONLY valid JSON matching this exact schema. No preamble, no markdown code fences.

{
  "risky_methods": [
    {
      "name": "<method name>",
      "file": "<file path>",
      "risk_score": <float 0.0-1.0>,
      "reason": "<one sentence>"
    }
  ],
  "summary": "<two sentences about the overall change>",
  "language": "<python or java>"
}"""

    user_message = f"""Language: {state.get("language", "")}
Bug description (if available): {state.get("bug_description", "")}

Git diff:
{state.get("diff", "")}"""

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
        risk_analysis = json.loads(response_text)
        return {"risk_analysis": risk_analysis}

    except (json.JSONDecodeError, Exception) as e:
        return {
            "risk_analysis": {
                "risky_methods": [{"name": "unknown", "file": "unknown", "risk_score": 0.5, "reason": "Unable to analyze"}],
                "summary": "Analysis failed",
                "language": state.get("language", "")
            }
        }
