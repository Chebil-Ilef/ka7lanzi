import asyncio
from core.managers.dataset_manager import DatasetManager
from core.managers.index_manager import IndexManager
from core.managers.feedback_manager import FeedbackManager
from core.utils.planner import Planner
from core.utils.executor import Executor
from core.utils.visualizer import Visualizer
from core.llm import LLM
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from config import EMBEDDING_MODEL, DATA_DIR, LLMODEL
from typing import Optional
import threading

class WorkflowAgent:
    def __init__(self, ):
        self.dataset_manager = DatasetManager()
        self.index_manager = None
        self.visualizer = None
        self.feedback = None
        self.llm = None
        self.planner = None
        
        self._init_started = False
        self._init_finished = False
        self._init_error: Optional[str] = None
        self._init_thread: Optional[threading.Thread] = None

    async def async_init(self, embeddings_model: HuggingFaceEmbedding = EMBEDDING_MODEL, llm_client: LLM = LLMODEL):
        self.index_manager = IndexManager(embeddings_model=embeddings_model)
        self.visualizer = Visualizer()
        self.feedback = FeedbackManager()
        self.llm = llm_client
        self.planner = Planner(self.llm)
        self._init_started = True

    def start_async_init(self, llm_client: LLM = LLMODEL):
        if not self._init_started:
            self._init_task = asyncio.create_task(self.async_init(llm_client))

    def is_ready(self):
        return self._init_finished

    def load_dataset(self, current_dataset_name: str):
        path = DATA_DIR / current_dataset_name
        df = self.dataset_manager.load(path)
        return df

    def build_index(self):
        df = self.dataset_manager.df
        if df is None:
            raise ValueError("No dataset loaded")
        self.index_manager.build_index(df)

    def ask(self, question: str):
        # --- State Validation ---
        if not self._init_finished:
            raise RuntimeError(
                "Agent is not initialized."
            )

        if self.dataset_manager.df is None:
            raise ValueError(
                "No dataset loaded."
            )

        if self.planner is None:
            raise RuntimeError("Planner is not initialized.")

        if self.llm is None:
            raise RuntimeError("LLM client is not initialized.")

        df = self.dataset_manager.df
        summary = self.dataset_manager.basic_stats_text()

        # --- Planning ---
        try:
            plan = self.planner.plan(question, summary, list(df.columns))
            if not plan or not isinstance(plan, dict):
                raise ValueError("Planner returned an invalid or empty plan.")
        except Exception as e:
            raise RuntimeError(f"Failed to generate a plan from the question: {e}") from e

        # --- Execution ---
        try:
            executor = Executor(df)
            exec_results = executor.execute(plan)
        except Exception as e:
            raise RuntimeError(f"Error executing the plan: {e}") from e

        figs = []
        textual_parts = []

        # --- Post-process results ---
        try:
            for r in exec_results:
                if r["type"] == "compute" and r["name"] == "correlation":
                    top = r.get("value")
                    if top is not None:
                        textual_parts.append(f"Top correlations:\n{top.to_string()}")
                        cols = [r["meta"]["target"]] + top.index.tolist()
                        figs.append(self.visualizer.heatmap(df, cols))

                elif r["type"] == "compute" and r["name"] == "groupby":
                    grp = r.get("value")
                    if grp is not None:
                        textual_parts.append(f"Groupby result:\n{grp.to_string(index=False)}")

                elif r["type"] == "visualize":
                    name = r.get("name")
                    params = r.get("params", {})
                    if name == "heatmap" and "columns" in params:
                        figs.append(self.visualizer.heatmap(df, params["columns"]))

                elif r["type"] == "answer":
                    context = "\n\n".join(textual_parts) if textual_parts else "No prior results."
                    try:
                        final_answer = self.llm.generate(
                            f"Using the following results:\n{context}\nAnswer: {question}"
                        )
                        textual_parts.append(final_answer)
                    except Exception as e:
                        textual_parts.append(f"[LLM Error: Failed to generate final answer: {e}]")

        except Exception as e:
            raise RuntimeError(f"Error during post-processing of execution results: {e}") from e

        # --- Final answer ---
        answer_text = "\n\n".join(textual_parts) if textual_parts else "No meaningful results produced."
        return {"answer": answer_text, "figs": figs, "plan": plan}