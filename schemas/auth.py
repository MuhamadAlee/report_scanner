from pydantic import BaseModel
class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    is_super_user: bool