"""
Test du toolkit Judge
"""
from pathlib import Path
import sys
# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


from src.tools.judge_toolkit import (
    evaluate_code,
    format_test_feedback_for_fixer,
    compare_quality
)

def test_judge_toolkit():
    """Test des fonctions du Judge"""
    print("\n" + "="*60)
    print("⚖️  Testing Judge Toolkit")
    print("="*60)
    
    target_dir = str(project_root / "sandbox" / "test_toolkit")
    
    try:
        # Test 1: Évaluer le code (devrait échouer car buggy)
        print("\n🧪 Test 1: Evaluating buggy code...")
        test_results = evaluate_code(target_dir)
        
        assert 'passed' in test_results, "Missing 'passed' field"
        assert 'errors' in test_results, "Missing 'errors' field"
        
        print(f"  ✅ Code evaluated")
        print(f"  📊 Tests passed: {test_results['passed']}")
        print(f"  ❌ Errors: {len(test_results['errors'])}")
        
        if not test_results['passed']:
            print(f"  Expected: Tests should fail (code is buggy)")
        
        # Test 2: Formater le feedback
        if not test_results['passed']:
            print("\n📝 Test 2: Formatting test feedback...")
            feedback = format_test_feedback_for_fixer(test_results)
            assert isinstance(feedback, str), "Feedback should be a string"
            print(f"  ✅ Feedback formatted (length: {len(feedback)} chars)")
            print(f"  Preview:\n{feedback[:200]}...")
        
        # Test 3: Comparer la qualité
        print("\n📊 Test 3: Comparing quality...")
        comparison = compare_quality(before_score=3.5, after_score=7.2)
        assert 'improvement' in comparison, "Missing improvement field"
        assert 'percentage' in comparison, "Missing percentage field"
        print(f"  ✅ Quality comparison done")
        print(f"  📈 Improvement: {comparison['improvement']:.2f}")
        print(f"  📊 Percentage: {comparison['percentage']:.1f}%")
        
        print("\n✅ Judge Toolkit: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    success = test_judge_toolkit()
    sys.exit(0 if success else 1)