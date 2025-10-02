from llama_index.core import Document, VectorStoreIndex, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
from config import EMBEDDING_MODEL, EMBEDDINGS_PATH

class IndexManager:
    def __init__(self, collection_name="quickstart", embeddings_model=EMBEDDING_MODEL):
        self.embeddings_model = embeddings_model
        self.collection_name = collection_name
        self.db = chromadb.PersistentClient(path=str(EMBEDDINGS_PATH.resolve()))
        try:
            self.collection = self.db.get_collection(collection_name)
        except Exception:
            self.collection = self.db.create_collection(collection_name)
        self.vector_store = ChromaVectorStore(chroma_collection=self.collection)
        self.index = None

    def _df_to_documents(self, df):
        """
        Convert dataframe columns into a list of llama_index.Document to be indexed.
        Each doc corresponds to a column with basic stats and a small sample.
        """
        docs = []
        for col in df.columns:
            s = df[col]
            
            text = (
                f"Column: {col}\n"
                f"Type: {s.dtype}\n"
                f"N_missing: {int(s.isna().sum())}\n"
                f"Sample: {s.dropna().head(10).tolist()}\n"
                f"Stats:\n{s.describe(include='all').to_string()}"
            )
            docs.append(Document(text=text, extra_info={"column": col}))
        # top-level dataset doc
        docs.append(Document(text=f"Dataset summary: {len(df)} rows, {len(df.columns)} columns"))
        return docs

    def build_index(self, df):
        docs = self._df_to_documents(df)
        storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        self.index = VectorStoreIndex.from_documents(docs, storage_context=storage_context, embed_model=self.embeddings_model)
        return self.index

    def add_feedback_doc(self, text: str, metadata: dict):
        """
        Add a user correction as a new document in the index.
        Relies on LlamaIndex to handle embeddings & vector store updates.
        """
        if not self.index:
            raise RuntimeError("Index has not been built yet. Build index before adding feedback.")

        doc = Document(text=text, extra_info=metadata or {"source": "user_feedback"})
        self.index.insert(doc)
        return doc