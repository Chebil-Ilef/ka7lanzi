from threading import Lock
import os


class LLM:

    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    # Lazy import to avoid circular imports (config.py imports LLM)
                    openai_api_key = os.getenv("OPENAI_API_KEY")
                    openai_api_base = os.getenv("OPENAI_API_BASE")
                    # Default to a small open model that vLLM can start quickly
                    openai_model = os.getenv("OPENAI_MODEL", "facebook/opt-125m")

                    try:
                        import openai
                    except Exception as e:
                        raise RuntimeError(
                            "The 'openai' package is required for LLM but is not installed."
                        ) from e

                    # Configure API base (for local vLLM OpenAI-compatible server)
                    if openai_api_base:
                        openai.api_base = openai_api_base

                    if openai_api_key:
                        # prefer explicit API key from env (still accepted by vLLM if set)
                        openai.api_key = openai_api_key

                    cls._instance = super().__new__(cls)
                    cls._instance.client = openai
                    cls._instance.model_name = openai_model
        return cls._instance

    def get_client(self):
        return self.client

    def generate(self, messages: list | str) -> str:

        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]

        # Ensure messages are in expected shape for OpenAI SDK
        payload_messages = []
        for m in messages:
            role = m.get("role") if isinstance(m, dict) else None
            content = m.get("content") if isinstance(m, dict) else str(m)
            if role not in {"system", "user", "assistant"}:
                # default to user if role missing/invalid
                role = "user"
            payload_messages.append({"role": role, "content": content})

        temperature = 0.7
        top_p = 0.95
        max_tokens = 1024

        try:
            with self._lock:
                # Use ChatCompletion for widest compatibility
                resp = self.client.ChatCompletion.create(
                    model=self.model_name,
                    messages=payload_messages,
                    temperature=temperature,
                    top_p=top_p,
                    max_tokens=max_tokens,
                    n=1,
                )

                choice = resp["choices"][0]
                if "message" in choice:
                    generated_text = choice["message"].get("content", "").strip()
                else:
                    generated_text = choice.get("text", "").strip()

                return generated_text
        except Exception as e:
            print(f"Erreur lors de la génération: {e}")
            return f"Erreur: {str(e)}"