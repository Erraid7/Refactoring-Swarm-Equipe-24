# tests/test_agents_stub.py
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agents.auditor import AuditorAgent
from src.orchestration.state import RefactoringState

def test_auditor_stub():
    state = RefactoringState(target_dir="./sandbox/test")
    agent = AuditorAgent()
    new_state = agent.execute(state)
    
    assert new_state.audit_report is not None
    assert new_state.agent_status.value == "success"
    print("✅ Auditor stub works!")

if __name__ == "__main__":
    test_auditor_stub()