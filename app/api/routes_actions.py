
# app/api/routes_actions.py
from typing import List
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy import text
from datetime import datetime
from app.core.db import ENGINE
from app.models.schemas import (
    ActionApplyRequest, ActionApplyResponse,
    ActionImpactRequest, ActionImpactItem, ActionImpactResponse,
    ActionSuggestRequest, ActionSuggestItem, ActionSuggestResponse,
)
from app.models.enums import Action, AnomalyType
from app.services.analyzer import baseline_next_24h_mb, apply_effect, detect_anoms_detailed, risk_score
from app.models.repo import repo

router = APIRouter(tags=["Actions"]) 

# Basit WS Manager
class WSManager:
    def __init__(self):
        self.active: set[WebSocket] = set()

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.add(ws)

    def disconnect(self, ws: WebSocket):
        self.active.discard(ws)

    async def send_all(self, payload: dict):
        dead = []
        for ws in list(self.active):
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

ws_manager = WSManager()

@router.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws_manager.connect(ws)
    try:
        while True:
            _ = await ws.receive_text()
            await ws.send_json({"type": "pong"})
    except WebSocketDisconnect:
        ws_manager.disconnect(ws)


@router.post("/actions", response_model=ActionApplyResponse)
async def apply(req: ActionApplyRequest):
    if not req.sim_ids:
        raise HTTPException(status_code=400, detail="sim_ids boş olamaz")
    action_id = f"A-{int(datetime.utcnow().timestamp())}"
    with ENGINE.begin() as c:
        c.execute(text(
            """
            INSERT INTO dbo.actions_log (action_id, sim_id, action, reason, created_at, actor, status)
            VALUES (:id, :sim, :act, :rsn, :ts, :actor, :st)
            """
        ), dict(id=action_id, sim=";".join(req.sim_ids), act=req.action.value,
                 rsn=req.reason or "", ts=datetime.utcnow(), actor="api", st="done"))
    await ws_manager.send_all({
        "type": "action_logged",
        "action": req.action.value,
        "sim_ids": req.sim_ids,
        "reason": req.reason or ""
    })
    return ActionApplyResponse(applied_to=len(req.sim_ids))


def _suggest_for_sim(sid: str) -> ActionSuggestItem:
    repo.reload()
    u = repo.usage[repo.usage["sim_id"].astype(str) == str(sid)]
    details = detect_anoms_detailed(u, roaming_expected=False)
    r = risk_score([Anomaly(type=d.type, ts=d.ts, reason=d.reason) for d in details])
    types = {d.type for d in details}

    if (AnomalyType.spike in types or AnomalyType.drain in types) and r >= 70:
        act, conf = Action.freeze_24h, 90
    elif AnomalyType.roaming in types:
        act, conf = Action.throttle, 80
    elif AnomalyType.inactivity in types:
        act, conf = Action.notify, 70
    else:
        act, conf = Action.notify, 60

    b = baseline_next_24h_mb(str(sid))
    e = apply_effect(b, act, 65.0)
    impact_pct = 0.0 if b == 0 else (e - b) / b * 100.0
    reason = f"risk={r}, anomali={','.join(t.value for t in types) or 'yok'}"
    return ActionSuggestItem(
        sim_id=str(sid), recommended=act, confidence=conf,
        reason=reason, impact_pct=round(impact_pct,1)
    )

@router.post("/actions/suggest", response_model=ActionSuggestResponse)
def suggest(req: ActionSuggestRequest):
    sims = req.sim_ids or repo.sims["sim_id"].astype(str).tolist()
    items = [_suggest_for_sim(s) for s in sims]
    return ActionSuggestResponse(items=items)

@router.post("/actions/impact", response_model=ActionImpactResponse)
def impact(req: ActionImpactRequest):
    items, tb, te = [], 0.0, 0.0
    for sid in req.sim_ids:
        b = baseline_next_24h_mb(str(sid))
        e = apply_effect(b, req.action, req.throttle_reduction_pct)
        d = 0.0 if b == 0 else (e - b) / b * 100.0
        items.append(ActionImpactItem(
            sim_id=str(sid),
            baseline_mb_24h=round(b, 2),
            expected_mb_24h=round(e, 2),
            delta_pct=round(d, 1),
        ))
        tb += b; te += e
    tdelta = 0.0 if tb == 0 else (te - tb) / tb * 100.0
    return ActionImpactResponse(
        action=req.action,
        total_baseline_mb_24h=round(tb, 2),
        total_expected_mb_24h=round(te, 2),
        delta_pct=round(tdelta, 1),
        items=items
    )

