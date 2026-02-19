
import subprocess
import json
import shutil
import sys
from pathlib import Path

CASES = [
    "case1_syntax_error",
    "case2_missing_import",
    "case3_logic_error",
    "case4_style_issues",
    "case5_complex_bugs"
]

def run_case(case_name):
    case_path = f"sandbox/test_cases/{case_name}"
    

    test_sandbox = f"sandbox/tmp/{case_name}"
    if Path(test_sandbox).exists():
        shutil.rmtree(test_sandbox)
    shutil.copytree(case_path, test_sandbox)
    
    print(f"\n🧪 Testing: {case_name}")
    
    result = subprocess.run(
        ["python", "main.py", "--target_dir", test_sandbox],
        capture_output=True,
        timeout=300,
        text=True
    )
    
    
    try:
        with open("logs/experiment_data.json") as f:
            data = json.load(f)
        iterations = len(data.get("iterations", []))
        success = data.get("final_results", {}).get("success", False)
    except:
        iterations = 0
        success = result.returncode == 0
    
    return {
        "case": case_name,
        "success": success,
        "iterations": iterations,
        "return_code": result.returncode
    }

def main():
    results = []
    
    for case in CASES:
        try:
            r = run_case(case)
        except subprocess.TimeoutExpired:
            r = {"case": case, "success": False, "iterations": -1, "error": "Timeout"}
        except Exception as e:
            r = {"case": case, "success": False, "iterations": -1, "error": str(e)}
        
        status = "✅" if r["success"] else "❌"
        print(f"  {status} {r['case']} — {r.get('iterations', '?')} itérations")
        results.append(r)
    
    passed = sum(1 for r in results if r["success"])
    print(f"\n🎯 Résultat final: {passed}/{len(CASES)} cas réussis")
    
    
    with open("logs/test_report.json", "w") as f:
        json.dump(results, f, indent=2)
    
    return passed == len(CASES)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)