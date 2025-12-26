from pydantic import BaseModel, EmailStr

class UserSignup(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    brand_voice_style: str = "Professional"

class Token(BaseModel):
    access_token: str
    token_type: str
