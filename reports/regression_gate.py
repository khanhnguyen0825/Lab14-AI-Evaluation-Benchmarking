import json
from datetime import datetime

QUALITY_THRESHOLD = 3.5
HIT_RATE_THRESHOLD = 0.75
AGREEMENT_THRESHOLD = 0.70
COST_BUDGET_USD = 1.00
DELTA_THRESHOLD = 0.0

def run_release_gate(summary_path="reports/summary.json"):
    with open(summary_path, "r", encoding="utf-8") as f:
        summary = json.load(f)
    metrics = summary.get("metrics", {})
    regression = summary.get("regression", {})
    checks = {}
    checks["quality"] = {"pass": metrics.get("avg_score", 0) >= QUALITY_THRESHOLD, "value": metrics.get("avg_score", 0), "threshold": QUALITY_THRESHOLD}
    checks["hit_rate"] = {"pass": metrics.get("hit_rate", 0) >= HIT_RATE_THRESHOLD, "value": metrics.get("hit_rate", 0), "threshold": HIT_RATE_THRESHOLD}
    checks["agreement_rate"] = {"pass": metrics.get("agreement_rate", 0) >= AGREEMENT_THRESHOLD, "value": metrics.get("agreement_rate", 0), "threshold": AGREEMENT_THRESHOLD}
    checks["cost_usd"] = {"pass": metrics.get("cost_usd", 0) <= COST_BUDGET_USD, "value": metrics.get("cost_usd", 0), "threshold": COST_BUDGET_USD}
    checks["delta"] = {"pass": regression.get("delta", 0) >= DELTA_THRESHOLD, "value": regression.get("delta", 0), "threshold": DELTA_THRESHOLD}
    all_pass = all(c["pass"] for c in checks.values())
    decision = "APPROVE" if all_pass else "ROLLBACK"
    for k, v in checks.items():
        if not v["pass"]:
            print(f"❌ {k} check failed: value={v['value']} < threshold={v['threshold']}")
    if all_pass:
        print("🚀 DECISION: APPROVE — Ready for release")
    else:
        print("🔴 DECISION: ROLLBACK — Do not release")
    result = {
        "decision": decision,
        "checks": checks,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    with open("reports/gate_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return decision

if __name__ == "__main__":
    run_release_gate()
