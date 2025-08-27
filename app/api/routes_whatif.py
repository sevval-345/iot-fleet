
# app/api/routes_whatif.py
from fastapi import APIRouter, HTTPException
from app.models.schemas import WhatIfRequest, WhatIfResponse, WhatIfTop3Response, WhatIfBreakdown, WhatIfOption
from app.models.repo import repo
from app.services.whatif import usage_stats_for_whatif, get_sim_plan_apn, compute_total

router = APIRouter(tags=["What-If"]) 

@router.post("/whatif/{sim_id}", response_model=WhatIfResponse)
def whatif(sim_id: str, body: WhatIfRequest):
    repo.reload()
    cur_plan_id, sim_apn, cur_plan_row = get_sim_plan_apn(sim_id)
    if cur_plan_row is None:
        raise HTTPException(404, "SIM veya mevcut plan bulunamadı")

    stats = usage_stats_for_whatif(sim_id)
    used_so_far = stats["used_so_far_mb"]; forecast_mb = stats["forecast_mb"]

    current = compute_total(cur_plan_row, [], sim_apn, used_so_far, forecast_mb)

    cand_plan_id = body.plan_id or cur_plan_id
    cand_plan_row = repo.plans[repo.plans["plan_id"].astype(str) == str(cand_plan_id)]
    if cand_plan_row.empty:
        raise HTTPException(400, "Aday plan bulunamadı")
    cand = compute_total(cand_plan_row.iloc[0], body.addons or [], sim_apn, used_so_far, forecast_mb)

    saving = current["total"] - cand["total"]

    return WhatIfResponse(
        current_total=round(current["total"], 2),
        candidate_total=round(cand["total"], 2),
        saving=round(saving, 2),
        current_breakdown=WhatIfBreakdown(**{k: current[k] for k in WhatIfBreakdown.__fields__.keys()}),
        candidate_breakdown=WhatIfBreakdown(**{k: cand[k] for k in WhatIfBreakdown.__fields__.keys()}),
    )

@router.post("/whatif/{sim_id}/top3", response_model=WhatIfTop3Response)
def whatif_top3(sim_id: str):
    repo.reload()
    cur_plan_id, sim_apn, cur_plan_row = get_sim_plan_apn(sim_id)
    if cur_plan_row is None:
        raise HTTPException(404, "SIM veya plan bulunamadı")

    stats = usage_stats_for_whatif(sim_id)
    used_so_far = stats["used_so_far_mb"]; forecast_mb = stats["forecast_mb"]

    current = compute_total(cur_plan_row, [], sim_apn, used_so_far, forecast_mb)
    current_total = current["total"]

    plans = repo.plans[repo.plans["apn"].astype(str) == sim_apn]
    addons_all = []
    if hasattr(repo, "addons") and not repo.addons.empty:
        addons_all = repo.addons[repo.addons["apn"].astype(str) == sim_apn]["addon_id"].astype(str).tolist()

    addon_sets = [[]] + [[a] for a in addons_all]

    options: list[WhatIfOption] = []
    for _, prow in plans.iterrows():
        for adns in addon_sets:
            try:
                cand = compute_total(prow, adns, sim_apn, used_so_far, forecast_mb)
            except ValueError:
                continue
            label = f"{cand['plan_name']}" + (f" + {'+'.join(adns)}" if adns else "")
            saving = current_total - cand["total"]
            options.append(WhatIfOption(
                label=label,
                plan_id=str(cand["plan_id"]),
                addons=[*adns],
                total=round(cand["total"], 2),
                saving=round(saving, 2),
            ))

    options.sort(key=lambda x: x.total)
    return WhatIfTop3Response(current_total=round(current_total, 2), options=options[:3])
