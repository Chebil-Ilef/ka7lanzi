from core.managers.dataset_manager import DatasetManager
from core.managers.index_manager import IndexManager
from core.managers.feedback_manager import FeedbackManager
from core.utils.planner import Planner
from core.utils.executor import Executor
from core.utils.visualizer import Visualizer
from core.llm import LLM
from config import EMBEDDING_MODEL

class WorkflowAgent:
    def __init__(self, embeddings_model=EMBEDDING_MODEL, llm_client: LLM = None):
        self.dataset_manager = DatasetManager()
        self.index_manager = IndexManager(embeddings_model=embeddings_model)
        self.visualizer = Visualizer()
        self.feedback = FeedbackManager()
        self.llm = llm_client or LLM()
        self.planner = Planner(self.llm)

    def load_dataset(self, path: str):
        df = self.dataset_manager.load(path)
        return df

    def build_index(self):
        df = self.dataset_manager.df
        if df is None:
            raise ValueError("No dataset loaded")
        self.index_manager.build_index(df)

    def ask(self, question: str):
        df = self.dataset_manager.df
        summary = self.dataset_manager.basic_stats_text()
        plan = self.planner.plan(question, summary, list(df.columns))
        executor = Executor(df)
        exec_results = executor.execute(plan)
        figs = []
        textual_parts = []
        # post-process executor results: create figs and text
        for r in exec_results:
            if r["type"] == "compute" and r["name"] == "correlation":
                top = r["value"]
                textual_parts.append(f"Top correlations:\n{top.to_string()}")
                # pick columns for heatmap
                cols = [r["meta"]["target"]] + top.index.tolist()
                figs.append(self.visualizer.heatmap(df, cols))
            elif r["type"] == "visualize":
                name = r["name"]
                params = r["params"]
                if name == "heatmap":
                    figs.append(self.visualizer.heatmap(df, params["columns"]))
                # add other visualizations...
            elif r["type"] == "answer":
                # ask llm to craft final answer using compute results
                context = "\n\n".join(textual_parts)
                final = self.llm.generate(f"Using the following results:\n{context}\nAnswer: {question}")
                textual_parts.append(final)
        answer_text = "\n\n".join(textual_parts)
        return {"answer": answer_text, "figs": figs, "plan": plan}