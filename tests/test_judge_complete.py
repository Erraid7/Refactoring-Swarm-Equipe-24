"""
Test complet du Judge Agent avec Gemini + Toolkit
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agents.judge import JudgeAgent
from src.orchestration.state import RefactoringState


def test_judge_agent():
    """Test le Judge Agent complet"""
    print("\n" + "="*70)
    print("🧪 Testing Judge Agent (Gemini + Toolkit)")
    print("="*70)
    
    try:
        # Créer un état
        state = RefactoringState(target_dir="./sandbox/test_toolkit")
        state.current_iteration = 1
        state.pylint_score_initial = 3.5
        state.files_to_process = [
            str(Path("./sandbox/test_toolkit/simple_bug.py").resolve())
        ]
        state.audit_report = {
            "plan": ["Fix syntax errors", "Add docstrings"]
        }
        
        # Créer et exécuter l'agent
        print(f"\n🚀 Executing Judge Agent...")
        agent = JudgeAgent()
        state = agent.execute(state)
        
        # Vérifier les résultats
        if state.agent_status.value == "success":
            print(f"\n✅ Judge Agent succeeded!")
            print(f"  Tests passed: {state.tests_passed}")
            print(f"  Current score: {state.pylint_score_current:.2f}")
            
            if not state.tests_passed:
                if state.test_results:
                    print(f"  Errors: {len(state.test_results['errors'])}")
        else:
            print(f"\n❌ Judge Agent failed: {state.error_message}")
            return False
        
        print("\n✅ TEST PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_judge_agent()
    sys.exit(0 if success else 1)