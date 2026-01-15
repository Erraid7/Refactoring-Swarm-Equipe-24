"""
Workflow principal - Orchestre les agents pour le refactoring
"""

from typing import Dict
import time
from pathlib import Path

from src.orchestration.state import RefactoringState, AgentStatus
from src.agents.auditor import AuditorAgent
from src.agents.fixer import FixerAgent
from src.agents.judge import JudgeAgent
from src.utils.logger import log_experiment, ActionType


def run_refactoring_workflow(
    target_dir: str,
    max_iterations: int = 10,
    verbose: bool = False
) -> Dict:
    """
    Orchestre le workflow complet de refactoring
    
    Args:
        target_dir: Répertoire contenant le code à refactorer
        max_iterations: Nombre maximum d'itérations Fix-Test
        verbose: Affichage détaillé
    
    Returns:
        Dict avec les résultats finaux
    """
    print("\n" + "="*70)
    print("🐝 THE REFACTORING SWARM")
    print("="*70)
    print(f"📂 Target: {target_dir}")
    print(f"🔄 Max iterations: {max_iterations}")
    print("="*70 + "\n")
    
    # Validation initiale
    if not Path(target_dir).exists():
        return {
            'success': False,
            'iterations': 0,
            'pylint_before': 0.0,
            'pylint_after': 0.0,
            'execution_time': 0.0,
            'error': f"Directory not found: {target_dir}"
        }
    
    # Initialiser l'état
    state = RefactoringState(
        target_dir=target_dir,
        max_iterations=max_iterations
    )
    
    # Initialiser les agents
    auditor = AuditorAgent()
    fixer = FixerAgent()
    judge = JudgeAgent()
    
    start_time = time.time()
    
    try:
        # ==========================================
        # PHASE 1: AUDIT INITIAL (une seule fois)
        # ==========================================
        print("┌" + "─"*68 + "┐")
        print("│" + " "*20 + "PHASE 1: INITIAL AUDIT" + " "*25 + "│")
        print("└" + "─"*68 + "┘")
        
        state = auditor.execute(state)
        
        if state.agent_status == AgentStatus.FAILED:
            raise Exception(f"Auditor failed: {state.error_message}")
        
        print(f"\n📊 Initial Assessment:")
        print(f"  • Files to fix: {len(state.files_to_process)}")
        print(f"  • Pylint score: {state.pylint_score_initial:.2f}/10")
        if state.audit_report:
            print(f"  • Issues found: {len(state.audit_report['issues'])}")
            print(f"  • Refactoring plan: {len(state.audit_report['plan'])} actions")
        else:
            print(f"  • Issues found: N/A (no audit report)")
            print(f"  • Refactoring plan: N/A")
        
        # ==========================================
        # PHASE 2: FIX-TEST LOOP
        # ==========================================
        print("\n┌" + "─"*68 + "┐")
        print("│" + " "*18 + "PHASE 2: FIX-TEST LOOP" + " "*25 + "│")
        print("└" + "─"*68 + "┘\n")
        
        previous_score = state.pylint_score_initial
        stagnation_count = 0
        
        while state.should_continue():
            state.increment_iteration()
            
            print(f"\n{'┌' + '─'*68 + '┐'}")
            print(f"│  ITERATION {state.current_iteration}/{state.max_iterations}" + " "*(55-len(str(state.current_iteration))-len(str(state.max_iterations))) + "│")
            print(f"{'└' + '─'*68 + '┘'}")
            
            # Étape 1: Fixer le code
            state = fixer.execute(state)
            
            if state.agent_status == AgentStatus.FAILED:
                print(f"\n⚠️  Fixer failed: {state.error_message}")
                print("   Stopping iteration loop.")
                break
            
            # Étape 2: Tester et évaluer
            state = judge.execute(state)
            
            if state.agent_status == AgentStatus.FAILED:
                print(f"\n⚠️  Judge failed: {state.error_message}")
                print("   Stopping iteration loop.")
                break
            
            # Vérifier si les tests passent
            if state.tests_passed:
                print(f"\n{'🎉'*20}")
                print(f"  ALL TESTS PASSED!")
                print(f"  Success after {state.current_iteration} iteration(s)")
                print(f"{'🎉'*20}\n")
                break
            
            # Détecter la stagnation
            score_improvement = abs(state.pylint_score_current - previous_score)
            if score_improvement < 0.1:
                stagnation_count += 1
                print(f"\n⚠️  Warning: Little improvement detected (count: {stagnation_count}/3)")
                
                if stagnation_count >= 3:
                    print(f"   No significant progress for 3 iterations. Stopping.")
                    break
            else:
                stagnation_count = 0
            
            previous_score = state.pylint_score_current
            
            # Afficher l'état
            print(f"\n📊 Iteration {state.current_iteration} Summary:")
            print(f"  • Tests: {'✅ PASSED' if state.tests_passed else '❌ FAILED'}")
            print(f"  • Pylint: {state.pylint_score_current:.2f}/10")
            print(f"  • Status: {'✅ Complete' if state.tests_passed else '🔄 Retrying...'}")
        
        # ==========================================
        # PHASE 3: FINALISATION
        # ==========================================
        execution_time = time.time() - start_time
        
        print("\n┌" + "─"*68 + "┐")
        print("│" + " "*23 + "FINAL RESULTS" + " "*30 + "│")
        print("└" + "─"*68 + "┘\n")
        
        # Logger la fin de l'expérience
        log_experiment(
            agent_name="Orchestrator",
            model_used="workflow_v1",
            action=ActionType.ANALYSIS,
            details={
                "input_prompt": f"Complete refactoring workflow for {target_dir}",
                "output_response": f"Workflow completed: {state.tests_passed}",
                "total_iterations": state.current_iteration,
                "success": state.tests_passed,
                "pylint_improvement": state.pylint_score_current - state.pylint_score_initial
            },
            status="SUCCESS" if state.tests_passed else "PARTIAL"
        )
        
        # Résultats finaux
        results = {
            'success': state.tests_passed,
            'iterations': state.current_iteration,
            'pylint_before': state.pylint_score_initial,
            'pylint_after': state.pylint_score_current,
            'execution_time': execution_time,
            'error': None if state.tests_passed else "Tests did not pass within max iterations"
        }
        
        # Affichage des résultats
        print(f"{'✅' if results['success'] else '⚠️ '} Success: {results['success']}")
        print(f"🔄 Iterations used: {results['iterations']}/{max_iterations}")
        print(f"📈 Pylint: {results['pylint_before']:.2f} → {results['pylint_after']:.2f}")
        print(f"   Improvement: {results['pylint_after'] - results['pylint_before']:+.2f} points")
        print(f"⏱️  Execution time: {results['execution_time']:.2f}s")
        
        if not results['success']:
            print(f"\n⚠️  Note: {results['error']}")
        
        print("\n" + "="*70 + "\n")
        
        return results
        
    except Exception as e:
        execution_time = time.time() - start_time
        
        print(f"\n💥 WORKFLOW CRASHED\n")
        print(f"Error: {e}\n")
        
        import traceback
        if verbose:
            traceback.print_exc()
        
        # Logger l'erreur
        log_experiment(
            agent_name="Orchestrator",
            model_used="workflow_v1",
            action=ActionType.DEBUG,
            details={
                "input_prompt": f"Workflow for {target_dir}",
                "output_response": f"Crashed: {str(e)}",
                "error": str(e)
            },
            status="FAILED"
        )
        
        return {
            'success': False,
            'iterations': state.current_iteration,
            'pylint_before': state.pylint_score_initial,
            'pylint_after': state.pylint_score_current,
            'execution_time': execution_time,
            'error': str(e)
        }