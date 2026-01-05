"""
Sandbox Security Module
Ensures all file operations stay within the designated sandbox directory.
"""

import os
from pathlib import Path
from typing import Optional


class SandboxViolationError(Exception):
    """Raised when an operation attempts to access files outside the sandbox."""
    pass


class SandboxManager:
    """
    Manages sandbox security for file operations.
    Prevents directory traversal attacks and ensures all operations
    stay within the designated safe zone.
    """
    
    def __init__(self, sandbox_root: str):
        """
        Initialize sandbox manager.
        
        Args:
            sandbox_root: Root directory for all operations
            
        Raises:
            ValueError: If sandbox_root doesn't exist
        """
        self.sandbox_root = Path(sandbox_root).resolve()
        
        if not self.sandbox_root.exists():
            raise ValueError(f"Sandbox root does not exist: {sandbox_root}")
        
        if not self.sandbox_root.is_dir():
            raise ValueError(f"Sandbox root is not a directory: {sandbox_root}")
    
    def validate_path(self, filepath: str) -> Path:
        """
        Validate that a path is within the sandbox.
        
        Args:
            filepath: Path to validate
            
        Returns:
            Resolved Path object if valid
            
        Raises:
            SandboxViolationError: If path is outside sandbox
        """
        # Resolve to absolute path
        try:
            resolved_path = Path(filepath).resolve()
        except Exception as e:
            raise SandboxViolationError(f"Invalid path: {filepath} ({e})")
        
        # Check if path is within sandbox
        try:
            resolved_path.relative_to(self.sandbox_root)
        except ValueError:
            raise SandboxViolationError(
                f"Path outside sandbox: {filepath}\n"
                f"Sandbox root: {self.sandbox_root}\n"
                f"Attempted path: {resolved_path}"
            )
        
        return resolved_path
    
    def safe_read(self, filepath: str) -> str:
        """
        Safely read a file within the sandbox.
        
        Args:
            filepath: Path to file
            
        Returns:
            File content
            
        Raises:
            SandboxViolationError: If path is invalid
            IOError: If file cannot be read
        """
        validated_path = self.validate_path(filepath)
        
        if not validated_path.exists():
            raise IOError(f"File does not exist: {filepath}")
        
        if not validated_path.is_file():
            raise IOError(f"Path is not a file: {filepath}")
        
        try:
            return validated_path.read_text(encoding='utf-8')
        except Exception as e:
            raise IOError(f"Failed to read {filepath}: {e}")
    
    def safe_write(self, filepath: str, content: str) -> None:
        """
        Safely write to a file within the sandbox.
        
        Args:
            filepath: Path to file
            content: Content to write
            
        Raises:
            SandboxViolationError: If path is invalid
            IOError: If file cannot be written
        """
        validated_path = self.validate_path(filepath)
        
        # Create parent directories if needed
        validated_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            validated_path.write_text(content, encoding='utf-8')
        except Exception as e:
            raise IOError(f"Failed to write {filepath}: {e}")
    
    def safe_delete(self, filepath: str) -> None:
        """
        Safely delete a file within the sandbox.
        
        Args:
            filepath: Path to file
            
        Raises:
            SandboxViolationError: If path is invalid
        """
        validated_path = self.validate_path(filepath)
        
        if validated_path.exists():
            validated_path.unlink()
    
    def list_files(self, pattern: str = "*.py") -> list[str]:
        """
        List files in the sandbox matching a pattern.
        
        Args:
            pattern: Glob pattern (default: *.py)
            
        Returns:
            List of file paths
        """
        files = []
        for file_path in self.sandbox_root.rglob(pattern):
            if file_path.is_file():
                # Exclude __pycache__ and other system directories
                if "__pycache__" not in str(file_path) and ".git" not in str(file_path):
                    files.append(str(file_path))
        
        return sorted(files)
    
    def get_relative_path(self, filepath: str) -> str:
        """
        Get path relative to sandbox root.
        
        Args:
            filepath: Absolute or relative path
            
        Returns:
            Path relative to sandbox root
        """
        validated_path = self.validate_path(filepath)
        return str(validated_path.relative_to(self.sandbox_root))
    
    def create_subdirectory(self, dirname: str) -> Path:
        """
        Create a subdirectory within the sandbox.
        
        Args:
            dirname: Name of subdirectory
            
        Returns:
            Path to created directory
        """
        new_dir = self.sandbox_root / dirname
        validated_path = self.validate_path(str(new_dir))
        validated_path.mkdir(parents=True, exist_ok=True)
        return validated_path


def is_safe_path(filepath: str, sandbox_root: str) -> bool:
    """
    Quick check if a path is safe without raising exceptions.
    
    Args:
        filepath: Path to check
        sandbox_root: Root directory
        
    Returns:
        True if path is within sandbox
    """
    try:
        resolved_path = Path(filepath).resolve()
        resolved_sandbox = Path(sandbox_root).resolve()
        
        resolved_path.relative_to(resolved_sandbox)
        return True
    except (ValueError, Exception):
        return False


def detect_dangerous_patterns(filepath: str) -> Optional[str]:
    """
    Detect potentially dangerous patterns in file paths.
    
    Args:
        filepath: Path to check
        
    Returns:
        Warning message if dangerous pattern detected, None otherwise
    """
    dangerous_patterns = [
        ("../", "Directory traversal attempt"),
        ("..\\", "Directory traversal attempt (Windows)"),
        ("/etc/", "System directory access"),
        ("/sys/", "System directory access"),
        ("/proc/", "System directory access"),
        ("C:\\Windows", "System directory access (Windows)"),
        ("~", "Home directory expansion"),
    ]
    
    for pattern, message in dangerous_patterns:
        if pattern in filepath:
            return f"⚠️  {message}: '{pattern}' in path"
    
    return None


# Example usage and tests
if __name__ == "__main__":
    import tempfile
    import shutil
    
    print("🔒 Testing Sandbox Security...")
    
    # Create a temporary sandbox
    temp_sandbox = tempfile.mkdtemp()
    
    try:
        sandbox = SandboxManager(temp_sandbox)
        print(f"✅ Sandbox created at: {temp_sandbox}")
        
        # Test 1: Valid write
        print("\n🧪 Test 1: Valid write operation")
        test_file = os.path.join(temp_sandbox, "test.py")
        sandbox.safe_write(test_file, "print('Hello')")
        print("✅ Valid write succeeded")
        
        # Test 2: Valid read
        print("\n🧪 Test 2: Valid read operation")
        content = sandbox.safe_read(test_file)
        assert content == "print('Hello')"
        print("✅ Valid read succeeded")
        
        # Test 3: Invalid path (directory traversal)
        print("\n🧪 Test 3: Directory traversal attack")
        try:
            dangerous_path = os.path.join(temp_sandbox, "../outside.py")
            sandbox.safe_write(dangerous_path, "malicious")
            print("❌ Security breach! Should have been blocked")
        except SandboxViolationError as e:
            print(f"✅ Attack blocked: {str(e)[:50]}...")
        
        # Test 4: Absolute path outside sandbox
        print("\n🧪 Test 4: Absolute path outside sandbox")
        try:
            sandbox.safe_write("/tmp/outside.py", "malicious")
            print("❌ Security breach! Should have been blocked")
        except SandboxViolationError as e:
            print(f"✅ Attack blocked: {str(e)[:50]}...")
        
        # Test 5: Dangerous pattern detection
        print("\n🧪 Test 5: Dangerous pattern detection")
        test_paths = [
            "../../../etc/passwd",
            "C:\\Windows\\System32\\config",
            "~/secret.txt"
        ]
        
        for path in test_paths:
            warning = detect_dangerous_patterns(path)
            if warning:
                print(f"✅ Detected: {warning}")
        
        # Test 6: List files
        print("\n🧪 Test 6: List files")
        sandbox.safe_write(os.path.join(temp_sandbox, "file1.py"), "# code")
        sandbox.safe_write(os.path.join(temp_sandbox, "file2.py"), "# code")
        files = sandbox.list_files()
        print(f"✅ Found {len(files)} files")
        
        print("\n✅ All sandbox security tests passed!")
        
    finally:
        # Cleanup
        shutil.rmtree(temp_sandbox)
        print(f"\n🧹 Cleaned up sandbox")