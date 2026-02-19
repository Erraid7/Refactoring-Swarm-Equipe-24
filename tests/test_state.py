# tests/test_state.py
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.orchestration.state import RefactoringState


def test_state_creation():
    state = RefactoringState(target_dir="./sandbox/test")
    assert state.current_iteration == 0
    assert state.should_continue() == True
    
def test_max_iterations():
    state = RefactoringState(target_dir="./sandbox/test", max_iterations=3)
    state.current_iteration = 3
    assert state.should_continue() == False

if __name__ == "__main__":
    test_state_creation()
    test_max_iterations()
    print("✅ State tests passed!")