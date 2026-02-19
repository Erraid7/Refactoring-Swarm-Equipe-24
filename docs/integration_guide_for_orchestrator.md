# Integration Guide for Orchestrator

## Overview

This guide explains how to integrate the Toolsmith's toolkit with the agents in `src/agents/`.

---

## Agent Integration Points

### 1. Auditor Agent (`src/agents/auditor.py`)

**Primary Tool:** `auditor_toolkit.analyze_project()`

**Integration Steps:**

```python
from src.tools.auditor_toolkit import analyze_project, format_issues_for_llm

def execute(self, state: RefactoringState) -> RefactoringState:
    # 1. Analyze the project
    audit_report = analyze_project(state.target_dir)
    
    # 2. Populate state.files_to_analyze
    state.files_to_analyze = audit_report['files_analyzed']
    
    # 3. Format issues for LLM
    issues_text = format_issues_for_llm(audit_report['issues'], max_issues=10)
    
    # 4. Create LLM prompt with issues_text
    prompt = f"Analyze these issues and create a plan:\n{issues_text}"
    
    # 5. Call LLM to get refactoring plan
    response = self._call_llm(prompt)
    
    # 6. Parse plan and populate state.audit_report
    state.audit_report = {
        "pylint_score": audit_report['pylint_score'],
        "issues": audit_report['issues'],
        "plan": parsed_plan_from_llm
    }
    
    return state
```

**Output Format (matches interfaces.md):**
```python
state.audit_report = {
    "pylint_score": 6.5,
    "issues": [...],
    "plan": ["Action 1", "Action 2", ...]
}
```

---

### 2. Fixer Agent (`src/agents/fixer.py`)

**Primary Tools:**
- `fixer_toolkit.prepare_context_for_fixer()` - Before LLM call
- `fixer_toolkit.apply_fixes()` - After LLM response

**Integration Steps:**

```python
from src.tools.fixer_toolkit import prepare_context_for_fixer, apply_fixes, format_files_for_llm

def execute(self, state: RefactoringState) -> RefactoringState:
    # 1. Prepare context (limits files to avoid token overflow)
    context = prepare_context_for_fixer(
        files_to_fix=state.files_to_analyze,
        audit_report=state.audit_report,
        target_dir=state.target_dir,
        max_files=3  # Limit to 3 files per iteration
    )
    
    # 2. Format files for LLM
    files_text = format_files_for_llm(context['files'])
    
    # 3. Create LLM prompt
    prompt = f"Fix these files:\n{files_text}\n\nPlan: {context['plan']}"
    
    # 4. Call LLM
    response = self._call_llm(prompt)
    
    # 5. Parse LLM response (should be JSON)
    import json
    fixed_files = json.loads(response)  # Format: {"files": [{"path": ..., "content": ...}]}
    
    # 6. Apply fixes using toolkit
    result = apply_fixes(fixed_files, state.target_dir)
    
    # 7. Update state
    state.fixed_files = fixed_files
    
    return state
```

**Expected LLM Output Format:**
```json
{
  "files": [
    {
      "path": "/absolute/path/to/file.py",
      "content": "fixed code here"
    }
  ]
}
```

---

### 3. Judge Agent (`src/agents/judge.py`)

**Primary Tool:** `judge_toolkit.evaluate_code()`

**Integration Steps:**

```python
from src.tools.judge_toolkit import evaluate_code, format_test_feedback_for_fixer

def execute(self, state: RefactoringState) -> RefactoringState:
    # 1. Evaluate the code
    test_results = evaluate_code(state.target_dir)
    
    # 2. Update state (format matches interfaces.md)
    state.test_results = {
        "passed": test_results['passed'],
        "errors": test_results['errors']
    }
    state.tests_passed = test_results['passed']
    
    # 3. If failed, format feedback for next Fixer iteration
    if not test_results['passed']:
        feedback = format_test_feedback_for_fixer(test_results)
        # This feedback can be included in Fixer's prompt in the next iteration
        state.test_results['feedback'] = feedback
    
    return state
```

**Output Format (matches interfaces.md):**
```python
state.test_results = {
    "passed": False,
    "errors": ["Test error message 1", "Test error message 2"]
}
```

---

## Workflow Integration (`src/orchestration/workflow.py`)

### Basic Workflow Structure

```python
from src.agents.auditor import AuditorAgent
from src.agents.fixer import FixerAgent
from src.agents.judge import JudgeAgent

def run_refactoring_workflow(target_dir: str, max_iterations: int = 10):
    # Initialize state
    state = RefactoringState(target_dir=target_dir, max_iterations=max_iterations)
    
    # Initialize agents
    auditor = AuditorAgent()
    fixer = FixerAgent()
    judge = JudgeAgent()
    
    # Phase 1: Initial Audit (once)
    print("Phase 1: Auditing...")
    state = auditor.execute(state)
    
    # Phase 2: Fix-Test Loop (until tests pass or max iterations)
    while state.should_continue():
        state.iteration += 1
        
        print(f"Iteration {state.iteration}: Fixing...")
        state = fixer.execute(state)
        
        print(f"Iteration {state.iteration}: Testing...")
        state = judge.execute(state)
        
        if state.tests_passed:
            print("✅ All tests passed!")
            break
    
    return state
```

---

## Error Handling

All toolkit functions can raise exceptions. Wrap them in try-except:

```python
try:
    audit_report = analyze_project(state.target_dir)
except Exception as e:
    print(f"❌ Analysis failed: {e}")
    state.error_message = str(e)
    return state
```

---

## Token Optimization Tips

1. **Auditor**: Use `format_issues_for_llm(issues, max_issues=10)` to limit issues
2. **Fixer**: Use `prepare_context_for_fixer(..., max_files=3)` to limit files
3. **Judge**: Feedback is already truncated by `format_test_feedback_for_fixer()`

---

## Testing Integration

Before full integration, test each toolkit independently:

```bash
# Test Auditor toolkit
python -c "from src.tools.auditor_toolkit import analyze_project; print(analyze_project('./sandbox/test'))"

# Test Fixer toolkit
python src/tools/fixer_toolkit.py

# Test Judge toolkit
python src/tools/judge_toolkit.py
```

---

## Quick Reference

| Agent | Primary Function | Input | Output Field in State |
|-------|-----------------|-------|----------------------|
| Auditor | `analyze_project()` | `target_dir` | `state.audit_report` |
| Fixer | `apply_fixes()` | `fixed_files_data, target_dir` | `state.fixed_files` |
| Judge | `evaluate_code()` | `target_dir` | `state.test_results` |

---

## Contact

For questions about the toolkit integration, contact the Toolsmith or refer to:
- Full API docs: `docs/tool_api.md`
- Interface contract: `docs/interfaces.md`