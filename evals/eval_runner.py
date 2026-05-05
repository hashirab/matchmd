import json
import requests
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def load_golden_dataset():
    with open("golden_dataset.json") as f:
        return json.load(f)

def run_eval(case):
    try:
        # Call match endpoint
        res = requests.post(f"{BASE_URL}/match", json=case["profile"], timeout=30)
        data = res.json()

        result_text = data.get("result", "").lower()
        match_prob = data.get("match_probability", 0)
        tier = data.get("tier", "")
        programs_used = data.get("programs_used", [])

        # Check 1: keywords present
        keywords_found = [kw for kw in case["expected_keywords"] if kw.lower() in result_text]
        keyword_score = len(keywords_found) / len(case["expected_keywords"])

        # Check 2: tier alignment
        expected_tier = case["expected_tier"]
        tier_pass = (
            (expected_tier == "strong" and match_prob >= 0.6) or
            (expected_tier == "moderate" and 0.1 <= match_prob <= 0.95) or
            (expected_tier == "reach" and match_prob <= 0.5)
        )

        # Check 3: programs retrieved
        programs_retrieved = len(programs_used) > 0

        # Overall pass
        passed = keyword_score >= 0.5 and tier_pass and programs_retrieved

        return {
            "id": case["id"],
            "passed": passed,
            "keyword_score": round(keyword_score, 2),
            "tier_pass": tier_pass,
            "programs_retrieved": programs_retrieved,
            "match_probability": match_prob,
            "programs_used": programs_used[:3],
            "notes": case["notes"]
        }
    except Exception as e:
        return {
            "id": case["id"],
            "passed": False,
            "error": str(e),
            "notes": case["notes"]
        }

def run_all_evals():
    print(f"\nMatchMD Eval Run — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    cases = load_golden_dataset()
    results = []
    passed = 0

    for case in cases:
        print(f"Running case {case['id']}: {case['profile']['specialty']} — Step2 {case['profile']['step2_score']}...")
        result = run_eval(case)
        results.append(result)
        if result["passed"]:
            passed += 1
            print(f"  PASS — keyword: {result.get('keyword_score')}, tier: {result.get('tier_pass')}, prob: {result.get('match_probability')}")
        else:
            keyword_s = result.get('keyword_score')
            tier_s = result.get('tier_pass')
            prob = result.get('match_probability', 'N/A')
            err = result.get('error', f'keyword: {keyword_s}, tier: {tier_s}, prob: {prob}')
            print(f"  FAIL — {err}")
        time.sleep(1)

    total = len(cases)
    pass_rate = passed / total * 100

    print("\n" + "=" * 60)
    print(f"Results: {passed}/{total} passed ({pass_rate:.1f}%)")
    print("=" * 60)

    # Save results
    output = {
        "timestamp": datetime.now().isoformat(),
        "passed": passed,
        "total": total,
        "pass_rate": round(pass_rate, 1),
        "results": results
    }
    with open("eval_results.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to eval_results.json")

    return pass_rate

if __name__ == "__main__":
    run_all_evals()