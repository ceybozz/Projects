from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import os, pyotp, qrcode, io, base64
from . import models, schemas
from .database import SessionLocal

SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/register", response_model=schemas.Token)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pw = pwd_context.hash(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    token = create_access_token(data={"sub": new_user.email})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/login", response_model=schemas.Token)
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not pwd_context.verify(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if db_user.twofa_secret:
        if not user.twofa_code:
            raise HTTPException(status_code=403, detail="2FA code required")
        totp = pyotp.TOTP(db_user.twofa_secret)
        if not totp.verify(user.twofa_code):
            raise HTTPException(status_code=403, detail="Invalid 2FA code")
    token = create_access_token(data={"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/enable-2fa", response_model=schemas.TwoFAResponse)
def enable_2fa(email: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    secret = pyotp.random_base32()
    user.twofa_secret = secret
    db.commit()
    otp_auth_url = pyotp.totp.TOTP(secret).provisioning_uri(name=email, issuer_name="AuthAPI")
    return {"otp_auth_url": otp_auth_url}

@router.get("/enable-2fa-html", response_class=HTMLResponse)
def enable_2fa_html(email: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    secret = pyotp.random_base32()
    user.twofa_secret = secret
    db.commit()
    otp_auth_url = pyotp.totp.TOTP(secret).provisioning_uri(name=email, issuer_name="AuthAPI")
    qr = qrcode.make(otp_auth_url)
    img_byte_arr = io.BytesIO()
    qr.save(img_byte_arr, format='PNG')
    img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode()
    html = f"""
    <html>
      <body>
        <h2>Skanna QR-koden i din autentiseringsapp</h2>
        <img src='data:image/png;base64,{img_base64}' />
        <p>eller använd denna länk: <code>{otp_auth_url}</code></p>
      </body>
    </html>
    """
    return HTMLResponse(content=html)
