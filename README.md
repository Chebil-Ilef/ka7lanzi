# analyste
Agent d’exploration interactive de dataset

```
Streamlit UI
   ↓
WorkflowAgent  (orchestrator)
   ├─ DatasetManager       # load/cast/clean/cached pandas.DataFrame + summary
   ├─ IndexManager         # create / update vector index (LlamaIndex + Chroma)
   ├─ Planner              # LLM -> structured plan (JSON) of compute/visualize/answer steps
   ├─ Executor             # performs compute steps on DataFrame (corr, agg, filter...)
   ├─ Visualizer           # creates matplotlib/plotly figures (returned to UI)
   ├─ LLMMediator (llm.py) # wrapper for local model (qwen2.5.gguf)
   └─ FeedbackManager      # store feedback, apply correction to docs/index (or queue)
```