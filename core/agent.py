from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.core.evaluation import FaithfulnessEvaluator
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
from pathlib import Path
from config import LLMODEL, EMBEDDING_MODEL


class DatasetAgent:
    def __init__(self, dataset_path: str, collection_name: str = "quickstart"):
        self.dataset_path = Path(dataset_path)
        self.collection_name = collection_name
        self.reader = None
        self.index = None
        self.vector_store = None

        if not self.dataset_path.exists():
            raise FileNotFoundError(f"Le dossier '{dataset_path}' n'existe pas !")
        else:
            self.reader = SimpleDirectoryReader(input_dir=str(self.dataset_path))

    def build_index(self):
        """
        Crée l'index LlamaIndex (vector embeddings) à partir du dataset
        """
        try:
            documents = self.reader.load_data()
            if not documents:
                raise ValueError("Aucun document trouvé dans le dataset !")

            db_path = Path("embeddings").resolve()
            db = chromadb.PersistentClient(path=str(db_path))
            try:
                chroma_collection = db.get_collection(self.collection_name)
            except Exception:
                chroma_collection = db.create_collection(self.collection_name)

            self.vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
            storage_context = StorageContext.from_defaults(vector_store=self.vector_store)

            self.index = VectorStoreIndex.from_documents(
                documents, storage_context=storage_context, embed_model=EMBEDDING_MODEL
            )
            print("✅ Index créé avec succès !")
        except Exception as e:
            print(f"⚠️ Erreur lors de la création de l'index : {e}")

    def query(self, question: str):
        """
        Pose une question sur le dataset via le LLM
        """
        if not self.index:
            raise ValueError("Index non créé. Veuillez appeler build_index() d'abord.")

        try:
            query_engine = self.index.as_query_engine(
                llm=LLMODEL
            )
            response = query_engine.query(question)
            evaluator = FaithfulnessEvaluator(llm=LLMODEL)
            eval_result = evaluator.evaluate_response(response=response)
            print("Evaluation "+eval_result.passing)
            return str(response)
        except Exception as e:
            print(f"⚠️ Erreur lors de la requête : {e}")
            return None