from typing import Optional, Type, List, Dict, Any
import pandas as pd
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from core.managers.dataset_manager import DatasetManager
from core.managers.index_manager import IndexManager

from core.interfaces.iplanner import IPlanner
from core.executor.executor import Executor
from core.interfaces.ivisualizer import IVisualizer

from core.executor.strategies.correlation import CorrelationStrategy
from core.executor.strategies.describe import DescribeStrategy
from core.executor.strategies.groupby import GroupByStrategy
from core.executor.strategies.topk import TopKStrategy
from core.executor.strategies.filter import FilterStrategy
from core.executor.strategies.timeseries import TimeSeriesAggregateStrategy

from core.llm import LLM
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
            executor: Executor,  
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
            self.executor: Executor = executor
            self.visualizer: IVisualizer = visualizer

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

    def format_results(self, results: List[Dict[str, Any]]):
        answer_texts = [] 
        figs = [] 
        for res in results: 
            if res["type"] == "answer": 
                answer_texts.append(res["text"]) 
            elif res["type"] == "visualize" and res.get("figure") is not None: 
                figs.append(res["figure"]) 
            elif res["type"] == "compute": 
                value = res.get("value")
                if isinstance(value, (dict, list)):
                    try:
                        df = pd.DataFrame(value)
                        if df.index.name is None and isinstance(value, dict): 
                            df = df.reset_index().rename(columns={"index": "key"}) 
                        figs.append(df)
                    except Exception:
                        answer_texts.append(str(value)) 
                else:
                    answer_texts.append(str(res["value"])) 
            elif res["type"] == "error": 
                answer_texts.append(res["message"]) 
        return { "answer": "\n\n".join(answer_texts).strip(), "figs": figs }

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
                "topk": TopKStrategy(),
                "filter": FilterStrategy(),
                "timeseries": TimeSeriesAggregateStrategy()
            }
            executor: Executor = self.executor(df, strategies, self.visualizer)
            exec_results = executor.execute(plan)
            return self.format_results(exec_results)
        except Exception as e:
            raise RuntimeError(f"Error executing the plan: {e}") from e
