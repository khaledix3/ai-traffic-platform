from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
    
class UserLogin(BaseModel):
    email: str
    password: str