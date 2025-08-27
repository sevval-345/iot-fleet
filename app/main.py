# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy import text

from app.core.config import settings
from app.core.db import ENGINE
from app.api import routes_fleet, routes_usage, routes_actions, routes_whatif
from app.models.repo import repo


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Uygulama açılırken hafıza önbelleğini doldur (DB varsa).
    try:
        repo.reload_if_stale(force=True)
    except Exception:
        # DB opsiyonel; hata olsa bile ayakta kalsın.
        pass
    yield


app = FastAPI(title="IoT SIM Fleet (Modular)", lifespan=lifespan)

# 🔧 CORS: .env içindeki virgüllü ALLOW_ORIGINS'i listeye çevir
origins = [o.strip() for o in settings.ALLOW_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # ← DÜZELTİLDİ
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basit kök ve sağlık kontrolü
@app.get("/", include_in_schema=False)
def home():
    return {
        "ok": True,
        "docs": "/docs",
        "origins": origins,
        "endpoints": ["/api/health", "/api/fleet", "/api/usage/{sim_id}", "POST /api/actions"],
    }

@app.get("/api/health")
def health():
    try:
        with ENGINE.begin() as c:
            n = c.execute(text("SELECT COUNT(*) FROM dbo.sims")).scalar()
        return {"ok": True, "sims": int(n)}
    except Exception as e:
        # DB yoksa da 200 dön, UI bozulmasın
        return {"ok": True, "note": "DB erişimi isteğe bağlı", "error": str(e)}


# Router'ları dahil et
app.include_router(routes_fleet.router, prefix="/api")
app.include_router(routes_usage.router, prefix="/api")
app.include_router(routes_actions.router, prefix="/api")
app.include_router(routes_whatif.router, prefix="/api")
