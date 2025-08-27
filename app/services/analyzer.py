
# app/services/analyzer.py
from typing import List
import pandas as pd
import numpy as np
from app.models.schemas import Anomaly, AnomalyDetail, Evidence
from app.models.enums import AnomalyType, Action
from app.models.repo import repo
from app.services.utils import roll_ma_sd, detect_inactivity_block, fmt_ts

DEFAULTS = {
    "k": 2.5,
    "drain_factor": 1.5,
    "drain_days": 3,
    "inactivity_hours": 48,
    "roaming_threshold_mb": 20.0,
}
DAYS_DEFAULT = 30


def detect_anoms_detailed(
    df: pd.DataFrame,
    roaming_expected: bool = False,
    *,
    k: float = 2.5,
    drain_factor: float = 1.5,
    drain_days: int = 3,
    inactivity_hours: int = 48,
    roaming_threshold_mb: float = 20.0
) -> List[AnomalyDetail]:
    out: List[AnomalyDetail] = []
    if df is None or df.empty:
        return out

    d = df.sort_values("timestamp_mb").copy()
    ma7, sd7 = roll_ma_sd(d["mb_used"], 7)
    d["ma7"], d["sd7"] = ma7, sd7

    thr = np.maximum(d["ma7"]*k, d["ma7"] + 3*d["sd7"])
    mask = d["mb_used"] > thr
    for i, row in d.loc[mask].iterrows():
        ts = row["timestamp_mb"].date().isoformat()
        out.append(AnomalyDetail(
            type=AnomalyType.spike,
            ts=ts,
            reason=f"mb_used {row['mb_used']:.1f} > max({k}×MA7={row['ma7']*k:.1f}, MA7+3σ={(row['ma7']+3*row['sd7']):.1f})",
            evidence=Evidence(
                threshold=float(thr.loc[i]) if not pd.isna(thr.loc[i]) else None,
                baseline_ma7=float(row["ma7"]) if not pd.isna(row["ma7"]) else None,
                baseline_sd7=float(row["sd7"]) if not pd.isna(row["sd7"]) else None,
                value=float(row["mb_used"])
            )
        ))

    over = d["mb_used"] > (d["ma7"] * drain_factor)
    streak = 0
    start_idx = None
    for i in range(len(d)):
        if over.iloc[i]:
            streak += 1
            if start_idx is None: start_idx = i
            if streak >= drain_days:
                end_idx = i
                days = [d.iloc[j]["timestamp_mb"].date().isoformat() for j in range(start_idx, end_idx+1)]
                out.append(AnomalyDetail(
                    type=AnomalyType.drain,
                    ts=d.iloc[end_idx]["timestamp_mb"].date().isoformat(),
                    reason=f"{drain_days}+ gün > {drain_factor}×MA7",
                    evidence=Evidence(
                        days=days,
                        window_start=days[0],
                        window_end=days[-1]
                    )
                ))
                break
        else:
            streak = 0
            start_idx = None

    blk = detect_inactivity_block(d, inactivity_hours=inactivity_hours)
    if blk:
        out.append(AnomalyDetail(
            type=AnomalyType.inactivity,
            ts=fmt_ts(blk["end"], blk["step"]),
            reason=f">= {inactivity_hours}h zero usage",
            evidence=Evidence(
                window_start=fmt_ts(blk["start"], blk["step"]),
                window_end=fmt_ts(blk["end"], blk["step"])
            )
         ))

    if not roaming_expected and (d["roaming_mb"] > roaming_threshold_mb).any():
        idx = d.index[d["roaming_mb"] > roaming_threshold_mb][0]
        row = d.loc[idx]
        out.append(AnomalyDetail(
            type=AnomalyType.roaming,
            ts=row["timestamp_mb"].date().isoformat(),
            reason=f"roaming {row['roaming_mb']:.1f}MB > {roaming_threshold_mb}MB (unexpected)",
            evidence=Evidence(
                roaming_mb=float(row["roaming_mb"]),
                expected_roaming=False,
                threshold=float(roaming_threshold_mb)
            )
        ))
    return out


def detect_anoms(df: pd.DataFrame, roaming_expected: bool = False) -> List[Anomaly]:
    details = detect_anoms_detailed(df, roaming_expected=roaming_expected, **DEFAULTS)
    return [Anomaly(type=d.type, ts=d.ts, reason=d.reason) for d in details]


def risk_score(anoms: List[Anomaly]) -> int:
    t = {a.type for a in anoms}; s = 0
    if AnomalyType.spike in t: s += 40
    if AnomalyType.drain in t: s += 30
    if AnomalyType.inactivity in t: s += 20
    if AnomalyType.roaming in t: s += 40
    return min(100, s)


def baseline_next_24h_mb(sim_id: str) -> float:
    import pandas as pd
    repo.reload()
    u = repo.usage[repo.usage["sim_id"].astype(str) == str(sim_id)].copy()
    if not u.empty:
        u["timestamp_mb"] = pd.to_datetime(u["timestamp_mb"], errors="coerce")
        u = u.sort_values("timestamp_mb").tail(7)
        return float(u["mb_used"].mean() or 0.0)
    row = repo.sims[repo.sims["sim_id"].astype(str) == str(sim_id)]
    if not row.empty:
        plan_id = row.iloc[0]["plan_id"]
        p = repo.plans[repo.plans["plan_id"].astype(str) == str(plan_id)]
        if not p.empty:
            return float(p.iloc[0]["monthly_quota_mb"] / 30.0)
    return 0.0


def apply_effect(baseline: float, action: Action, throttle_reduction_pct: float = 65.0) -> float:
    if action == Action.freeze_24h:
        return 0.0
    if action == Action.throttle:
        return baseline * max(0.0, 1.0 - throttle_reduction_pct/100.0)
    return baseline

