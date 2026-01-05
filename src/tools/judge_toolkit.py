"""
Judge Toolkit
High-level API specifically designed for the Judge agent.
Conforms to the interface contract defined in docs/interfaces.md
"""

from typing import Dict, List
from src.tools.testing import run_pytest
from src.tools.analysis import run_pylint_on_directory


def evaluate_code(target_dir: str) -> Dict:
    """
    Evaluate code quality and test results.
    This is the main function the Judge agent should call.
    
    Returns data in the format expected by RefactoringState.test_results
    
    Args:
        target_dir: Path to the project directory
        
    Returns:
        Dict matching the test_results format from interfaces.md:
        {
            "passed": bool,      # True if all tests pass
            "errors": [...]      # List of error messages if tests failed
        }
        
        Plus additional metrics for logging:
        {
            "pylint_score": float,
            "test_count": int,
            "failed_tests": int,
            "test_details": {...}
        }
    """
    # Run tests
    test_results = run_pytest(target_dir)
    
    # Run Pylint for quality score
    pylint_results = run_pylint_on_directory(target_dir)
    
    # Format errors for the interface
    errors = []
    
    if not test_results['passed']:
        # Extract failure messages
        for failure in test_results.get('failures', []):
            errors.append(
                f"Test: {failure.get('test', 'unknown')}\n"
                f"Message: {failure.get('message', 'No details')}"
            )
        
        # Add error messages
        for error in test_results.get('errors', []):
            if isinstance(error, dict):
                errors.append(error.get('message', str(error)))
            else:
                errors.append(str(error))
    
    # Return in the expected format
    return {
        # Required fields from interfaces.md
        "passed": test_results['passed'],
        "errors": errors,
        
        # Additional metrics for logging and analysis
        "pylint_score": pylint_results['average_score'],
        "test_count": test_results.get('total', 0),
        "passed_tests": test_results.get('passed_count', 0),
        "failed_tests": test_results.get('failed_count', 0),
        "error_count": test_results.get('error_count', 0),
        "execution_time": test_results.get('execution_time', 0.0),
        
        # Raw results for detailed analysis
        "test_details": test_results,
        "pylint_details": pylint_results
    }


def compare_quality(before_score: float, after_score: float) -> Dict:
    """
    Compare code quality before and after refactoring.
    
    Args:
        before_score: Pylint score before fixes
        after_score: Pylint score after fixes
        
    Returns:
        Dict with comparison metrics
    """
    improvement = after_score - before_score
    improvement_percentage = (improvement / before_score * 100) if before_score > 0 else 0
    
    return {
        "improved": improvement > 0,
        "improvement": round(improvement, 2),
        "improvement_percentage": round(improvement_percentage, 1),
        "before": before_score,
        "after": after_score,
        "verdict": _get_verdict(improvement, after_score)
    }


def _get_verdict(improvement: float, final_score: float) -> str:
    """
    Get a human-readable verdict on the refactoring.
    
    Args:
        improvement: Score improvement
        final_score: Final Pylint score
        
    Returns:
        Verdict string
    """
    if final_score >= 9.0:
        return "Excellent - Code quality is exceptional"
    elif final_score >= 7.0 and improvement > 0:
        return "Good - Significant improvement achieved"
    elif improvement > 0:
        return "Acceptable - Some improvement made"
    elif improvement == 0:
        return "No Change - No quality improvement"
    else:
        return "Regression - Code quality decreased"


def check_critical_failures(test_results: Dict) -> List[str]:
    """
    Identify critical test failures that must be fixed.
    
    Args:
        test_results: Results from evaluate_code()
        
    Returns:
        List of critical failure descriptions
    """
    critical = []
    
    if not test_results['passed']:
        # Check for syntax errors
        for error in test_results.get('errors', []):
            error_str = str(error).lower()
            if 'syntaxerror' in error_str or 'indentationerror' in error_str:
                critical.append(f"CRITICAL: Syntax error detected - {error}")
        
        # Check for import errors
        for error in test_results.get('errors', []):
            error_str = str(error).lower()
            if 'importerror' in error_str or 'modulenotfounderror' in error_str:
                critical.append(f"CRITICAL: Import error - {error}")
    
    return critical


def format_test_feedback_for_fixer(test_results: Dict, max_errors: int = 5) -> str:
    """
    Format test results into feedback for the Fixer agent.
    This helps the Fixer understand what went wrong.
    
    Args:
        test_results: Results from evaluate_code()
        max_errors: Maximum number of errors to include
        
    Returns:
        Formatted feedback string for the Fixer's LLM
    """
    if test_results['passed']:
        return "✅ All tests passed! No fixes needed."
    
    feedback_parts = []
    
    # Summary
    feedback_parts.append(
        f"❌ Tests Failed: {test_results['failed_tests']}/{test_results['test_count']}"
    )
    
    # Critical issues first
    critical = check_critical_failures(test_results)
    if critical:
        feedback_parts.append("\n🚨 CRITICAL ISSUES (must fix first):")
        for issue in critical:
            feedback_parts.append(f"  - {issue}")
    
    # Test failures
    errors = test_results.get('errors', [])
    if errors:
        feedback_parts.append(f"\n⚠️ Test Errors (showing top {min(len(errors), max_errors)}):")
        for i, error in enumerate(errors[:max_errors], 1):
            # Truncate very long error messages
            error_str = str(error)
            if len(error_str) > 200:
                error_str = error_str[:200] + "..."
            feedback_parts.append(f"{i}. {error_str}")
    
    # Quality score
    if 'pylint_score' in test_results:
        score = test_results['pylint_score']
        feedback_parts.append(f"\n📊 Current Pylint Score: {score:.2f}/10")
        
        if score < 5.0:
            feedback_parts.append("   ⚠️ Score is below acceptable threshold (5.0)")
    
    return "\n".join(feedback_parts)


def should_continue_fixing(
    iteration: int,
    max_iterations: int,
    test_results: Dict,
    improvement_history: List[float]
) -> tuple[bool, str]:
    """
    Determine if the fixing loop should continue.
    
    Args:
        iteration: Current iteration number
        max_iterations: Maximum allowed iterations
        test_results: Latest test results
        improvement_history: List of Pylint scores from previous iterations
        
    Returns:
        Tuple of (should_continue: bool, reason: str)
    """
    # Check if tests pass
    if test_results['passed']:
        return False, "All tests passed"
    
    # Check iteration limit
    if iteration >= max_iterations:
        return False, f"Maximum iterations ({max_iterations}) reached"
    
    # Check for stagnation (no improvement in last 3 iterations)
    if len(improvement_history) >= 3:
        recent_scores = improvement_history[-3:]
        if max(recent_scores) - min(recent_scores) < 0.1:
            return False, "No improvement detected in last 3 iterations"
    
    # Continue fixing
    return True, "Tests still failing, continuing fixes"


# Example usage
if __name__ == "__main__":
    import tempfile
    import shutil
    from pathlib import Path
    
    print("🧪 Testing Judge Toolkit...")
    
    # Create a temporary directory with test files
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create a simple Python file
        code_file = Path(temp_dir) / "example.py"
        code_file.write_text("""
def add(a: int, b: int) -> int:
    \"\"\"Add two numbers.\"\"\"
    return a + b

def subtract(a: int, b: int) -> int:
    \"\"\"Subtract b from a.\"\"\"
    return a - b
""")
        
        # Create a test file
        test_file = Path(temp_dir) / "test_example.py"
        test_file.write_text("""
from example import add, subtract

def test_add():
    assert add(2, 3) == 5

def test_subtract():
    assert subtract(5, 3) == 2

def test_failing():
    assert add(1, 1) == 3  # This will fail
""")
        
        print(f"✅ Created test files in: {temp_dir}")
        
        # Evaluate the code
        results = evaluate_code(temp_dir)
        
        print(f"\n📊 Evaluation Results:")
        print(f"  Tests Passed: {results['passed']}")
        print(f"  Test Count: {results['test_count']}")
        print(f"  Failed Tests: {results['failed_tests']}")
        print(f"  Pylint Score: {results['pylint_score']:.2f}/10")
        
        # Format feedback
        feedback = format_test_feedback_for_fixer(results)
        print(f"\n💬 Feedback for Fixer:")
        print(feedback)
        
        # Compare quality (simulated)
        comparison = compare_quality(5.0, results['pylint_score'])
        print(f"\n📈 Quality Comparison:")
        print(f"  Improved: {comparison['improved']}")
        print(f"  Improvement: {comparison['improvement']}")
        print(f"  Verdict: {comparison['verdict']}")
        
        # Check if should continue
        should_cont, reason = should_continue_fixing(1, 10, results, [5.0])
        print(f"\n🔄 Continue Fixing: {should_cont}")
        print(f"   Reason: {reason}")
        
        print("\n✅ Judge toolkit is ready!")
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)