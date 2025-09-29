import json

PLANNER_INSTRUCTIONS = """
You are a strict planner that receives:
 - QUESTION: a user's question (in French or English)
 - SUMMARY: a short dataset summary
 - COLUMNS: a list of column names

Return strictly valid JSON only. The JSON must have one top-level key "actions" whose value is a list of steps.
Each step must be one of:
 - compute (name: correlation, groupby, filter, describe, topk, timeseries_aggregate)
 - visualize (name: heatmap, boxplot, scatter, histogram, timeseries)
 - answer (no name; params: {"style":"short"|"detailed"})

Do not include any commentary or extra text.
"""

EXAMPLES = [
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
    }
]

def build_planner_prompt(question: str, summary: str, columns: list) -> list:
    """
    Returns a list of chat messages (ChatML format) for Qwen.
    """
    messages = [
        {"role": "system", "content": PLANNER_INSTRUCTIONS.strip()}
    ]

    for ex in EXAMPLES:
        # include few-shot examples
        messages.append({
            "role": "user",
            "content": f"QUESTION: {ex['question']}\nSUMMARY: {ex['summary']}\nCOLUMNS: {ex['columns']}"
        })
        messages.append({
            "role": "assistant",
            "content": json.dumps(ex["json"], ensure_ascii=False)
        })

    # final task
    messages.append({
        "role": "user",
        "content": f"QUESTION: {question}\nSUMMARY: {summary}\nCOLUMNS: {columns}\nReturn STRICT JSON only."
    })

    return messages