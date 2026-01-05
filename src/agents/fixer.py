from src.agents.base_agent import BaseAgent
from src.orchestration.state import RefactoringState, AgentStatus
from src.utils.logger import log_experiment, ActionType

# filepath: c:\Users\ABC\Desktop\refactoring-swarm-template\src\agents\fixer.py

class FixerAgent(BaseAgent):
    """Agent qui applique les corrections de code basées sur le plan de refactoring"""
    
    def __init__(self):
        super().__init__(name="Fixer", model="gemini-2.0-flash-exp")
    
    def execute(self, state: RefactoringState) -> RefactoringState:
        """Applique les corrections de code"""
        print(f"🔧 {self.name} applying fixes...")
        
        state.current_agent = self.name
        state.agent_status = AgentStatus.RUNNING
        
        try:
            # Vérifier qu'un plan existe
            if not state.audit_report or "plan" not in state.audit_report:
                raise ValueError("No refactoring plan available")
            
            plan = state.audit_report["plan"]
            
            # TODO: Utiliser les outils du Toolsmith
            # - Lire les fichiers à modifier
            # - Appliquer les changements suggérés
            # - Écrire les fichiers modifiés
            
            # Pour l'instant: stub
            prompt = f"Apply these fixes to {state.target_dir}: {plan}"
            response = self._call_llm(prompt)
            
            # Log obligatoire
            log_experiment(
                agent_name=self.name,
                model_used=self.model,
                action=ActionType.FIX,
                details={
                    "target_dir": state.target_dir,
                    "plan": plan,
                    "input_prompt": prompt,
                    "output_response": response,
                    "files_modified": ["stub.py"]
                },
                status="SUCCESS"
            )
            
            # Mettre à jour l'état
            state.fixed_code = {
                "stub.py": "# Fixed code with docstrings"  # Stub
            }
            state.agent_status = AgentStatus.SUCCESS
            
            print(f"✅ {self.name} completed")
            return state
            
        except Exception as e:
            state.agent_status = AgentStatus.FAILED
            state.error_message = str(e)
            print(f"❌ {self.name} failed: {e}")
            return state