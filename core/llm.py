from llama_cpp import Llama
from threading import Lock

class LLM:
    """Singleton pour gérer un LLM"""

    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    from config import MODEL_PATH
                    cls._instance = super(LLM, cls).__new__(cls)

                    cls._instance.llm = Llama(
                        model_path=str(MODEL_PATH),
                        n_threads=8,           
                        n_gpu_layers=1,        # 0 for CPU only, 1 couche sur GPU
                        use_mmap=True,
                        use_mlock=True
                    )
        return cls._instance

    def get_llm(self):
        """Retourne l’instance unique du LLM"""
        return self.llm