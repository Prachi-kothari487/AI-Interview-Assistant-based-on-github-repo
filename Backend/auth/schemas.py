from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):

    name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Name cannot be empty")

        if not value.replace(" ", "").isalpha():
            raise ValueError("Name should contain only letters")

        return value


class LoginRequest(BaseModel):

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)