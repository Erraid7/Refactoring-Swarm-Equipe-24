"""
Testing Module
Provides test execution capabilities using pytest.
"""

import subprocess
import json
from pathlib import Path
from typing import Dict, List


def run_pytest(directory: str, timeout: int = 60) -> Dict:
    """
    Run pytest on a directory and return results.
    
    Args:
        directory: Path to directory containing tests
        timeout: Maximum execution time in seconds (default: 60)
        
    Returns:
        Dict containing:
        - passed: Boolean indicating if all tests passed
        - total: Total number of tests
        - passed_count: Number of passed tests
        - failed_count: Number of failed tests
        - failures: List of failure details
        - errors: List of errors
        - execution_time: Time taken to run tests
        
    Raises:
        ValueError: If directory doesn't exist
        RuntimeError: If pytest execution fails
    """
    dir_path = Path(directory)
    
    if not dir_path.exists():
        raise ValueError(f"Directory does not exist: {directory}")
    
    # Look for test files
    test_files = list(dir_path.rglob("test_*.py")) + list(dir_path.rglob("*_test.py"))
    
    if not test_files:
        return {
            'passed': True,
            'total': 0,
            'passed_count': 0,
            'failed_count': 0,
            'failures': [],
            'errors': [],
            'execution_time': 0.0,
            'message': 'No test files found'
        }
    
    try:
        # Run pytest with JSON report
        result = subprocess.run(
            [
                "pytest",
                str(directory),
                "--tb=short",  # Short traceback format
                "-v",  # Verbose
                "--json-report",  # JSON output
                "--json-report-file=/tmp/pytest_report.json"
            ],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        # Try to load JSON report
        report_path = Path("/tmp/pytest_report.json")
        if report_path.exists():
            with open(report_path, 'r') as f:
                report = json.load(f)
            
            return _parse_pytest_json_report(report)
        else:
            # Fallback to parsing text output
            return _parse_pytest_text_output(result.stdout, result.stderr, result.returncode)
        
    except subprocess.TimeoutExpired:
        return {
            'passed': False,
            'total': 0,
            'passed_count': 0,
            'failed_count': 0,
            'failures': [],
            'errors': ["Test execution timed out"],
            'execution_time': timeout,
            'message': 'Timeout'
        }
    except Exception as e:
        raise RuntimeError(f"Pytest execution failed: {e}")


def _parse_pytest_json_report(report: Dict) -> Dict:
    """
    Parse pytest JSON report.
    
    Args:
        report: JSON report from pytest
        
    Returns:
        Formatted test results
    """
    summary = report.get('summary', {})
    tests = report.get('tests', [])
    
    passed_count = summary.get('passed', 0)
    failed_count = summary.get('failed', 0)
    error_count = summary.get('error', 0)
    total = summary.get('total', 0)
    
    failures = []
    errors = []
    
    for test in tests:
        if test.get('outcome') == 'failed':
            failures.append({
                'test': test.get('nodeid', ''),
                'message': test.get('call', {}).get('longrepr', 'No details'),
                'line': test.get('lineno', 0)
            })
        elif test.get('outcome') == 'error':
            errors.append({
                'test': test.get('nodeid', ''),
                'message': str(test.get('setup', {}).get('longrepr', 'Setup error'))
            })
    
    return {
        'passed': failed_count == 0 and error_count == 0,
        'total': total,
        'passed_count': passed_count,
        'failed_count': failed_count,
        'error_count': error_count,
        'failures': failures,
        'errors': errors,
        'execution_time': report.get('duration', 0.0)
    }


def _parse_pytest_text_output(stdout: str, stderr: str, returncode: int) -> Dict:
    """
    Parse pytest text output (fallback method).
    
    Args:
        stdout: Standard output from pytest
        stderr: Standard error from pytest
        returncode: Exit code
        
    Returns:
        Formatted test results
    """
    lines = stdout.split('\n')
    
    # Look for summary line: "X passed, Y failed in Z seconds"
    passed_count = 0
    failed_count = 0
    total = 0
    
    for line in lines:
        if 'passed' in line.lower() or 'failed' in line.lower():
            # Try to extract numbers
            import re
            passed_match = re.search(r'(\d+) passed', line)
            failed_match = re.search(r'(\d+) failed', line)
            
            if passed_match:
                passed_count = int(passed_match.group(1))
            if failed_match:
                failed_count = int(failed_match.group(1))
    
    total = passed_count + failed_count
    
    # Extract failures
    failures = []
    in_failure = False
    current_failure = {}
    
    for line in lines:
        if 'FAILED' in line:
            in_failure = True
            current_failure = {'test': line.strip(), 'message': ''}
        elif in_failure:
            if line.strip().startswith('=') or line.strip().startswith('_'):
                if current_failure.get('test'):
                    failures.append(current_failure)
                in_failure = False
                current_failure = {}
            else:
                current_failure['message'] += line + '\n'
    
    return {
        'passed': returncode == 0,
        'total': total,
        'passed_count': passed_count,
        'failed_count': failed_count,
        'failures': failures,
        'errors': [stderr] if stderr else [],
        'execution_time': 0.0
    }


def find_test_files(directory: str) -> List[str]:
    """
    Find all test files in a directory.
    
    Args:
        directory: Path to search
        
    Returns:
        List of test file paths
    """
    dir_path = Path(directory)
    
    if not dir_path.exists():
        return []
    
    test_files = []
    
    # Find test_*.py files
    test_files.extend(dir_path.rglob("test_*.py"))
    
    # Find *_test.py files
    test_files.extend(dir_path.rglob("*_test.py"))
    
    return [str(f.absolute()) for f in test_files]


def check_test_exists(directory: str) -> bool:
    """
    Check if a directory contains any test files.
    
    Args:
        directory: Path to check
        
    Returns:
        True if test files exist
    """
    return len(find_test_files(directory)) > 0


# Example usage and tests
if __name__ == "__main__":
    import tempfile
    import os
    
    print("🧪 Testing Test Execution Module...")
    
    # Create a temporary directory with a test file
    temp_dir = tempfile.mkdtemp()
    
    # Create a simple test file
    test_code = '''
import pytest

def test_addition():
    assert 1 + 1 == 2

def test_subtraction():
    assert 5 - 3 == 2

def test_failing():
    assert 1 + 1 == 3  # This will fail
'''
    
    test_file = Path(temp_dir) / "test_example.py"
    test_file.write_text(test_code)
    
    try:
        print(f"\n📂 Created test in: {temp_dir}")
        
        # Run tests
        result = run_pytest(temp_dir)
        
        print(f"\n📊 Test Results:")
        print(f"  Total: {result['total']}")
        print(f"  Passed: {result['passed_count']}")
        print(f"  Failed: {result['failed_count']}")
        print(f"  All Passed: {result['passed']}")
        
        if result['failures']:
            print(f"\n❌ Failures:")
            for failure in result['failures']:
                print(f"  - {failure['test']}")
                print(f"    {failure['message'][:100]}...")
        
        print("\n✅ Testing module is ready!")
        
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)