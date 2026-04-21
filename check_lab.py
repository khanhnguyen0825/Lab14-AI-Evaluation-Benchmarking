import json
import os
import sys

# Ensure output is UTF-8 to handle any remaining special characters
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def validate_lab():
    print("[INFO] Dang kiem tra dinh dang bai nop...")

    required_files = [
        "reports/summary.json",
        "reports/benchmark_results.json",
        "analysis/failure_analysis.md"
    ]

    # 1. Kiểm tra sự tồn tại của tất cả file
    missing = []
    for f in required_files:
        if os.path.exists(f):
            print(f"[OK] Tim thay: {f}")
        else:
            print(f"[FAIL] Thieu file: {f}")
            missing.append(f)

    if missing:
        print(f"\n[FAIL] Thieu {len(missing)} file. Hay bo sung truoc khi nop bai.")
        return

    # 2. Kiểm tra nội dung summary.json
    try:
        with open("reports/summary.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"[FAIL] File reports/summary.json khong phai JSON hop le: {e}")
        return

    if "metrics" not in data or "metadata" not in data:
        print("[FAIL] File summary.json thieu truong 'metrics' hoac 'metadata'.")
        return

    metrics = data["metrics"]

    print(f"\n--- Thong ke nhanh ---")
    print(f"Tong so cases: {data['metadata'].get('total', 'N/A')}")
    print(f"Diem trung binh: {metrics.get('avg_score', 0):.2f}")

    # EXPERT CHECKS
    # Check retrieval
    if "hit_rate" in metrics:
        print(f"[OK] Da tim thay Retrieval Metrics (Hit Rate: {metrics['hit_rate']*100:.1f}%)")
    else:
        print(f"[WARN] CẢNH BÁO: Thieu Retrieval Metrics (hit_rate).")

    # Check multi-judge
    if "agreement_rate" in metrics:
        print(f"[OK] Da tim thay Multi-Judge Metrics (Agreement Rate: {metrics['agreement_rate']*100:.1f}%)")
    else:
        print(f"[WARN] CẢNH BÁO: Thieu Multi-Judge Metrics (agreement_rate).")

    # Check mrr
    if "mrr" in metrics:
        print(f"[OK] Tim thay MRR metric: {metrics['mrr']:.2f}")
    else:
        print(f"[WARN] CẢNH BÁO: Thieu MRR metric (mrr).")

    # Check cost_usd
    if "cost_usd" in metrics:
        print(f"[OK] Tim thay Cost metric: {metrics['cost_usd']:.4f} USD")
    else:
        print(f"[WARN] CẢNH BÁO: Thieu Cost metric (cost_usd).")

    # Check regression section
    if "regression" in data:
        print(f"[OK] Tim thay Regression section trong summary.json")
    else:
        print(f"[WARN] CẢNH BÁO: Thieu Regression section trong summary.json")

    if data["metadata"].get("version"):
        print(f"[OK] Da tim thay thong tin phien ban Agent (Regression Mode)")

    print("\n[SUCCESS] Bai lab da san sang de cham diem!")

if __name__ == "__main__":
    validate_lab()
