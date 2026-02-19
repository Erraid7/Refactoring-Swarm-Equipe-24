import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agents.auditor import AuditorAgent
from src.orchestration.state import RefactoringState

state = RefactoringState(target_dir="./sandbox/test_toolkit")
agent = AuditorAgent()
state = agent.execute(state)

print("\n📊 Results:")
print(f"Score: {state.pylint_score_initial}")

# Safety check before accessing audit_report
if state.audit_report is not None:
    print(f"Plan: {state.audit_report.get('plan', 'No plan found')}")
else:
    print("⚠️ Audit report was not generated")
    print(f"Debug - audit_report value: {state.audit_report}")