import json, re
from typing import Dict
from core.llm import LLM
from core.prompts import build_planner_prompt

class Planner:
    def __init__(self, llm_client: LLM):
        self.llm = llm_client

    def plan(self, question: str, dataset_summary: str, columns: list) -> Dict:
        """
        Generate a structured plan (JSON) for a given question and dataset.

        Steps:
        1. Build a prompt for the planner.
        2. Call the LLM to get raw text output.
        3. Try to parse JSON from output. If LLM adds extra text, extract first {...}.
        """
        prompt_text = build_planner_prompt(question, dataset_summary, columns)
        messages = [
            {"role": "system", "content": "You are a strict planner. Return ONLY valid JSON."},
            {"role": "user", "content": prompt_text}
        ]

        raw = self.llm.generate(messages)
        print("LLM RAW OUTPUT:")
        print(raw)

        plan_str = None
        if isinstance(raw, list):
            # e.g., [{"role":"assistant", "content": "..."}]
            for msg in raw:
                if msg.get("role") == "assistant" and "content" in msg:
                    plan_str = msg["content"]
                    break
        elif isinstance(raw, str):
            plan_str = raw

        if plan_str is None:
            raise ValueError("LLM output does not contain assistant content.")

        try:
            plan = json.loads(plan_str)
            return plan
        except json.JSONDecodeError:
            # fallback: try to extract first {...} block
            match = re.search(r"\{.*\}", plan_str, re.DOTALL)
            if match:
                try:
                    plan = json.loads(match.group(0))
                    return plan
                except json.JSONDecodeError:
                    raise ValueError(f"LLM output contains invalid JSON:\n{plan_str}")
            else:
                raise ValueError(f"LLM output does not contain JSON:\n{plan_str}")