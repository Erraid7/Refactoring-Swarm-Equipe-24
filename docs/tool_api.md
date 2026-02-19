# Tool API Documentation - Interface Compliant

## Overview

This API provides three high-level toolkits, one for each agent:
- **Auditor Toolkit**: For code analysis and issue detection
- **Fixer Toolkit**: For applying code fixes
- **Judge Toolkit**: For test execution and quality evaluation

All toolkits conform to the interface contract defined in `docs/interfaces.md`.

---

## Auditor Toolkit (`src/tools/auditor_toolkit.py`)

### `analyze_project(target_dir: str) -> Dict`

**Primary function for the Auditor agent.**

Analyzes an entire project and returns data in the format expected by `RefactoringState.audit_report`.

**Returns:**
```python
{
    "pylint_score": 6.5,           # Average score across all files
    "issues": [                     # All detected issues
        {
            "file": "path/to/file.py",
            "line": 42,
            "type": "error",
            "message": "undefined name 'x'",
            "severity": "critical"
        }
    ],
    "critical_issues": [...],       # Filtered critical issues
    "plan": [],                     # To be filled by LLM
    "files_analyzed": [...],
    "total_files": 5,
    "total_issues": 23
}
```

**Usage in Auditor Agent:**
```python
from src.tools.auditor_toolkit import analyze_project

# In Auditor.execute()
audit_report = analyze_project(state.target_dir)
state.audit_report = audit_report
state.files_to_analyze = audit_report['files_analyzed']
```

---

### `get_files_to_analyze(target_dir: str) -> List[str]`

Get list of Python files to populate `RefactoringState.files_to_analyze`.

---

### `format_issues_for_llm(issues: List[Dict], max_issues: int = 10) -> str`

Format issues for inclusion in LLM prompt (avoids token overflow).

---

## Fixer Toolkit (`src/tools/fixer_toolkit.py`)

### `apply_fixes(fixed_files_data: Dict, target_dir: str) -> Dict`

**Primary function for the Fixer agent.**

Applies fixes from LLM output to actual files.

**Input format (from Fixer's LLM):**
```python
{
    "files": [
        {
            "path": "/abs/path/to/file.py",
            "content": "# fixed code here"
        }
    ]
}
```

**Returns:**
```python
{
    "success": True,
    "files_modified": ["file1.py", "file2.py"],
    "errors": []
}
```

**Usage in Fixer Agent:**
```python
from src.tools.fixer_toolkit import apply_fixes, prepare_context_for_fixer

# Prepare context for LLM
context = prepare_context_for_fixer(
    files_to_fix=state.audit_report['files_analyzed'][:3],
    audit_report=state.audit_report,
    target_dir=state.target_dir
)

# ... send context to LLM, get response ...

# Apply the fixes
result = apply_fixes(llm_response, state.target_dir)
state.fixed_files = llm_response
```

---

### `prepare_context_for_fixer(...) -> Dict`

Prepares context for the Fixer's LLM, limiting token usage.

---

### `validate_python_syntax(filepath: str, target_dir: str) -> Dict`

Validates syntax after fixing (catches syntax errors before testing).

---

## Judge Toolkit (`src/tools/judge_toolkit.py`)

### `evaluate_code(target_dir: str) -> Dict`

**Primary function for the Judge agent.**

Evaluates code quality and runs tests.

**Returns (matches interfaces.md format):**
```python
{
    "passed": False,              # Required: True if all tests pass
    "errors": [                   # Required: Error messages if failed
        "Test: test_example.py::test_add\nMessage: AssertionError..."
    ],
    
    # Additional metrics for logging
    "pylint_score": 6.5,
    "test_count": 10,
    "passed_tests": 8,
    "failed_tests": 2
}
```

**Usage in Judge Agent:**
```python
from src.tools.judge_toolkit import evaluate_code, format_test_feedback_for_fixer

# Evaluate the code
test_results = evaluate_code(state.target_dir)
state.test_results = test_results
state.tests_passed = test_results['passed']

# If failed, format feedback for Fixer
if not test_results['passed']:
    feedback = format_test_feedback_for_fixer(test_results)
    # Include feedback in next iteration
```

---

### `compare_quality(before_score: float, after_score: float) -> Dict`

Compares quality before/after refactoring.

---

### `should_continue_fixing(...) -> tuple[bool, str]`

Determines if fixing loop should continue (checks for stagnation).

---

## Low-Level Tools (Still Available)

For advanced use cases, the original low-level tools remain available:

- `src/tools/file_operations.py` - File I/O
- `src/tools/analysis.py` - Pylint integration
- `src/tools/testing.py` - Pytest integration
- `src/tools/sandbox_security.py` - Security layer

---

## Quick Start for Each Agent

### Auditor Agent
```python
from src.tools.auditor_toolkit import analyze_project

audit_report = analyze_project(state.target_dir)
# audit_report is ready to be put in state.audit_report
```

### Fixer Agent
```python
from src.tools.fixer_toolkit import apply_fixes

result = apply_fixes(llm_fixed_files, state.target_dir)
```

### Judge Agent
```python
from src.tools.judge_toolkit import evaluate_code

test_results = evaluate_code(state.target_dir)
# test_results is ready to be put in state.test_results
```