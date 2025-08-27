# app/models/schemas.py
from typing import List, Optional, Dict
from pydantic import BaseModel
from app.models.enums import Action, AnomalyType

class FleetItem(BaseModel):
    sim_id: str
    device_type: str
    apn: str
    plan: str
    status: str
    city: Optional[str] = None
    last_seen_at: Optional[str] = None
    risk_score: int = 0
    risk_badge: str = "green"
    anomalies_count: int = 0
    has_roaming: bool = False

class UsagePoint(BaseModel):
    ts: str
    mb_used: float
    roaming_mb: float
    sms_count: Optional[int] = None

class UsagePointLite(BaseModel):
    ts: str
    mb_used: float
    roaming_mb: float

class Evidence(BaseModel):
    threshold: Optional[float] = None
    baseline_ma7: Optional[float] = None
    baseline_sd7: Optional[float] = None
    value: Optional[float] = None
    days: Optional[List[str]] = None
    window_start: Optional[str] = None
    window_end: Optional[str] = None
    roaming_mb: Optional[float] = None
    expected_roaming: Optional[bool] = None

class Anomaly(BaseModel):
    type: AnomalyType
    ts: str
    reason: str

class AnomalyDetail(BaseModel):
    type: AnomalyType
    ts: str
    reason: str
    evidence: Evidence

class AnalyzeParams(BaseModel):
    days: int = 30
    k: float = 2.5
    drain_factor: float = 1.5
    drain_days: int = 3
    inactivity_hours: int = 48
    roaming_threshold_mb: float = 20.0

class AnalyzeResponse(BaseModel):
    anomalies: List[Anomaly]
    risk_score: int
    summary: str

class ActionApplyRequest(BaseModel):
    sim_ids: List[str]
    action: Action
    params: Optional[Dict[str, object]] = None
    reason: Optional[str] = None

class ActionApplyResponse(BaseModel):
    status: str = "ok"
    logged: bool = True
    applied_to: int

class ActionImpactRequest(BaseModel):
    sim_ids: List[str]
    action: Action
    throttle_reduction_pct: float = 65.0

class ActionImpactItem(BaseModel):
    sim_id: str
    baseline_mb_24h: float
    expected_mb_24h: float
    delta_pct: float

class ActionImpactResponse(BaseModel):
    action: Action
    total_baseline_mb_24h: float
    total_expected_mb_24h: float
    delta_pct: float
    items: List[ActionImpactItem]

class ActionSuggestRequest(BaseModel):
    sim_ids: Optional[List[str]] = None

class ActionSuggestItem(BaseModel):
    sim_id: str
    recommended: Action
    confidence: int
    reason: str
    impact_pct: float

class ActionSuggestResponse(BaseModel):
    items: List[ActionSuggestItem]

class WhatIfBreakdown(BaseModel):
    plan_id: str
    plan_name: str
    base: float
    quota_mb: float
    addons_applied: List[str]
    addons_cost: float
    extra_mb_total: float
    effective_quota_mb: float
    used_so_far_mb: float
    forecast_mb: float
    overage_mb: float
    overage_cost: float
    total: float

class WhatIfResponse(BaseModel):
    current_total: float
    candidate_total: float
    saving: float
    current_breakdown: WhatIfBreakdown
    candidate_breakdown: WhatIfBreakdown


class WhatIfRequest(BaseModel):
    plan_id: Optional[str] = None
    addons: Optional[List[str]] = None

class WhatIfOption(BaseModel):
    label: str
    plan_id: str
    addons: List[str]
    total: float
    saving: float

class WhatIfTop3Response(BaseModel):
    current_total: float
    options: List[WhatIfOption]

