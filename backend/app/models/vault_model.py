from sqlalchemy import Column,Integer,String,ForeignKey
from app.config.database import Base
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
class KnowledgeVault(Base):
    __tablename__="knowledge_vault"
    id=Column(Integer,primary_key=True,index=True)
    user_id=Column(Integer,ForeignKey("users.id"),nullable=False)
    content_chunk=Column(String,nullable=False)
    embedding=Column(Vector(384),nullable=False)
    
    user = relationship("app.models.user_model.User", back_populates="knowledge_vault")