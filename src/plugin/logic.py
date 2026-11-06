from datetime import datetime, timedelta


def solve(x):
    cutoff = datetime.strptime(x["cutoff"], "%Y-%m-%dT%H:%M:%S%z")
    rows = []
    for r in x["memories"]:
        if not r["resolved_at"]:
            continue
        age = cutoff - datetime.strptime(r["resolved_at"], "%Y-%m-%dT%H:%M:%S%z")
        if age < timedelta(0) or age > timedelta(days=x["ttl_days"]):
            continue
        score = (
            4 * int(r["profile"] == x["profile"])
            + 2 * int(r["symbol"] == x["symbol"])
            + int(r["regime"] == x["regime"])
        )
        if score:
            rows.append((r, score))
    rows.sort(key=lambda p: p[0]["id"])
    rows.sort(key=lambda p: p[0]["resolved_at"], reverse=True)
    rows.sort(key=lambda p: p[0]["utility"], reverse=True)
    rows.sort(key=lambda p: p[1], reverse=True)
    return {"hits": [{"id": r["id"], "score": s} for r, s in rows[: x["top_k"]]]}
