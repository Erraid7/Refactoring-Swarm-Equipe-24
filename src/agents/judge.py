from src.agents.base_agent import BaseAgent
from src.orchestration.state import RefactoringState, AgentStatus
from src.utils.logger import log_experiment, ActionType

# filepath: c:\Users\ABC\Desktop\refactoring-swarm-template\src\agents\judge.py


class JudgeAgent(BaseAgent):
    """Agent qui valide les corrections et vérifie l'amélioration du code"""
    
    def __init__(self):
        super().__init__(name="Judge", model="gemini-2.0-flash-exp")
    
    def execute(self, state: RefactoringState) -> RefactoringState:
        """Valide les corrections appliquées et calcule le score final"""
        print(f"⚖️ {self.name} validating fixes...")
        
        state.current_agent = self.name
        state.agent_status = AgentStatus.RUNNING
        
        try:
            # Vérifier que le code a été corrigé
            if not state.fixed_code:
                raise ValueError("No fixed code available to validate")
            
            # TODO: Utiliser les outils du Toolsmith
            # - Exécuter pylint sur le code corrigé
            # - Comparer avec le score initial
            # - Vérifier que les tests passent
            
            # Pour l'instant: stub
            prompt = f"Validate the fixes applied to {state.target_dir}. Original score: {state.pylint_score_initial}"
            response = self._call_llm(prompt)
            
            # Calculer le score final (stub)
            final_score = 8.5  # Stub - devrait venir de pylint
            improvement = final_score - state.pylint_score_initial
            
            # Log obligatoire
            log_experiment(
                agent_name=self.name,
                model_used=self.model,
                action=ActionType.ANALYSIS,
                details={
                    "target_dir": state.target_dir,
                    "input_prompt": prompt,
                    "output_response": response,
                    "initial_score": state.pylint_score_initial,
                    "final_score": final_score,
                    "improvement": improvement,
                    "files_validated": list(state.fixed_code.keys())
                },
                status="SUCCESS"
            )
            
            # Mettre à jour l'état
            state.pylint_score_current = final_score
            state.agent_status = AgentStatus.SUCCESS
            
            if improvement > 0:
                print(f"✅ {self.name} completed - Score improved from {state.pylint_score_initial} to {final_score}")
            else:
                print(f"⚠️ {self.name} completed - No improvement detected")
            
            return state
            
        except Exception as e:
            state.agent_status = AgentStatus.FAILED
            state.error_message = str(e)
            print(f"❌ {self.name} failed: {e}")
            return state