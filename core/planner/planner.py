from typing import Dict
from core.llm import LLM
from core.planner.plan_parser import PlanParser
from core.interfaces.iplanner import IPlanner
from core.prompts import PLANNER_PROMPT
from config import LLMODEL

class Planner(IPlanner):
    def __init__(self, llm_client: LLM = LLMODEL):
        self.llm = llm_client

    def plan(self, question: str, dataset_summary: str, columns: list, context: str = None) -> Dict:

        prompt = PLANNER_PROMPT.format(
            question=question,
            summary=dataset_summary,
            columns=columns
        )

        if context:
            prompt += f"\n\n[Retrieved context from dataset]:\n{context}"
        
        try:
            raw = self.llm.generate([{"role": "user", "content": prompt}])
        except Exception as e:
            raise RuntimeError(f"[ERROR] Failed to generate output from LLM: {e}") from e

        return PlanParser.parse(raw=raw)