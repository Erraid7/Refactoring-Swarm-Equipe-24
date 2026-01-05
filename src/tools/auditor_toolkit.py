"""
Auditor Toolkit
High-level API specifically designed for the Auditor agent.
Conforms to the interface contract defined in docs/interfaces.md
"""

from typing import Dict, List
from src.tools.file_operations import scan_python_files
from src.tools.analysis import run_pylint_analysis, run_pylint_on_directory


def analyze_project(target_dir: str) -> Dict:
    """
    Analyze an entire project and return data in the format expected by RefactoringState.
    
    This is the main function the Auditor agent should call.
    
    Args:
        target_dir: Path to the project directory
        
    Returns:
        Dict matching the audit_report format from interfaces.md:
        {
            "pylint_score": float,      # Average score across all files
            "issues": [...],            # List of all issues found
            "plan": [...],              # Will be filled by LLM, but we provide issues
            "files_analyzed": [...]     # List of files that were analyzed
        }
    """
    # Step 1: Find all Python files
    files = scan_python_files(target_dir)
    
    if not files:
        return {
            "pylint_score": 0.0,
            "issues": [],
            "plan": [],
            "files_analyzed": []
        }
    
    # Step 2: Run comprehensive analysis
    analysis = run_pylint_on_directory(target_dir)
    
    # Step 3: Extract and format issues for the LLM
    all_issues = []
    
    for filepath, file_data in analysis['file_scores'].items():
        if 'error' not in file_data:
            # Get detailed issues for this file
            file_analysis = run_pylint_analysis(filepath)
            
            # Format issues in a simple, LLM-friendly way
            for issue in file_analysis['issues']:
                all_issues.append({
                    "file": filepath,
                    "line": issue['line'],
                    "type": issue['type'],
                    "message": issue['message'],
                    "severity": _categorize_severity(issue['type'])
                })
    
    # Step 4: Prioritize critical issues
    critical_issues = [i for i in all_issues if i['severity'] == 'critical']
    high_issues = [i for i in all_issues if i['severity'] == 'high']
    
    # Step 5: Return in the expected format
    return {
        "pylint_score": analysis['average_score'],
        "issues": all_issues,
        "critical_issues": critical_issues,  # Extra field for LLM to prioritize
        "high_issues": high_issues,
        "plan": [],  # Will be filled by the Auditor's LLM
        "files_analyzed": files,
        "total_files": len(files),
        "total_issues": analysis['total_issues']
    }


def get_files_to_analyze(target_dir: str) -> List[str]:
    """
    Get the list of Python files to analyze.
    This populates the 'files_to_analyze' field in RefactoringState.
    
    Args:
        target_dir: Path to the project directory
        
    Returns:
        List of file paths
    """
    return scan_python_files(target_dir)


def get_file_content(filepath: str, target_dir: str) -> str:
    """
    Get the content of a specific file for the LLM to analyze.
    
    Args:
        filepath: Path to the file
        target_dir: Sandbox root directory
        
    Returns:
        File content as string
    """
    from src.tools.file_operations import read_file_safe
    return read_file_safe(filepath, target_dir)


def get_critical_files(target_dir: str, threshold: float = 5.0) -> List[str]:
    """
    Get files that have a Pylint score below the threshold.
    These are the files that need immediate attention.
    
    Args:
        target_dir: Path to the project directory
        threshold: Minimum acceptable score (default: 5.0)
        
    Returns:
        List of file paths with low scores
    """
    analysis = run_pylint_on_directory(target_dir)
    critical_files = []
    
    for filepath, data in analysis['file_scores'].items():
        if 'score' in data and data['score'] < threshold:
            critical_files.append(filepath)
    
    return critical_files


def _categorize_severity(issue_type: str) -> str:
    """
    Categorize issue type into severity levels.
    
    Args:
        issue_type: Pylint issue type (error, warning, convention, refactor)
        
    Returns:
        Severity level: critical, high, medium, low
    """
    severity_map = {
        'error': 'critical',
        'fatal': 'critical',
        'warning': 'high',
        'refactor': 'medium',
        'convention': 'low'
    }
    
    return severity_map.get(issue_type, 'medium')


def format_issues_for_llm(issues: List[Dict], max_issues: int = 10) -> str:
    """
    Format issues in a way that's easy for the LLM to understand.
    
    Args:
        issues: List of issue dictionaries
        max_issues: Maximum number of issues to include (to avoid token overflow)
        
    Returns:
        Formatted string for LLM prompt
    """
    if not issues:
        return "No issues found."
    
    # Prioritize by severity
    sorted_issues = sorted(issues, key=lambda x: (
        x['severity'] == 'critical',
        x['severity'] == 'high',
        x['severity'] == 'medium',
        x['severity'] == 'low'
    ), reverse=True)
    
    # Take top N issues
    top_issues = sorted_issues[:max_issues]
    
    formatted = []
    for i, issue in enumerate(top_issues, 1):
        formatted.append(
            f"{i}. [{issue['severity'].upper()}] {issue['file']}:{issue['line']}\n"
            f"   Type: {issue['type']}\n"
            f"   Message: {issue['message']}"
        )
    
    if len(issues) > max_issues:
        formatted.append(f"\n... and {len(issues) - max_issues} more issues")
    
    return "\n\n".join(formatted)


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python auditor_toolkit.py <target_dir>")
        sys.exit(1)
    
    target_dir = sys.argv[1]
    
    print(f"🔍 Analyzing project: {target_dir}\n")
    
    # Main analysis function
    result = analyze_project(target_dir)
    
    print(f"📊 Analysis Results:")
    print(f"  Average Pylint Score: {result['pylint_score']:.2f}/10")
    print(f"  Files Analyzed: {result['total_files']}")
    print(f"  Total Issues: {result['total_issues']}")
    print(f"  Critical Issues: {len(result['critical_issues'])}")
    print(f"  High Priority Issues: {len(result['high_issues'])}")
    
    if result['critical_issues']:
        print(f"\n🚨 Critical Issues:")
        for issue in result['critical_issues'][:5]:
            print(f"  - {issue['file']}:{issue['line']} - {issue['message']}")
    
    # Show formatted output for LLM
    print(f"\n📝 Formatted for LLM:")
    print(format_issues_for_llm(result['issues'], max_issues=5))