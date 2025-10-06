from core.managers.index_manager import IndexManager


class Retriever:
    def __init__(self, index_manager: IndexManager) -> str:
        self.index_manager = index_manager

    def retrieve(self, query: str, top_k: int = 3) -> str:
        """Return relevant context from dataset."""
        if not self.index_manager or not self.index_manager.index:
            return ""
        try:
            query_engine = self.index_manager.index.as_query_engine(similarity_top_k=top_k)
            response = query_engine.query(query)
            return str(response)
        except Exception:
            return "[Retriever: failed to fetch relevant context]"