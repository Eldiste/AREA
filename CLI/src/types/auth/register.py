from pydantic import BaseModel, Field


class RegisterConfig(BaseModel):
    username: str = Field(..., description="The username of the user.")
    email: str = Field(..., description="The email address of the user.")
    password: str = Field(..., description="The password for the user account.")


class RegisterResponse(BaseModel):
    username: str
    email: str
    id: int
    is_active: bool
    is_admin: bool
