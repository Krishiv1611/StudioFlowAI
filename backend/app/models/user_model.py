from sqlalchemy import Column,Integer,String
from sqlalchemy.orm import relationship
from app.config.database import Base
class User(Base):
    __tablename__="users"
    id=Column(Integer,primary_key=True,index=True)
    email=Column(String,unique=True,index=True,nullable=False)
    full_name=Column(String,nullable=False)
    hashed_password=Column(String,nullable=False)
    brand_voice_style=Column(String,nullable=False)
    knowledge_vault=relationship("KnowledgeVault",back_populates="user")
    projects=relationship("Project",back_populates="user")
    social_accounts=relationship("SocialAccount",back_populates="user")
    