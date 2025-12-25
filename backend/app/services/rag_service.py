from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlmodel import Session, select
from app.models.vault_model import KnowledgeVault
class RagService:
    def __init__(self):
        self.model=SentenceTransformer("all-MiniLM-L6-v2")
        self.text_splitter=RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            is_separator_regex=False
        )
    def split_text(self,text):
        return self.text_splitter.split_text(text)
    def _get_embeddings(self,texts):
        return self.model.encode(texts).tolist()

    def store_content(self, db: Session, user_id: int, content: str):
        chunks = self.split_text(content)
        embeddings = self._get_embeddings(chunks)
        
        vault_entries = [
            KnowledgeVault(
                user_id=user_id,
                content_chunk=chunk,
                embedding=embedding
            )
            for chunk, embedding in zip(chunks, embeddings)
        ]
        
        db.add_all(vault_entries)
        db.commit()

    def search_vault(self, db: Session, user_id: int, query: str, limit: int = 5):
        query_embedding = self._get_embeddings(query)
        
        # Using pgvector's l2_distance
        results = db.exec(
            select(KnowledgeVault)
            .where(KnowledgeVault.user_id == user_id)
            .order_by(KnowledgeVault.embedding.l2_distance(query_embedding))
            .limit(limit)
        ).all()
        
        return results