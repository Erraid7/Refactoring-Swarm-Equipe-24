"""
Test complet de tous les toolkits
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_all_toolkit_tests():
    """Exécute tous les tests des toolkits"""
    print("\n" + "="*70)
    print("🧪 RUNNING ALL TOOLKIT TESTS")
    print("="*70)
    
    tests = []
    
    # Test 1: Imports
    print("\n[1/4] Testing imports...")
    from test_toolsmith_setup import test_toolkit_imports
    result1 = test_toolkit_imports()
    tests.append(("Imports", result1))
    
    if not result1:
        print("❌ Import tests failed. Fix imports before continuing.")
        return False
    
    # Test 2: Auditor
    print("\n[2/4] Testing Auditor Toolkit...")
    from test_auditor_toolkit import test_analyze_project
    result2 = test_analyze_project()
    tests.append(("Auditor", result2))
    
    # Test 3: Fixer
    print("\n[3/4] Testing Fixer Toolkit...")
    from test_fixer_toolkit import test_fixer_toolkit
    result3 = test_fixer_toolkit()
    tests.append(("Fixer", result3))
    
    # Test 4: Judge
    print("\n[4/4] Testing Judge Toolkit...")
    from test_judge_toolkit import test_judge_toolkit
    result4 = test_judge_toolkit()
    tests.append(("Judge", result4))
    
    # Rapport final
    print("\n" + "="*70)
    print("📊 FINAL REPORT")
    print("="*70)
    
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    all_passed = all(result for _, result in tests)
    
    if all_passed:
        print("\n🎉 ALL TOOLKIT TESTS PASSED!")
        print("✅ You can now proceed to agent integration.")
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("❌ Fix the failing tests before proceeding.")
    
    return all_passed

if __name__ == "__main__":
    success = run_all_toolkit_tests()
    sys.exit(0 if success else 1)