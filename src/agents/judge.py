"""
Agent Testeur - Évalue la qualité du code et exécute les tests
Utilise le judge_toolkit du Toolsmith
"""

from src.agents.base_agent import BaseAgent
from src.orchestration.state import RefactoringState, AgentStatus
from src.utils.logger import log_experiment, ActionType
from src.tools.judge_toolkit import (
    evaluate_code,
    format_test_feedback_for_fixer,
    compare_quality
)

class JudgeAgent(BaseAgent):
    """Agent qui teste et évalue la qualité du code"""
    
    def __init__(self):
        super().__init__(name="Judge", model="gemini-2.0-flash-exp")
    
    def execute(self, state: RefactoringState) -> RefactoringState:
        """Évalue le code et exécute les tests"""
        print(f"\n{'='*60}")
        print(f"⚖️  {self.name} Agent: Evaluating code quality")
        print(f"{'='*60}")
        
        state.current_agent = self.name
        state.agent_status = AgentStatus.RUNNING
        
        try:
            # Étape 1: Évaluer le code avec le toolkit
            print(f"🧪 Running tests and quality checks...")
            evaluation = evaluate_code(state.target_dir)
            
            # Étape 2: Mettre à jour l'état
            state.test_results = {
                "passed": evaluation['passed'],
                "errors": evaluation['errors']
            }
            state.tests_passed = evaluation['passed']
            
            # Mettre à jour le score Pylint actuel
            if 'pylint_score' in evaluation:
                state.pylint_score_current = evaluation['pylint_score']
            
            # Afficher les résultats
            print(f"  ✅ Evaluation complete")
            print(f"  📊 Pylint score: {state.pylint_score_current:.2f}/10")
            
            if evaluation['passed']:
                print(f"  ✅ All tests passed!")
                
                # Comparer la qualité
                comparison = compare_quality(
                    state.pylint_score_initial,
                    state.pylint_score_current
                )
                print(f"  📈 Quality improvement: {comparison['improvement']:.2f} points ({comparison['percentage']:.1f}%)")
            else:
                print(f"  ❌ Tests failed: {len(evaluation['errors'])} errors")
                for i, error in enumerate(evaluation['errors'][:3], 1):
                    print(f"     {i}. {error[:100]}...")
                if len(evaluation['errors']) > 3:
                    print(f"     ... and {len(evaluation['errors'])-3} more errors")
                
                # Formater le feedback pour le Fixer
                feedback = format_test_feedback_for_fixer(evaluation)
                state.test_results['feedback'] = feedback
            
            # Étape 3: Logger l'expérience (OBLIGATOIRE)
            action_type = ActionType.DEBUG if not evaluation['passed'] else ActionType.ANALYSIS
            
            log_experiment(
                agent_name=self.name,
                model_used=self.model,
                action=action_type,
                details={
                    "input_prompt": f"Evaluate code quality and tests for iteration {state.current_iteration}",
                    "output_response": f"Tests: {'PASSED' if evaluation['passed'] else 'FAILED'}, Pylint: {state.pylint_score_current:.2f}",
                    "tests_passed": evaluation['passed'],
                    "pylint_score": state.pylint_score_current,
                    "test_errors_count": len(evaluation['errors']),
                    "iteration": state.current_iteration
                },
                status="SUCCESS" if evaluation['passed'] else "PARTIAL"
            )
            
            state.agent_status = AgentStatus.SUCCESS
            print(f"✅ {self.name} Agent: Completed successfully\n")
            return state
            
        except Exception as e:
            print(f"❌ {self.name} Agent: Failed with error: {e}")
            state.agent_status = AgentStatus.FAILED
            state.error_message = str(e)
            
            # Logger l'erreur
            log_experiment(
                agent_name=self.name,
                model_used=self.model,
                action=ActionType.DEBUG,
                details={
                    "input_prompt": f"Evaluate {state.target_dir}",
                    "output_response": f"Error: {str(e)}",
                    "error": str(e)
                },
                status="FAILED"
            )
            
            return state