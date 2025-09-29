from threading import Lock
from llama_cpp import Llama

class LLM:
    """Singleton for Qwen LLM with chat support"""

    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    from config import MODEL_PATH

                    NB_THREADS = 8
                    NB_GPU_LAYERS = 1
                    NB_CTX = 1024

                    cls._instance = super().__new__(cls)
                    cls._instance.llm = Llama(
                        model_path=str(MODEL_PATH),
                        n_threads=NB_THREADS,
                        n_gpu_layers=NB_GPU_LAYERS,
                        n_ctx=NB_CTX,
                        use_mmap=True,
                        use_mlock=True
                    )
        return cls._instance

    def get_llm(self):
        return self.llm

    def generate(self, messages: list) -> str:
        """
        Generate text from a list of chat messages.
        Each message should be a dict: {"role": "system|user|assistant", "content": str}
        """
        chat_prompt = ""
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            chat_prompt += f"<|im_start|>{role}\n{content}<|im_end|>\n"

        MODEL_TEMPERATURE = 0.7
        TOP_P = 0.95
        LLM_MAX_TOKENS = 1024
        REPEAT_PENALTY = 1.1

        try:
            with self._lock:
                response = self.llm(
                    chat_prompt,
                    max_tokens=LLM_MAX_TOKENS,
                    temperature=MODEL_TEMPERATURE,
                    top_p=TOP_P,
                    repeat_penalty=REPEAT_PENALTY,
                    stop=["</s>", "\n\n"],
                    echo=False
                )
                generated_text = response['choices'][0]['text'].strip()
                return generated_text
        except Exception as e:
            print(f"Erreur lors de la génération: {e}")
            return f"Erreur: {str(e)}"