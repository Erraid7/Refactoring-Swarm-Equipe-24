"""
Code Analysis Module
Provides code quality analysis using Pylint.
"""

import subprocess
import json
import sys
from pathlib import Path
from typing import Dict, List


def run_pylint_analysis(filepath: str) -> Dict:
    """
    Run Pylint analysis on a Python file.
    
    Args:
        filepath: Path to the Python file to analyze
        
    Returns:
        Dict containing:
        - score: Pylint score (0-10)
        - issues: List of detected issues
        - errors: List of errors
        - warnings: List of warnings
        - conventions: List of convention violations
        
    Raises:
        ValueError: If file doesn't exist or isn't a Python file
    """
    file_path = Path(filepath)
    
    # Validation
    if not file_path.exists():
        raise ValueError(f"File does not exist: {filepath}")
    
    if file_path.suffix != ".py":
        raise ValueError(f"Not a Python file: {filepath}")
    
    try:
        # Run pylint twice: once for JSON output (issues), once for score
        # First run: Get detailed issues in JSON format
        result_json = subprocess.run(
            [sys.executable, "-m", "pylint", str(file_path), "--output-format=json"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Second run: Get the score from text output
        result_score = subprocess.run(
            [sys.executable, "-m", "pylint", str(file_path)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Parse JSON output for issues
        issues = []
        if result_json.stdout:
            try:
                issues = json.loads(result_json.stdout)
            except json.JSONDecodeError:
                issues = []
        
        # Get score from the text output (stderr typically has the score line)
        score = _extract_score_from_output(result_score.stdout + "\n" + result_score.stderr)
        
        # Categorize issues
        errors = [i for i in issues if i.get('type') == 'error']
        warnings = [i for i in issues if i.get('type') == 'warning']
        conventions = [i for i in issues if i.get('type') == 'convention']
        refactors = [i for i in issues if i.get('type') == 'refactor']
        
        return {
            'score': score,
            'total_issues': len(issues),
            'issues': _format_issues(issues),
            'errors': _format_issues(errors),
            'warnings': _format_issues(warnings),
            'conventions': _format_issues(conventions),
            'refactors': _format_issues(refactors),
            'raw_issues': issues
        }
        
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"Pylint analysis timed out for {filepath}")
    except Exception as e:
        raise RuntimeError(f"Pylint analysis failed for {filepath}: {e}")


def run_pylint_on_directory(directory: str) -> Dict:
    """
    Run Pylint analysis on all Python files in a directory.
    
    Args:
        directory: Path to directory
        
    Returns:
        Dict containing:
        - average_score: Average Pylint score
        - file_scores: Dict mapping files to their scores
        - total_issues: Total number of issues found
        - critical_files: Files with score < 5
    """
    from src.tools.file_operations import scan_python_files
    
    dir_path = Path(directory)
    if not dir_path.exists():
        raise ValueError(f"Directory does not exist: {directory}")
    
    # Get all Python files
    python_files = scan_python_files(directory)
    
    if not python_files:
        return {
            'average_score': 0.0,
            'file_scores': {},
            'total_issues': 0,
            'critical_files': []
        }
    
    file_scores = {}
    total_score = 0.0
    total_issues = 0
    critical_files = []
    
    for filepath in python_files:
        try:
            analysis = run_pylint_analysis(filepath)
            score = analysis['score']
            
            file_scores[filepath] = {
                'score': score,
                'issues': analysis['total_issues']
            }
            
            total_score += score
            total_issues += analysis['total_issues']
            
            if score < 5.0:
                critical_files.append(filepath)
                
        except Exception as e:
            print(f"⚠️  Failed to analyze {filepath}: {e}")
            file_scores[filepath] = {
                'score': 0.0,
                'issues': 0,
                'error': str(e)
            }
    
    average_score = total_score / len(python_files) if python_files else 0.0
    
    return {
        'average_score': round(average_score, 2),
        'file_scores': file_scores,
        'total_issues': total_issues,
        'critical_files': critical_files,
        'files_analyzed': len(python_files)
    }


def _extract_score_from_output(output: str) -> float:
    """
    Extract Pylint score from stderr output.
    
    Args:
        output: Pylint stderr output
        
    Returns:
        Score as float (0-10)
    """
    # Pylint outputs: "Your code has been rated at X.XX/10"
    try:
        for line in output.split('\n'):
            if "rated at" in line:
                # Extract the score
                parts = line.split("rated at")[1].split("/")[0].strip()
                return float(parts)
    except:
        pass
    
    # Default to 0 if we can't parse
    return 0.0


def _format_issues(issues: List[Dict]) -> List[Dict]:
    """
    Format Pylint issues into a cleaner structure.
    
    Args:
        issues: Raw Pylint issues
        
    Returns:
        Formatted issues with essential information
    """
    formatted = []
    
    for issue in issues:
        formatted.append({
            'file': issue.get('path', ''),
            'line': issue.get('line', 0),
            'column': issue.get('column', 0),
            'type': issue.get('type', ''),
            'symbol': issue.get('symbol', ''),
            'message': issue.get('message', ''),
            'message_id': issue.get('message-id', '')
        })
    
    return formatted


def get_critical_issues(analysis_result: Dict) -> List[Dict]:
    """
    Extract only critical issues (errors) from analysis.
    
    Args:
        analysis_result: Result from run_pylint_analysis
        
    Returns:
        List of critical issues
    """
    return analysis_result.get('errors', [])


# Example usage and tests
if __name__ == "__main__":
    import tempfile
    import os
    
    print("🧪 Testing Code Analysis...")
    
    # Create a test file with intentional issues
    test_code = '''
def bad_function(x,y):
    z=x+y
    return z

print(bad_function(1,2))
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_code)
        test_file = f.name
    
    try:
        # Test analysis
        result = run_pylint_analysis(test_file)
        print(f"\n📊 Analysis Results:")
        print(f"  Score: {result['score']}/10")
        print(f"  Total Issues: {result['total_issues']}")
        print(f"  Errors: {len(result['errors'])}")
        print(f"  Warnings: {len(result['warnings'])}")
        print(f"  Conventions: {len(result['conventions'])}")
        
        if result['issues']:
            print(f"\n⚠️  Sample Issues:")
            for issue in result['issues'][:3]:
                print(f"  - Line {issue['line']}: {issue['message']}")
        
        print("\n✅ Code analysis module is ready!")
        
    finally:
        # Cleanup
        os.unlink(test_file)