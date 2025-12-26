from pydantic import BaseModel

class VaultItem(BaseModel):
    content: str
    
class SearchQuery(BaseModel):
    query: str
    limit: int = 5
