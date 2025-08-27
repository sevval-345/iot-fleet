
# app/api/routes_fleet.py
from typing import List, Optional
from fastapi import APIRouter
import pandas as pd
from app.models.schemas import FleetItem, Anomaly
from app.models.repo import repo
from app.services.analyzer import detect_anoms_detailed, DEFAULTS, risk_score
from app.services.utils import risk_badge_from_score

router = APIRouter(tags=["Fleet"]) 

@router.get("/fleet", response_model=List[FleetItem], response_model_exclude_none=True)
def fleet(risk: Optional[str] = None, roaming: Optional[bool] = None, limit: int = 100, offset: int = 0):
    repo.reload_if_stale()

    plan_name = {str(r["plan_id"]): str(r["plan_name"]) for _, r in repo.plans.iterrows()}
    last_seen = {}
    if not repo.usage.empty:
        last_ts = repo.usage.groupby("sim_id")["timestamp_mb"].max()
        last_seen = {str(k): (v.date().isoformat() if pd.notna(v) else None) for k, v in last_ts.items()}

    prof = {}
    if not repo.profiles.empty:
        prof = {str(r["device_type"]): str(r["roaming_expected"]).lower() in ("1","true","yes")
                for _, r in repo.profiles.iterrows()}

    items: List[FleetItem] = []
    sims_iter = repo.sims.reset_index(drop=True).iloc[offset: offset + limit].itertuples(index=False)
    for s in sims_iter:
        sid = str(getattr(s, "sim_id"))
        u = repo.usage[repo.usage["sim_id"].astype(str) == sid]
        an_details = detect_anoms_detailed(u, roaming_expected=prof.get(str(getattr(s, "device_type")), False), **DEFAULTS)
        an = [Anomaly(type=d.type, ts=d.ts, reason=d.reason) for d in an_details]
        score = risk_score(an)

        has_roam = any(d.type.value == "roaming" for d in an_details)
        items.append(FleetItem(
            sim_id=sid,
            device_type=str(getattr(s, "device_type")),
            apn=str(getattr(s, "apn")),
            plan=plan_name.get(str(getattr(s, "plan_id")), str(getattr(s, "plan_id"))),
            status=str(getattr(s, "status")),
            city=str(getattr(s, "city")),
            last_seen_at=last_seen.get(sid),
            risk_score=score,
            risk_badge=risk_badge_from_score(score),
            anomalies_count=len(an),
            has_roaming=has_roam,
        ))

    if risk is not None:
        items = [i for i in items if i.risk_badge == risk.lower()]
    if roaming is not None:
        items = [i for i in items if i.has_roaming is roaming]

    return items

@router.get("/fleet/ids", response_model=List[str])
def fleet_ids(risk: Optional[str] = None, roaming: Optional[bool] = None):
    items = fleet(risk=risk, roaming=roaming)
    return [i.sim_id for i in items]

