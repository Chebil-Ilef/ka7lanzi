import asyncio
from typing import Optional, Type
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from core.managers.dataset_manager import DatasetManager
from core.managers.index_manager import IndexManager

from core.interfaces.iplanner import IPlanner
from core.interfaces.iexecutor import IExecutor
from core.interfaces.ivisualizer import IVisualizer

from core.executor.strategies.correlation import CorrelationStrategy
from core.executor.strategies.describe import DescribeStrategy
from core.executor.strategies.groupby import GroupByStrategy

from core.llm import LLM
from core.formatter.formatter import Formatter

from core.prompts import executor_prompt
from config import EMBEDDING_MODEL, DATA_DIR, LLMODEL


class WorkflowAgent:
    def __init__(
        self,
    ):
        self.dataset_manager = DatasetManager()
        self.index_manager: Optional[IndexManager] = None
        self.llm: Optional[LLM] = None
        self.embeddings_model: Optional[HuggingFaceEmbedding] = None
        
        self._init_started = False
        self._init_finished = False
        self._init_error: Optional[str] = None

    async def async_init(
            self, 
            planner: IPlanner,
            executor: type[IExecutor],  
            visualizer: IVisualizer,
            embeddings_model: HuggingFaceEmbedding = EMBEDDING_MODEL, 
            llm_client: LLM = LLMODEL,
        ):
        """Initialisation asynchrone des composants lourds"""
        try:
            self._init_started = True

            self.index_manager = IndexManager(embeddings_model=embeddings_model)
            self.llm = llm_client

            self.planner: IPlanner = planner
            self.executor: Type[IExecutor] = executor
            self.visualizer: IVisualizer = visualizer
            self.formatter: Formatter = Formatter(self.visualizer)

            self._init_finished = True
        except Exception as e:
            self._init_error = str(e)
            self._init_finished = False
            raise

    def is_ready(self):
        return self._init_finished and self._init_error is None

    def load_dataset(self, current_dataset_name: str):
        path = DATA_DIR / current_dataset_name
        df = self.dataset_manager.load(path)
        self.dataset_manager.df = df
        return df

    def build_index(self):
        df = self.dataset_manager.df
        if df is None:
            raise ValueError("No dataset loaded")
        if self.index_manager is None:
            raise RuntimeError("IndexManager not initialized")
        self.index_manager.build_index(df)

    def ask(self, question: str):
        if not self._init_finished:
            raise RuntimeError("Agent is not initialized.")
        
        df = self.dataset_manager.df
        if df is None:
            raise ValueError("No dataset loaded.")

        try:
            plan = self.planner.plan(question, self.dataset_manager.basic_stats_text(), list(df.columns))
            if not plan or not isinstance(plan, dict):
                raise ValueError("Planner returned an invalid or empty plan.")
        except Exception as e:
            raise RuntimeError(f"Failed to generate a plan from the question: {e}") from e

        try:
            strategies = {
                "describe": DescribeStrategy(),
                "groupby": GroupByStrategy(),
                "correlation": CorrelationStrategy(),
            }
            executor: IExecutor = self.executor(df, strategies)
            exec_results = executor.execute(plan)
        except Exception as e:
            raise RuntimeError(f"Error executing the plan: {e}") from e

        try:
            
            context, textual_parts, figs = self.formatter.format(exec_results, df)
            try:
                final_answer = self.llm.generate(executor_prompt.format(context=context, question=question))
            except Exception as e:
                raise RuntimeError(f"[LLM Error: Failed to generate final answer: {e}]")

        except Exception as e:
            raise RuntimeError(f"Error during post-processing of execution results: {e}") from e

        return {"answer": final_answer, "figs": figs, "plan": plan}