import math
import re
from dataclasses import asdict, is_dataclass


def plain(value):
    return asdict(value) if is_dataclass(value) else value


def verdict(valid, message, **details):
    return {"valid": bool(valid), "score": 1.0 if valid else 0.0, "message": message, "details": details}


def day(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        raise ValueError("noncanonical date")
    y, m, d = [int(part) for part in value.split("-")]
    if y < 1 or not 1 <= m <= 12:
        raise ValueError("invalid year or month")
    leap = y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)
    months = [31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if not 1 <= d <= months[m - 1]:
        raise ValueError("invalid day")
    previous = y - 1
    return 365 * previous + previous // 4 - previous // 100 + previous // 400 + sum(months[: m - 1]) + d


def stamp(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", value):
        raise ValueError("timestamps must use canonical UTC")
    h, m, s = [int(part) for part in value[11:19].split(":")]
    if h > 23 or m > 59 or s > 59:
        raise ValueError("invalid clock time")
    return day(value[:10]) * 86400 + h * 3600 + m * 60 + s


def integer(value, low, high):
    if type(value) is not int or not low <= value <= high:
        raise ValueError("integer outside supported bounds")


def finite(value):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError("expected finite number")


def unique(rows, key):
    ids = [r[key] for r in rows]
    if any(not isinstance(x, str) or not x.strip() for x in ids) or len(set(ids)) != len(ids):
        raise ValueError("identifiers must be nonempty and unique")


def equivalent(actual, expected):
    if isinstance(expected, dict):
        return (
            isinstance(actual, dict)
            and actual.keys() == expected.keys()
            and all(equivalent(actual[k], v) for k, v in expected.items())
        )
    if isinstance(expected, list):
        return (
            isinstance(actual, list)
            and len(actual) == len(expected)
            and all(equivalent(a, b) for a, b in zip(actual, expected))
        )
    if type(expected) is float:
        return (
            type(actual) in (int, float)
            and math.isfinite(actual)
            and math.isclose(actual, expected, rel_tol=1e-9, abs_tol=1e-9)
        )
    return type(actual) is type(expected) and actual == expected


def validate(x):
    stamp(x["cutoff"])
    integer(x["ttl_days"], 0, 36500)
    integer(x["top_k"], 0, 1000)
    if any(not x[k].strip() for k in ["profile", "symbol", "regime"]):
        raise ValueError("query context cannot be empty")
    unique(x["memories"], "id")
    for r in x["memories"]:
        integer(r["utility"], -100, 100)
        if any(not r[k].strip() for k in ["profile", "symbol", "regime"]):
            raise ValueError("memory context cannot be empty")
        observed = stamp(r["observed_at"])
        if r["resolved_at"] and stamp(r["resolved_at"]) < observed:
            raise ValueError("resolution precedes observation")


def expected(x):
    cutoff = stamp(x["cutoff"])
    lower = cutoff - 86400 * x["ttl_days"]
    candidates = []
    for r in x["memories"]:
        if not r["resolved_at"] or not lower <= stamp(r["resolved_at"]) <= cutoff:
            continue
        score = sum(weight for key, weight in [("profile", 4), ("symbol", 2), ("regime", 1)] if r[key] == x[key])
        if score:
            candidates.append((r, score))
    ordered = sorted(
        candidates, key=lambda pair: (-pair[1], -pair[0]["utility"], -stamp(pair[0]["resolved_at"]), pair[0]["id"])
    )
    return {"hits": [{"id": r["id"], "score": score} for r, score in ordered[: x["top_k"]]]}
