import json
import pandas as pd
from typing import Dict, List
from core.llm import LLM
from core.prompts import planner_prompt

class Planner:
    def __init__(self, llm_client: LLM, df: pd.DataFrame = None):
        self.llm = llm_client
        self.df = df

    def plan(self, question: str, dataset_summary: str, columns: list) -> Dict:

        prompt = planner_prompt.format(
            question=question,
            summary=dataset_summary,
            columns=columns
        )
        
        try:
            raw = self.llm.generate([{"role": "user", "content": prompt}])
            # print("\n[DEBUG] LLM RAW OUTPUT:")
            # print(raw)
        except Exception as e:
            raise RuntimeError(f"[ERROR] Failed to generate output from LLM: {e}") from e

        try:
            plan_json = json.loads(raw)
        except json.JSONDecodeError:
            import re
            match = re.search(r'(\{.*\}|\[.*\])', raw, re.DOTALL)
            if not match:
                raise ValueError(f"[ERROR] No JSON array detected in LLM output:\n{raw}")
            try:
                plan_json = json.loads(match.group(0))
            except json.JSONDecodeError as e:
                raise ValueError(f"[ERROR] Failed to parse JSON from LLM output:\n{raw}\n{e}") from e

        if isinstance(plan_json, list):
            plan = {"actions": plan_json}
        elif isinstance(plan_json, dict) and "actions" in plan_json:
            plan = plan_json
        else:
            raise ValueError(f"[ERROR] Parsed JSON is invalid or missing 'actions':\n{plan_json}")

        print("\n[DEBUG] PLAN OUTPUT:", plan)
        return plan