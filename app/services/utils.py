# app/services/utils.py
from typing import Union, Optional
import pandas as pd
import numpy as np

def to_dt(s: Union[pd.Series, pd.Timestamp]) -> Union[pd.Series, pd.Timestamp]:
    if isinstance(s, pd.Series):
        d = pd.to_datetime(s, errors="coerce", utc=True)
        return d.dt.tz_localize(None) if hasattr(d, "dt") else d
    d = pd.to_datetime(s, errors="coerce", utc=True)
    return d.tz_localize(None) if getattr(d, "tzinfo", None) else d


def fmt_ts(ts: pd.Timestamp, step_hours: float) -> str:
    return (ts.isoformat() if step_hours < 20 else ts.date().isoformat())


def infer_step_hours(ts: pd.Series) -> float:
    ts = ts.sort_values()
    if len(ts) < 2:
        return 24.0
    diffs = ts.diff().dropna().dt.total_seconds() / 3600.0
    if diffs.empty:
        return 24.0
    return float(np.median(diffs))


def detect_inactivity_block(d: pd.DataFrame, inactivity_hours: int) -> Optional[dict]:
    step = infer_step_hours(d["timestamp_mb"])
    need = max(1, int(np.ceil(inactivity_hours / step)))

    run_len, start_ts = 0, None
    for _, r in d.iterrows():
        if float(r["mb_used"]) == 0.0:
            run_len += 1
            if start_ts is None:
                start_ts = r["timestamp_mb"]
            if run_len >= need:
                return {"start": start_ts, "end": r["timestamp_mb"], "step": step}
        else:
            run_len, start_ts = 0, None
    return None


def roll_ma_sd(s: pd.Series, w: int = 7):
    if len(s) < 2:
        return s * 0 + (s.mean() if len(s) else 0), s * 0
    ma = s.rolling(w, min_periods=1).mean().shift(1)
    sd = s.rolling(w, min_periods=1).std(ddof=0).shift(1).fillna(0.0)
    return ma, sd


def risk_badge_from_score(score: int) -> str:
    if score <= 30:   return "green"
    if score <= 70:   return "orange"
    return "red"
