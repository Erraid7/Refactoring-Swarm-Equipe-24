"""Unit tests for tools"""
import pytest
import tempfile
import shutil
from pathlib import Path

from src.tools.file_operations import scan_python_files, read_file_safe, write_file_safe
from src.tools.sandbox_security import SandboxManager, SandboxViolationError


class TestFileOperations:
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        shutil.rmtree(self.temp_dir)
    
    def test_scan_python_files(self):
        # Create test files
        Path(self.temp_dir, "file1.py").write_text("# code")
        Path(self.temp_dir, "file2.py").write_text("# code")
        
        files = scan_python_files(self.temp_dir)
        assert len(files) == 2
    
    def test_read_write_file(self):
        test_file = str(Path(self.temp_dir, "test.py"))
        content = "print('hello')"
        
        write_file_safe(test_file, content, self.temp_dir)
        read_content = read_file_safe(test_file, self.temp_dir)
        
        assert read_content == content


class TestSandboxSecurity:
    def setup_method(self):
        self.sandbox_dir = tempfile.mkdtemp()
        self.sandbox = SandboxManager(self.sandbox_dir)
    
    def teardown_method(self):
        shutil.rmtree(self.sandbox_dir)
    
    def test_valid_path(self):
        test_file = str(Path(self.sandbox_dir, "test.py"))
        validated = self.sandbox.validate_path(test_file)
        assert validated.is_relative_to(Path(self.sandbox_dir))
    
    def test_directory_traversal_blocked(self):
        dangerous_path = str(Path(self.sandbox_dir, "../outside.py"))
        with pytest.raises(SandboxViolationError):
            self.sandbox.validate_path(dangerous_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])