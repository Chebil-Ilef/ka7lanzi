from typing import Dict
import json


class PlanParser:
    @staticmethod
    def parse(raw: str) -> Dict:
        import re
        print("RAW HERE/", raw)
        cleaned = re.sub(r'```(?:json)?\s*', '', raw)
        cleaned = re.sub(r'\s*```', '', cleaned)
        cleaned = cleaned.strip()
        cleaned = cleaned.replace('{{', '{').replace('}}', '}')
        print("CLEANED HERE/", cleaned)
        try:
            plan_json = json.loads(cleaned)
        except json.JSONDecodeError:
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