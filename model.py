from math import isfinite

def classify_risk(r):
    r = int(r)
    return "Low Risk" if r == 1 else "Medium Risk" if r == 2 else "High Risk"

def _minmax(x, lo, hi):
    if hi <= lo:
        return 0.0
    return (x - lo) / (hi - lo)

def recommend(df, budget, city, ptype, prefs, override_weights=None):

    candidates = []
    for _, r in df.iterrows():
        r_city = str(r.get("city", "")).strip()
        r_type = str(r.get("property_type", "")).strip()

        if city != "Any" and r_city.lower() != str(city).strip().lower():
            continue
        if ptype != "Any" and r_type.lower() != str(ptype).strip().lower():
            continue

        try:
            price = float(r.get("price", 0))
            roi   = float(r.get("expected_roi", 0))
            risk  = int(r.get("base_risk", 2))
        except Exception:
            continue

        if not isfinite(price) or not isfinite(roi):
            continue

        if budget and float(budget) > 0:
            if price > float(budget) * 1.2:
                continue

        risk_norm = (risk - 1) / 2.0 
        diff = abs(price - budget) / budget if budget and budget > 0 else 0.0

        candidates.append({
            "row": r,
            "price": price,
            "roi": roi,
            "risk": risk,
            "risk_norm": max(0.0, min(1.0, risk_norm)),
            "diff": max(0.0, diff),
        })

    if not candidates:
        return []

    rois  = [c["roi"] for c in candidates]
    diffs = [c["diff"] for c in candidates]

    roi_min, roi_max   = min(rois), max(rois)
    diff_min, diff_max = min(diffs), max(diffs)

    for c in candidates:
        c["roi_norm"]  = _minmax(c["roi"], roi_min, roi_max)
        c["diff_norm"] = _minmax(c["diff"], diff_min, diff_max)

    mode = "learned"

    if override_weights:
        if override_weights.get("w_roi", 0) >= 0.7:
            mode = "roi"
        elif override_weights.get("w_risk", 0) >= 0.7:
            mode = "risk"
        elif override_weights.get("w_budget", 0) >= 0.7:
            mode = "price"
    else:
        if prefs.w_roi >= 0.7:
            mode = "roi"
        elif prefs.w_risk >= 0.7:
            mode = "risk" 
        elif prefs.w_budget >= 0.7:
            mode = "price"

    if mode == "roi":
        candidates.sort(key=lambda c: (-c["roi"], c["risk_norm"], c["diff"]))

    elif mode == "risk":
        candidates.sort(key=lambda c: (c["risk_norm"], -c["roi"], c["diff"]))

    elif mode == "price":
        if budget and budget > 0:
            candidates.sort(key=lambda c: (c["diff"], -c["roi"], c["risk_norm"]))
        else:
            candidates.sort(key=lambda c: (c["price"], -c["roi"], c["risk_norm"]))

    else:
        w_roi    = float(prefs.w_roi)
        w_risk   = float(prefs.w_risk)
        w_budget = float(prefs.w_budget)

        candidates.sort(
            key=lambda c: (
                w_roi * c["roi_norm"]
                - w_risk * c["risk_norm"]
                - w_budget * c["diff_norm"]
            ),
            reverse=True
        )

    results = []
    for c in candidates:
        r = c["row"]
        results.append({
            "name": str(r.get("name", "")),
            "city": str(r.get("city", "")),
            "type": str(r.get("property_type", "")),
            "price": float(c["price"]),
            "roi": float(c["roi"]),
            "risk_text": classify_risk(int(c["risk"])),
            "url": str(r.get("url", "")).strip(),
        })

    return results
