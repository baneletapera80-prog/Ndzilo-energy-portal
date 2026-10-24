import math
from collections import Counter, defaultdict

MIN_REPORTS = 5


def clean(reports):
    rows = []
    for r in reports:
        try:
            rows.append(
                {
                    "suburb": str(r["suburb"]),
                    "hour": int(r["hour"]),
                    "duration": int(r["duration_mins"]),
                }
            )
        except (KeyError, TypeError, ValueError):
            continue
    return [r for r in rows if 0 <= r["hour"] <= 23 and r["duration"] > 0]


def analyse_reports(reports, current_hour):
    data = clean(reports)
    if len(data) < MIN_REPORTS:
        return {"enough_data": False, "count": len(data), "needed": MIN_REPORTS}

    by_hour = Counter(r["hour"] for r in data)
    peak_hour, peak_count = by_hour.most_common(1)[0]
    top_hours = [h for h, _ in by_hour.most_common(3)]

    by_suburb = defaultdict(list)
    for r in data:
        by_suburb[r["suburb"]].append(r["duration"])
    worst_suburb = max(by_suburb, key=lambda s: len(by_suburb[s]))
    worst_count = len(by_suburb[worst_suburb])
    worst_avg = round(sum(by_suburb[worst_suburb]) / worst_count)

    durations = sorted(r["duration"] for r in data)
    avg_duration = round(sum(durations) / len(durations))
    p80 = durations[max(0, math.ceil(0.8 * len(durations)) - 1)]
    backup_hours = max(1, math.ceil(p80 / 60))

    return {
        "enough_data": True,
        "count": len(data),
        "peak_hour": peak_hour,
        "peak_count": peak_count,
        "top_hours": top_hours,
        "worst_suburb": worst_suburb,
        "worst_count": worst_count,
        "worst_avg": worst_avg,
        "avg_duration": avg_duration,
        "p80": p80,
        "backup_hours": backup_hours,
        "next_day": "today" if peak_hour > current_hour else "tomorrow",
    }