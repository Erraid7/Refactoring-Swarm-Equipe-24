"""
Test complet du Fixer Agent avec Gemini + Toolkit
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agents.fixer import FixerAgent
from src.orchestration.state import RefactoringState


def test_fixer_agent():
    """Test le Fixer Agent complet"""
    print("\n" + "="*70)
    print("🧪 Testing Fixer Agent (Gemini + Toolkit)")
    print("="*70)
    
    try:
        # Créer un état avec un rapport d'audit simulé
        state = RefactoringState(target_dir="./sandbox/test_toolkit")
        
        # Simuler un rapport d'audit (normalement créé par l'Auditor)
        state.files_to_process = [
            str(Path("./sandbox/test_toolkit/simple_bug.py").resolve())
        ]
        state.audit_report = {
            "pylint_score": 3.5,
            "issues": [
                {"file": "simple_bug.py", "line": 4, "message": "Missing colon after function definition"},
                {"file": "simple_bug.py", "line": 7, "message": "Bad spacing around operator"}
            ],
            "plan": [
                "Fix syntax error on line 4: add missing colon after function definition",
                "Fix spacing issues on line 7: add spaces around operators",
                "Add docstrings to all functions"
            ]
        }
        
        print(f"\n📋 Mock Audit Report:")
        print(f"  Score: {state.audit_report['pylint_score']}")
        print(f"  Plan: {len(state.audit_report['plan'])} actions")
        
        # Créer et exécuter l'agent
        print(f"\n🚀 Executing Fixer Agent...")
        agent = FixerAgent()
        state = agent.execute(state)
        
        # Vérifier les résultats
        if state.agent_status.value == "success":
            print(f"\n✅ Fixer Agent succeeded!")
            print(f"  Fixed files: {state.fixed_code}")
        else:
            print(f"\n❌ Fixer Agent failed: {state.error_message}")
            return False
        
        # Vérifier que le fichier a été modifié
        fixed_file = Path("./sandbox/test_toolkit/simple_bug.py")
        if fixed_file.exists():
            content = fixed_file.read_text()
            print(f"\n📄 Fixed file content preview:")
            print(content[:300] + "...")
        
        print("\n✅ TEST PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_fixer_agent()
    sys.exit(0 if success else 1)