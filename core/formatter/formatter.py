import json
import pandas as pd
from typing import Any, Dict, List, Tuple
from matplotlib.figure import Figure
from core.visualizer.visualizer import Visualizer


class Formatter():
    def __init__(self, visualizer: Visualizer):
        self.visualizer = visualizer

    def format(self, results: List[Dict[str, Any]], df: pd.DataFrame) -> Tuple[str, List[str], List[Figure]]:
        """
        Convert Executor results into a textual summary and plots.
        """

        textual_parts: List[str] = []
        figs: List[Figure] = []

        for step in results:
            if step["type"] == "compute":
                name, val = step["name"], step["value"]
                if isinstance(val, dict):
                    textual_parts.append(f"[{name.upper()} RESULT]\n{json.dumps(val, indent=2)}")
                else:
                    textual_parts.append(f"[{name.upper()} RESULT]\n{val}")

            elif step["type"] == "answer":
                style = step.get("params", {}).get("style", "summary")
                textual_parts.append(f"[ANSWER style={style}]")

            elif step["type"] == "visualize":
                fig = self.visualizer.dispatch(df, step)
                if fig:
                    figs.append(fig)

            elif step["type"] == "error":
                textual_parts.append(f"[ERROR] {step.get('message')}")

        context = "\n\n".join(textual_parts)
        return context, textual_parts, figs