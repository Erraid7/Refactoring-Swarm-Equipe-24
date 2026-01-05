from src.agents.base_agent import BaseAgent
from src.orchestration.state import RefactoringState, AgentStatus
from src.utils.logger import log_experiment, ActionType

class AuditorAgent(BaseAgent):
    """Agent qui analyse le code et crée un plan de refactoring"""
    
    def __init__(self):
        super().__init__(name="Auditor", model="gemini-2.0-flash-exp")
    
    def execute(self, state: RefactoringState) -> RefactoringState:
        """Analyse le code et produit un rapport"""
        print(f"🔍 {self.name} analyzing code...")
        
        state.current_agent = self.name
        state.agent_status = AgentStatus.RUNNING
        
        try:
            # TODO: Utiliser les outils du Toolsmith
            # files = scan_python_files(state.target_dir)
            # pylint_results = run_pylint_analysis(files[0])
            
            # Pour l'instant: stub
            prompt = f"Analyze Python code in {state.target_dir}"
            response = self._call_llm(prompt)
            
            # Log obligatoire
            log_experiment(
                agent_name=self.name,
                model_used=self.model,
                action=ActionType.ANALYSIS,
                details={
                    "target_dir": state.target_dir,
                    "input_prompt": prompt,
                    "output_response": response,
                    "files_analyzed": ["stub.py"]
                },
                status="SUCCESS"
            )
            
            # Mettre à jour l'état
            state.audit_report = {
                "pylint_score": 5.0,  # Stub
                "issues": ["Missing docstring"],  # Stub
                "plan": ["Add docstrings"]  # Stub
            }
            state.pylint_score_initial = 5.0
            state.agent_status = AgentStatus.SUCCESS
            
            print(f"✅ {self.name} completed")
            return state
            
        except Exception as e:
            state.agent_status = AgentStatus.FAILED
            state.error_message = str(e)
            print(f"❌ {self.name} failed: {e}")
            return state