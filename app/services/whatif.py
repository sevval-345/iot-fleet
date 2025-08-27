
# app/services/whatif.py
import calendar
import pandas as pd
from typing import List, Union
from sqlalchemy import text
from app.models.repo import repo
from app.core.db import ENGINE


def month_bounds(today: pd.Timestamp) -> tuple[pd.Timestamp, pd.Timestamp, int, int]:
    y, m = today.year, today.month
    start = pd.Timestamp(year=y, month=m, day=1)
    days_in_month = calendar.monthrange(y, m)[1]
    end = pd.Timestamp(year=y, month=m, day=days_in_month)
    day_idx = today.day
    remaining = max(0, days_in_month - day_idx)
    return start, end, day_idx, remaining


def usage_stats_for_whatif(sim_id: str) -> dict:
    repo.reload()
    u = repo.usage[repo.usage["sim_id"].astype(str) == str(sim_id)].copy()
    u["timestamp_mb"] = pd.to_datetime(u["timestamp_mb"], errors="coerce")
    today = pd.Timestamp.today().normalize()
    m_start, _, _, remaining_days = month_bounds(today)
    used_so_far = float(u[(u["timestamp_mb"] >= m_start) & (u["timestamp_mb"] <= today)]["mb_used"].sum() or 0.0)
    last7 = u.sort_values("timestamp_mb").tail(7)
    if not last7.empty and last7["mb_used"].notna().any():
        avg_daily = float(last7["mb_used"].mean() or 0.0)
    else:
        srow = repo.sims[repo.sims["sim_id"].astype(str) == str(sim_id)]
        avg_daily = 0.0
        if not srow.empty:
            plan_id = srow.iloc[0]["plan_id"]
            prow = repo.plans[repo.plans["plan_id"].astype(str) == str(plan_id)]
            if not prow.empty:
                avg_daily = float(prow.iloc[0]["monthly_quota_mb"] / 30.0)
    forecast_mb = avg_daily * remaining_days
    return dict(used_so_far_mb=used_so_far, forecast_mb=forecast_mb, remaining_days=remaining_days)


def get_sim_plan_apn(sim_id: str):
    s = repo.sims[repo.sims["sim_id"].astype(str) == str(sim_id)]
    if s.empty: return None, None, None
    apn = str(s.iloc[0]["apn"])
    plan_id = str(s.iloc[0]["plan_id"])
    prow = repo.plans[repo.plans["plan_id"].astype(str) == plan_id]
    return plan_id, apn, (None if prow.empty else prow.iloc[0])


def compute_total(plan_row, addon_ids: Union[List[str], List[int]], sim_apn: str,
                  used_so_far_mb: float, forecast_mb: float) -> dict:
    if plan_row is None:
        raise ValueError("Plan bulunamadı")

    monthly_quota = float(plan_row["monthly_quota_mb"])
    monthly_price = float(plan_row["monthly_price"])
    overage_per_mb = float(plan_row["overage_per_mb"])
    plan_name = str(plan_row["plan_name"])
    plan_id = str(plan_row["plan_id"])
    plan_apn = str(plan_row["apn"])

    if plan_apn != sim_apn:
        raise ValueError("Plan APN, SIM APN ile uyumlu değil")

    addons_cost = 0.0
    extra_mb = 0.0
    applied: List[str] = []
    if hasattr(repo, "addons") and not repo.addons.empty and addon_ids:
        all_addons = repo.addons.copy()
        for aid in addon_ids:
            row = all_addons[all_addons["addon_id"].astype(str) == str(aid)]
            if row.empty:
                continue
            r = row.iloc[0]
            if str(r["apn"]) != sim_apn:
                continue
            addons_cost += float(r["price"])
            extra_mb += float(r["extra_mb"])
            applied.append(str(r["addon_id"]))

    effective_quota = monthly_quota + extra_mb
    expected_total_used = used_so_far_mb + forecast_mb
    overage_mb = max(0.0, expected_total_used - effective_quota)
    overage_cost = overage_mb * overage_per_mb
    total = monthly_price + addons_cost + overage_cost

    return dict(
        plan_id=plan_id,
        plan_name=plan_name,
        base=monthly_price,
        quota_mb=monthly_quota,
        addons_applied=applied,
        addons_cost=addons_cost,
        extra_mb_total=extra_mb,
        effective_quota_mb=effective_quota,
        used_so_far_mb=used_so_far_mb,
        forecast_mb=forecast_mb,
        overage_mb=overage_mb,
        overage_cost=overage_cost,
        total=total
    )
