import json
from typing import Dict
from core.llm import LLM
from core.prompts import build_planner_prompt

class Planner:
    def __init__(self, llm_client: LLM):
        self.llm = llm_client

    def plan(self, question: str, dataset_summary: str, columns: list) -> Dict:
        prompt =build_planner_prompt(question=question, summary=dataset_summary, columns=columns)
        raw = self.llm.generate(prompt)
        # enforce JSON parse; if LLM returns non-json try to extract first JSON object
        try:
            plan = json.loads(raw)
            return plan
        except Exception:
            # try to find first {...}
            import re
            m = re.search(r"\{.*\}", raw, re.DOTALL)
            if m:
                return json.loads(m.group(0))
            raise