État Partagé (RefactoringState):
- target_dir: str
- iteration: int
- max_iterations: int
- files_to_analyze: List[str]
- audit_report: Dict  # Output de l'Auditor
- fixed_files: Dict[str, str]  # Output du Fixer
- test_results: Dict  # Output du Judge
- should_continue: bool

Format des outputs:
- Auditor retourne: {"pylint_score": float, "issues": [...], "plan": [...]}
- Fixer retourne: {"files": [{"path": str, "content": str}]}
- Judge retourne: {"passed": bool, "errors": [...]}