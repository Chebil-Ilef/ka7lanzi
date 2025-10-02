import asyncio
import threading
import time
import traceback
from typing import Optional

from core.agent import WorkflowAgent


class Init:
    """Manages WorkflowAgent state, initialization, and queries."""

    def __init__(self):
        self.agent: WorkflowAgent = WorkflowAgent()
        self._init_thread: Optional[threading.Thread] = None

    def start_agent_init(self):
        """Start agent initialization in a background thread."""
        if getattr(self.agent, "_init_started", False):
            return

        def target():
            try:
                asyncio.run(self.agent.async_init())
            except Exception:
                self.agent._init_error = traceback.format_exc()
            finally:
                self.agent._init_finished = True

        self.agent._init_started = True
        self._init_thread = threading.Thread(target=target, daemon=True)
        self._init_thread.start()

    def wait_for_agent_ready(self):
        """Block until agent is ready, returning error if failed."""
        while not self.agent.is_ready() and not getattr(self.agent, "_init_finished", False):
            time.sleep(0.2)

        if getattr(self.agent, "_init_error", None):
            raise RuntimeError(self.agent._init_error)

    def load_dataset(self, dataset_path: str):
        df = self.agent.load_dataset(dataset_path)
        return df

    def ask(self, query: str):
        return self.agent.ask(query)