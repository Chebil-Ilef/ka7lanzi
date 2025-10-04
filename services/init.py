import asyncio
from typing import Optional, Type, Any
from core.llm import LLM

from core.agent.agent import WorkflowAgent

from core.planner.planner import Planner
from core.executor.executor import Executor
from core.visualizer.visualizer import Visualizer

from config import EMBEDDING_MODEL, LLMODEL


class Init:
    """Manages WorkflowAgent state, initialization, and queries."""

    def __init__(self):
        self.agent: WorkflowAgent = WorkflowAgent()
        self._init_error: Optional[str] = None
        self._init_task: Optional[asyncio.Task] = None
        self._init_lock = asyncio.Lock()

    async def start_agent_init_async(
        self,
        planner: Optional[Planner] = Planner(llm_client=LLMODEL),
        executor: Optional[Type[Executor]] = Executor,
        visualizer: Optional[Visualizer] = Visualizer(),
        embeddings_model: Any = EMBEDDING_MODEL, 
        llm_client: LLM = LLMODEL
    ):
        async with self._init_lock:
            if self.agent.is_ready():
                return 
            try:
                await self.agent.async_init(
                    planner=planner,
                    executor= executor,
                    visualizer=visualizer,
                    llm_client=llm_client, 
                    embeddings_model=embeddings_model
                    )
            except Exception as e:
                self._init_error = str(e)

    def start_agent_init(self):
        if self._init_task is not None and not self._init_task.done():
            return
        if self._init_error:
            return
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self.start_agent_init_async())
            finally:
                loop.close()
        except Exception as e:
            self._init_error = str(e)
            raise

    def is_ready(self) -> bool:
        return self.agent.is_ready()

    def load_dataset(self, dataset_path: str):
        return self.agent.load_dataset(dataset_path)

    def ask(self, query: str):
        return self.agent.ask(query)