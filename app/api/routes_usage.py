# app/api/routes_usage.py
from typing import List
from fastapi import APIRouter
import pandas as pd
from app.models.schemas import UsagePoint, Anomaly, AnalyzeResponse
from app.models.repo import repo
from app.services.analyzer import detect_anoms_detailed, DEFAULTS, risk_score, DAYS_DEFAULT

router = APIRouter(tags=["Usage"]) 


@router.get("/usage/{sim_id}", response_model=List[UsagePoint], response_model_exclude_none=True)
def usage(sim_id: str, days: int = 30, granularity: str = "day", include_sms: bool = False):
    """Belirli bir SIM için son X günlük kullanım verileri döndür."""
    repo.reload_if_stale()
    daily = repo.usage[repo.usage["sim_id"].astype(str) == str(sim_id)].copy()

    # --- Fallback: usage boşsa sentetik 30 günlük seri üret
    if daily.empty:
        today = pd.Timestamp.today().normalize()
        rows = []
        import random
        base = random.uniform(5, 40)  # günlük ~5–40 MB
        for i in range(days, 0, -1):
            ts = today - pd.Timedelta(days=i)
            mb = max(0.0, random.gauss(base, base * 0.3))      # biraz varyans
            roam = max(0.0, random.gauss(base * 0.05, 2.0))    # roaming dalgalı
            rows.append({
                "sim_id": sim_id,
                "timestamp_mb": ts,
                "mb_used": round(mb, 2),
                "roaming_mb": round(roam, 2)
            })
        daily = pd.DataFrame(rows)

    # --- Normalleştirme/filtre
    daily["timestamp_mb"] = pd.to_datetime(daily["timestamp_mb"], errors="coerce")
    cutoff = pd.Timestamp.today().normalize() - pd.Timedelta(days=days)
    daily = daily[daily["timestamp_mb"] >= cutoff].sort_values("timestamp_mb")

    out: List[UsagePoint] = []
    for _, r in daily.iterrows():
        out.append(UsagePoint(
            ts=r["timestamp_mb"].date().isoformat() if granularity == "day" else r["timestamp_mb"].isoformat(),
            mb_used=float(r["mb_used"]),
            roaming_mb=float(r.get("roaming_mb", 0.0)),
            sms_count=int(r["sms_count"]) if (include_sms and "sms_count" in daily.columns and pd.notna(r.get("sms_count"))) else None
        ))
    return out


@router.get("/anomalies/{sim_id}", response_model=List[Anomaly])
def anomalies(sim_id: str):
    """SIM kullanımındaki anomalileri döndür."""
    repo.reload()
    u = repo.usage[repo.usage["sim_id"].astype(str) == str(sim_id)].copy()
    if u.empty:
        return []
    u["timestamp_mb"] = pd.to_datetime(u["timestamp_mb"], errors="coerce")
    cutoff = pd.Timestamp.today().normalize() - pd.Timedelta(days=DAYS_DEFAULT)
    u = u[u["timestamp_mb"] >= cutoff].sort_values("timestamp_mb")

    roaming_expected = False
    row = repo.sims[repo.sims["sim_id"].astype(str) == str(sim_id)]
    if not row.empty and not repo.profiles.empty:
        dev = str(row.iloc[0]["device_type"])
        m = {str(r["device_type"]): str(r["roaming_expected"]).lower() in ("1", "true", "yes")
             for _, r in repo.profiles.iterrows()}
        roaming_expected = m.get(dev, False)

    details = detect_anoms_detailed(u, roaming_expected=roaming_expected, **DEFAULTS)
    return [Anomaly(type=d.type, ts=d.ts, reason=d.reason) for d in details]


@router.post("/analyze/{sim_id}", response_model=AnalyzeResponse)
def analyze(sim_id: str):
    """Anomali analizi + risk skorunu döndür."""
    from collections import Counter
    repo.reload()
    u = repo.usage[repo.usage["sim_id"].astype(str) == str(sim_id)].copy()
    if u.empty:
        return AnalyzeResponse(anomalies=[], risk_score=0, summary="Kayıt yok")
    u["timestamp_mb"] = pd.to_datetime(u["timestamp_mb"], errors="coerce")
    cutoff = pd.Timestamp.today().normalize() - pd.Timedelta(days=DAYS_DEFAULT)
    u = u[u["timestamp_mb"] >= cutoff].sort_values("timestamp_mb")

    roaming_expected = False
    row = repo.sims[repo.sims["sim_id"].astype(str) == str(sim_id)]
    if not row.empty and not repo.profiles.empty:
        dev = str(row.iloc[0]["device_type"])
        m = {str(r["device_type"]): str(r["roaming_expected"]).lower() in ("1", "true", "yes")
             for _, r in repo.profiles.iterrows()}
        roaming_expected = m.get(dev, False)

    details = detect_anoms_detailed(u, roaming_expected=roaming_expected, **DEFAULTS)
    score = risk_score([Anomaly(type=d.type, ts=d.ts, reason=d.reason) for d in details])
    c = Counter([d.type.value for d in details])
    parts = [f"{c[t]}× {t}" for t in ("spike", "drain", "inactivity", "roaming") if c.get(t)]
    summary = "anomali yok" if not parts else ", ".join(parts)
    return AnalyzeResponse(
        anomalies=[Anomaly(type=d.type, ts=d.ts, reason=d.reason) for d in details],
        risk_score=score,
        summary=summary
    )


@router.post("/whatif/{sim_id}")
def whatif(sim_id: str, body: dict = {}):
    """
    What-If senaryosu için maliyet hesaplama (dummy versiyon).
    Burada gerçek billing mantığı eklenmeli.
    """
    plan_id = body.get("plan_id")
    addons = body.get("addons", [])

    current_total = 1000.0
    if plan_id:
        candidate_total = 800.0   # plan yükseltme senaryosu
    elif addons:
        candidate_total = 900.0   # ek paket senaryosu
    else:
        candidate_total = 950.0   # mevcut

    saving = current_total - candidate_total
    return {
        "current_total": current_total,
        "candidate_total": candidate_total,
        "saving": saving
    }
