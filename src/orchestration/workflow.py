from src.agents.auditor import AuditorAgent
from src.agents.fixer import FixerAgent
from src.agents.judge import JudgeAgent
from src.orchestration.state import RefactoringState, AgentStatus
import time
from typing import Dict

def run_refactoring_workflow(target_dir: str, max_iterations: int = 10, verbose: bool = False) -> Dict:
    """Workflow complet avec agents"""
    
    print("🎭 Initializing workflow...")
    
    state = RefactoringState(
        target_dir=target_dir,
        max_iterations=max_iterations
    )
    
    # Instancier les agents
    auditor = AuditorAgent()
    fixer = FixerAgent()
    judge = JudgeAgent()
    
    start_time = time.time()
    
    try:
        # Étape 1: Audit initial (une seule fois)
        print("\n" + "="*50)
        print("Phase 1: Initial Code Audit")
        print("="*50)
        state = auditor.execute(state)
        
        if state.agent_status == AgentStatus.FAILED:
            raise Exception(f"Auditor failed: {state.error_message}")
        
        # Boucle de refactoring
        while state.should_continue():
            state.increment_iteration()
            print(f"\n{'='*50}")
            print(f"Iteration {state.current_iteration}/{state.max_iterations}")
            print(f"{'='*50}")
            
            # Étape 2: Correction
            print("\n🔧 Phase: Code Fixing")
            state = fixer.execute(state)
            
            if state.agent_status == AgentStatus.FAILED:
                print(f"⚠️  Fixer failed: {state.error_message}")
                break
            
            # Étape 3: Test
            print("\n🧪 Phase: Testing")
            state = judge.execute(state)
            
            if state.agent_status == AgentStatus.FAILED:
                print(f"⚠️  Judge failed: {state.error_message}")
                break
            
            if state.tests_passed:
                print("\n🎉 All tests passed!")
                break
            else:
                print(f"❌ Tests failed. Retrying... ({state.current_iteration}/{state.max_iterations})")
        
        execution_time = time.time() - start_time
        
        # Résultats finaux
        return {
            'success': state.tests_passed,
            'iterations': state.current_iteration,
            'pylint_before': state.pylint_score_initial,
            'pylint_after': state.pylint_score_current,
            'execution_time': execution_time,
            'error': state.error_message
        }
        
    except Exception as e:
        print(f"\n💥 Workflow crashed: {e}")
        return {
            'success': False,
            'iterations': state.current_iteration,
            'error': str(e)
        }