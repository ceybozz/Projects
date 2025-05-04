from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    twofa_code: str | None = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TwoFAResponse(BaseModel):
    otp_auth_url: str
