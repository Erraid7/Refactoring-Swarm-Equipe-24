"""
Fixer Toolkit
High-level API specifically designed for the Fixer agent.
Conforms to the interface contract defined in docs/interfaces.md
"""

from typing import Dict, List
from pathlib import Path
from src.tools.file_operations import read_file_safe, write_file_safe


def apply_fixes(fixed_files_data: Dict, target_dir: str) -> Dict:
    """
    Apply fixes from the LLM to actual files.
    
    This function receives the output from the Fixer agent's LLM
    and applies the changes to the file system.
    
    Args:
        fixed_files_data: Dict in the format from interfaces.md:
            {"files": [{"path": str, "content": str}, ...]}
        target_dir: Sandbox root directory
        
    Returns:
        Dict with application results:
        {
            "success": bool,
            "files_modified": List[str],
            "errors": List[str]
        }
    """
    if not isinstance(fixed_files_data, dict) or 'files' not in fixed_files_data:
        return {
            "success": False,
            "files_modified": [],
            "errors": ["Invalid fixed_files_data format. Expected: {'files': [...]}"]
        }
    
    files_modified = []
    errors = []
    
    for file_data in fixed_files_data['files']:
        try:
            filepath = file_data['path']
            new_content = file_data['content']
            
            # Write the fixed content
            write_file_safe(filepath, new_content, target_dir)
            files_modified.append(filepath)
            
        except KeyError as e:
            errors.append(f"Missing key in file_data: {e}")
        except Exception as e:
            errors.append(f"Failed to write {file_data.get('path', 'unknown')}: {e}")
    
    return {
        "success": len(errors) == 0,
        "files_modified": files_modified,
        "errors": errors
    }


def get_files_for_fixing(files_to_fix: List[str], target_dir: str) -> Dict[str, str]:
    """
    Read multiple files and return their contents.
    Used by the Fixer to get the current code before fixing.
    
    Args:
        files_to_fix: List of file paths
        target_dir: Sandbox root directory
        
    Returns:
        Dict mapping file paths to their contents
    """
    file_contents = {}
    
    for filepath in files_to_fix:
        try:
            content = read_file_safe(filepath, target_dir)
            file_contents[filepath] = content
        except Exception as e:
            print(f"⚠️  Failed to read {filepath}: {e}")
            file_contents[filepath] = None
    
    return file_contents


def prepare_context_for_fixer(
    files_to_fix: List[str],
    audit_report: Dict,
    target_dir: str,
    max_files: int = 3
) -> Dict:
    """
    Prepare the context that will be sent to the Fixer's LLM.
    
    This limits the amount of code sent to avoid token overflow.
    
    Args:
        files_to_fix: List of files that need fixing
        audit_report: The audit report from the Auditor
        target_dir: Sandbox root directory
        max_files: Maximum number of files to include (default: 3)
        
    Returns:
        Dict with:
        - files: Dict mapping paths to contents (limited to max_files)
        - issues: Relevant issues for these files
        - plan: The refactoring plan from audit
    """
    # Limit to most critical files
    limited_files = files_to_fix[:max_files]
    
    # Get file contents
    file_contents = get_files_for_fixing(limited_files, target_dir)
    
    # Extract issues relevant to these files
    relevant_issues = []
    if 'issues' in audit_report:
        for issue in audit_report['issues']:
            if issue.get('file') in limited_files:
                relevant_issues.append(issue)
    
    return {
        "files": file_contents,
        "issues": relevant_issues,
        "plan": audit_report.get('plan', []),
        "total_files_to_fix": len(files_to_fix),
        "currently_fixing": len(limited_files)
    }


def create_backup(filepath: str, target_dir: str) -> str:
    """
    Create a backup of a file before modifying it.
    
    Args:
        filepath: Path to the file
        target_dir: Sandbox root directory
        
    Returns:
        Path to the backup file
    """
    from datetime import datetime
    
    content = read_file_safe(filepath, target_dir)
    
    # Create backup filename with timestamp
    file_path = Path(filepath)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{file_path.stem}_backup_{timestamp}{file_path.suffix}"
    backup_path = file_path.parent / backup_name
    
    # Write backup
    write_file_safe(str(backup_path), content, target_dir)
    
    return str(backup_path)


def validate_python_syntax(filepath: str, target_dir: str) -> Dict:
    """
    Validate that a Python file has correct syntax after fixing.
    
    Args:
        filepath: Path to the file
        target_dir: Sandbox root directory
        
    Returns:
        Dict with:
        - valid: bool
        - error: str (if invalid)
    """
    import ast
    
    try:
        content = read_file_safe(filepath, target_dir)
        ast.parse(content)
        return {"valid": True, "error": None}
    except SyntaxError as e:
        return {
            "valid": False,
            "error": f"Syntax error at line {e.lineno}: {e.msg}"
        }
    except Exception as e:
        return {
            "valid": False,
            "error": str(e)
        }


def format_files_for_llm(file_contents: Dict[str, str], max_lines_per_file: int = 100) -> str:
    """
    Format file contents for inclusion in LLM prompt.
    Truncates very long files to avoid token overflow.
    
    Args:
        file_contents: Dict mapping file paths to contents
        max_lines_per_file: Maximum lines to include per file
        
    Returns:
        Formatted string for LLM prompt
    """
    formatted_parts = []
    
    for filepath, content in file_contents.items():
        if content is None:
            formatted_parts.append(f"### {filepath} ###\n[ERROR: Could not read file]")
            continue
        
        lines = content.split('\n')
        
        if len(lines) > max_lines_per_file:
            truncated_content = '\n'.join(lines[:max_lines_per_file])
            truncated_content += f"\n... [Truncated {len(lines) - max_lines_per_file} lines]"
        else:
            truncated_content = content
        
        formatted_parts.append(
            f"### {filepath} ###\n"
            f"```python\n{truncated_content}\n```"
        )
    
    return "\n\n".join(formatted_parts)


# Example usage
if __name__ == "__main__":
    import tempfile
    import shutil
    
    print("🔧 Testing Fixer Toolkit...")
    
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create a test file
        test_file = str(Path(temp_dir) / "example.py")
        original_content = "def bad_function(x,y):\n    return x+y\n"
        
        with open(test_file, 'w') as f:
            f.write(original_content)
        
        print(f"✅ Created test file: {test_file}")
        
        # Simulate Fixer output
        fixed_files_data = {
            "files": [
                {
                    "path": test_file,
                    "content": "def good_function(x: int, y: int) -> int:\n    \"\"\"Add two numbers.\"\"\"\n    return x + y\n"
                }
            ]
        }
        
        # Apply fixes
        result = apply_fixes(fixed_files_data, temp_dir)
        
        print(f"\n📊 Apply Fixes Result:")
        print(f"  Success: {result['success']}")
        print(f"  Files Modified: {len(result['files_modified'])}")
        print(f"  Errors: {len(result['errors'])}")
        
        # Validate syntax
        validation = validate_python_syntax(test_file, temp_dir)
        print(f"\n✅ Syntax Validation:")
        print(f"  Valid: {validation['valid']}")
        
        if not validation['valid']:
            print(f"  Error: {validation['error']}")
        
        print("\n✅ Fixer toolkit is ready!")
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)