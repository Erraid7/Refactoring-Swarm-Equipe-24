"""
File Operations Module
Provides safe file reading/writing operations for the refactoring swarm.
"""

import os
from pathlib import Path
from typing import List


def scan_python_files(directory: str) -> List[str]:
    """
    Scan a directory and return all Python files.
    
    Args:
        directory: Path to the directory to scan
        
    Returns:
        List of absolute paths to .py files
        
    Raises:
        ValueError: If directory doesn't exist
    """
    dir_path = Path(directory)
    
    if not dir_path.exists():
        raise ValueError(f"Directory does not exist: {directory}")
    
    if not dir_path.is_dir():
        raise ValueError(f"Path is not a directory: {directory}")
    
    # Find all .py files recursively
    python_files = []
    for py_file in dir_path.rglob("*.py"):
        # Skip __pycache__ and virtual environments
        if "__pycache__" not in str(py_file) and "venv" not in str(py_file):
            python_files.append(str(py_file.absolute()))
    
    return sorted(python_files)


def read_file_safe(filepath: str, sandbox_root: str) -> str:
    """
    Read a file safely with path validation.
    
    Args:
        filepath: Path to the file to read
        sandbox_root: Root directory (all operations must stay within this)
        
    Returns:
        Content of the file as string
        
    Raises:
        ValueError: If path is outside sandbox or file doesn't exist
        IOError: If file cannot be read
    """
    # Validate path is within sandbox
    if not _is_safe_path(filepath, sandbox_root):
        raise ValueError(f"Path outside sandbox: {filepath}")
    
    file_path = Path(filepath)
    
    if not file_path.exists():
        raise ValueError(f"File does not exist: {filepath}")
    
    if not file_path.is_file():
        raise ValueError(f"Path is not a file: {filepath}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        raise IOError(f"Failed to read file {filepath}: {e}")


def write_file_safe(filepath: str, content: str, sandbox_root: str) -> bool:
    """
    Write content to a file safely with path validation.
    
    Args:
        filepath: Path to the file to write
        content: Content to write
        sandbox_root: Root directory (all operations must stay within this)
        
    Returns:
        True if successful
        
    Raises:
        ValueError: If path is outside sandbox
        IOError: If file cannot be written
    """
    # Validate path is within sandbox
    if not _is_safe_path(filepath, sandbox_root):
        raise ValueError(f"Path outside sandbox: {filepath}")
    
    file_path = Path(filepath)
    
    # Create parent directories if needed
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        raise IOError(f"Failed to write file {filepath}: {e}")


def _is_safe_path(filepath: str, sandbox_root: str) -> bool:
    """
    Check if a path is within the sandbox directory.
    Prevents directory traversal attacks (../ paths).
    
    Args:
        filepath: Path to validate
        sandbox_root: Root directory
        
    Returns:
        True if path is safe
    """
    # Resolve to absolute paths
    real_filepath = Path(filepath).resolve()
    real_sandbox = Path(sandbox_root).resolve()
    
    # Check if filepath starts with sandbox_root
    try:
        real_filepath.relative_to(real_sandbox)
        return True
    except ValueError:
        return False


def list_files_in_directory(directory: str, extension: str = ".py") -> List[str]:
    """
    List all files with a specific extension in a directory.
    
    Args:
        directory: Path to directory
        extension: File extension to filter (default: .py)
        
    Returns:
        List of file paths
    """
    dir_path = Path(directory)
    
    if not dir_path.exists() or not dir_path.is_dir():
        return []
    
    files = []
    for file in dir_path.iterdir():
        if file.is_file() and file.suffix == extension:
            files.append(str(file.absolute()))
    
    return sorted(files)


# Example usage and tests
if __name__ == "__main__":
    print("🧪 Testing File Operations...")
    
    # Test 1: Scan Python files
    try:
        files = scan_python_files("./src")
        print(f"✅ Found {len(files)} Python files in src/")
    except Exception as e:
        print(f"❌ Scan failed: {e}")
    
    # Test 2: Safe path validation
    print("\n🔒 Testing path security...")
    test_cases = [
        ("./sandbox/test.py", "./sandbox", True),
        ("../outside.py", "./sandbox", False),
        ("./sandbox/../../../etc/passwd", "./sandbox", False),
    ]
    
    for filepath, sandbox, expected in test_cases:
        result = _is_safe_path(filepath, sandbox)
        status = "✅" if result == expected else "❌"
        print(f"{status} {filepath}: {result}")
    
    print("\n✅ File operations module is ready!")