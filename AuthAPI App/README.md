# 🔐 AuthAPI – Säker inloggning med JWT och 2FA

Detta projekt är en säker backend-API byggd med FastAPI, som erbjuder:
- Registrering och inloggning med JWT
- Valbar 2FA med QR-kod (kompatibel med Google Authenticator)
- Testtäckning med Pytest
- Dockerstöd

## 🚀 Starta lokalt
```bash
uvicorn app.main:app --reload
```

## 🐳 Starta med Docker
```bash
docker-compose up --build
```

## 🧪 Testning
```bash
pytest tests/
```

## 📸 Aktivera 2FA med QR-kod (HTML)
GET /enable-2fa-html?email=example@email.com
