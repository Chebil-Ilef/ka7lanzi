# core/prompts.py
"""
Planner prompt templates for the WorkflowAgent planner.

The planner MUST return valid JSON only (no surrounding text).
JSON schema:
{
  "actions": [
    {
      "action": "compute" | "visualize" | "answer",
      "name": "<operation_name>",
      "params": { ... }
    },
    ...
  ]
}

Supported compute operations (examples):
 - correlation: params {"target": "<col>", "top_n": int}
 - groupby: params {"by": "<col>", "agg": "mean"|"sum"|"count"|"median", "target": "<col (optional)>"}
 - filter: params {"expr": "<pandas-like expression>"}
 - describe: params {"columns": ["col1", "col2", ...]}
 - topk: params {"column": "<col>", "k": int}
 - timeseries_aggregate: params {"date_column": "<col>", "value_column": "<col>", "freq": "D|W|M", "agg": "sum|mean"}

Supported visualizations (examples):
 - heatmap: params {"columns": ["c1","c2",...]}
 - boxplot: params {"column": "<col>", "by": "<col (optional)>"}
 - scatter: params {"x": "<col>", "y": "<col>"}
 - histogram: params {"column": "<col>", "bins": int}
 - timeseries: params {"date_column": "<col>", "value_column": "<col>"}

RESTRICTIONS:
 - Output MUST be strictly valid JSON (no explanatory text).
 - Use only the actions and params shown in examples below.
 - Every plan MUST end with an "answer" action to instruct the final LLM-produced text form.

Below are helpful examples. The planner should follow these styles and return only JSON.
"""

PLANNER_INSTRUCTIONS = """
You are a planner that receives:
 - QUESTION: a user's question (in French or English)
 - SUMMARY: a short dataset summary
 - COLUMNS: a list of column names

Return strictly valid JSON only. The JSON must have one top-level key "actions" whose value is a list of steps.
Each step must be one of:
 - compute (name: correlation, groupby, filter, describe, topk, timeseries_aggregate)
 - visualize (name: heatmap, boxplot, scatter, histogram, timeseries)
 - answer (no name; params: {"style":"short"|"detailed"})

Do not include any commentary. Example outputs follow.
"""

# 5 examples to reduce hallucination / enforce format
EXAMPLES = [
    # Example 1: correlation + heatmap + answer
    {
        "question": "Quelle est la colonne ayant la plus forte corrélation avec 'sales' ?",
        "summary": "Dataset with 10000 rows and columns: sales (float), advertising (float), price (float), region (category).",
        "columns": ["sales", "advertising", "price", "region"],
        "json": {
            "actions": [
                {"action": "compute", "name": "correlation", "params": {"target": "sales", "top_n": 3}},
                {"action": "visualize", "name": "heatmap", "params": {"columns": ["sales", "advertising", "price"]}},
                {"action": "answer", "params": {"style": "short"}}
            ]
        }
    },

    # Example 2: groupby + boxplot + answer
    {
        "question": "Donne la distribution de 'salary' par 'department' et montre la boxplot.",
        "summary": "Dataset with 2000 rows and columns: salary (float), department (category), employee_id (int).",
        "columns": ["salary", "department", "employee_id"],
        "json": {
            "actions": [
                {"action": "compute", "name": "groupby", "params": {"by": "department", "agg": "median", "target": "salary"}},
                {"action": "visualize", "name": "boxplot", "params": {"column": "salary", "by": "department"}},
                {"action": "answer", "params": {"style": "detailed"}}
            ]
        }
    },

    # Example 3: filter + histogram + answer
    {
        "question": "Parmi les transactions après 2024-01-01, quelle est la distribution des montants ('amount') ?",
        "summary": "Dataset with columns: date (datetime), amount (float), user_id (int).",
        "columns": ["date", "amount", "user_id"],
        "json": {
            "actions": [
                {"action": "compute", "name": "filter", "params": {"expr": "date >= '2024-01-01'"}},
                {"action": "visualize", "name": "histogram", "params": {"column": "amount", "bins": 40}},
                {"action": "answer", "params": {"style": "short"}}
            ]
        }
    },

    # Example 4: timeseries_aggregate + timeseries plot + answer
    {
        "question": "Montre la série temporelle mensuelle des ventes totales (col 'sales')",
        "summary": "Dataset with columns: order_date (datetime), sales (float), store (category).",
        "columns": ["order_date", "sales", "store"],
        "json": {
            "actions": [
                {"action": "compute", "name": "timeseries_aggregate", "params": {"date_column": "order_date", "value_column": "sales", "freq": "M", "agg": "sum"}},
                {"action": "visualize", "name": "timeseries", "params": {"date_column": "order_date", "value_column": "sales"}},
                {"action": "answer", "params": {"style": "detailed"}}
            ]
        }
    },

    # Example 5: topk + scatter + answer
    {
        "question": "Quelles sont les 5 villes avec le plus grand nombre d'utilisateurs et montrer un scatter entre population et avg_session?",
        "summary": "Dataset with columns: city (str), users_count (int), population (int), avg_session (float).",
        "columns": ["city", "users_count", "population", "avg_session"],
        "json": {
            "actions": [
                {"action": "compute", "name": "topk", "params": {"column": "users_count", "k": 5}},
                {"action": "visualize", "name": "scatter", "params": {"x": "population", "y": "avg_session"}},
                {"action": "answer", "params": {"style": "short"}}
            ]
        }
    }
]

def build_planner_prompt(question: str, summary: str, columns: list) -> str:
    """
    Construct the planner prompt to send to the LLM.
    The LLM is expected to return ONLY the JSON plan as shown.
    """
    prompt_parts = [PLANNER_INSTRUCTIONS.strip()]
    prompt_parts.append("\n---\nEXAMPLES (JSON only):\n")
    for ex in EXAMPLES:
        # show the input and the correct JSON for few-shot
        prompt_parts.append(f"QUESTION: {ex['question']}")
        prompt_parts.append(f"SUMMARY: {ex['summary']}")
        prompt_parts.append(f"COLUMNS: {ex['columns']}")
        # the JSON example must be serialized compactly
        import json
        prompt_parts.append("EXPECTED_JSON:")
        prompt_parts.append(json.dumps(ex['json'], ensure_ascii=False))
        prompt_parts.append("---")
    # final task
    prompt_parts.append(f"QUESTION: {question}")
    prompt_parts.append(f"SUMMARY: {summary}")
    prompt_parts.append(f"COLUMNS: {columns}")
    prompt_parts.append("\nReturn STRICT JSON only (no surrounding text).")
    return "\n".join(prompt_parts)