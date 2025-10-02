import asyncio
from core.managers.dataset_manager import DatasetManager
from core.managers.index_manager import IndexManager
from core.managers.feedback_manager import FeedbackManager
from core.utils.planner import Planner
from core.utils.executor import Executor
from core.utils.visualizer import Visualizer
from core.prompts import executor_prompt
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
        self.planner = Planner(self.llm, self.dataset_manager.df)
        self._init_started = True

    def start_async_init(self, llm_client: LLM = LLMODEL):
        if not self._init_started:
            self._init_task = asyncio.create_task(self.async_init(llm_client))

    def is_ready(self):
        return self._init_finished

    def load_dataset(self, current_dataset_name: str):
        path = DATA_DIR / current_dataset_name
        df = self.dataset_manager.load(path)
        self.dataset_manager.df = df
        return df

    def build_index(self):
        df = self.dataset_manager.df
        if df is None:
            raise ValueError("No dataset loaded")
        self.index_manager.build_index(df)

    def ask(self, question: str):
        # --- State Validation ---
        if not self._init_finished:
            raise RuntimeError("Agent is not initialized.")

        if self.dataset_manager.df is None:
            raise ValueError("No dataset loaded.")

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

        # --- Post-process results ---
        try:
            
            context, textual_parts, figs = executor.render_results(exec_results)
            try:
                final_answer = self.llm.generate(executor_prompt.format(context=context, question=question))
            except Exception as e:
                raise RuntimeError(f"[LLM Error: Failed to generate final answer: {e}]")

        except Exception as e:
            raise RuntimeError(f"Error during post-processing of execution results: {e}") from e

        # --- Final answer ---
        answer_text = final_answer if final_answer else "No meaningful results produced."
        return {"answer": answer_text, "figs": figs, "plan": plan}