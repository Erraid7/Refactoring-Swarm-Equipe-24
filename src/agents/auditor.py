"""
Agent Auditeur - Version avec Gemini + Toolkit
"""

from src.agents.base_agent import BaseAgent
from src.orchestration.state import RefactoringState, AgentStatus
from src.utils.logger import log_experiment, ActionType
from src.tools.auditor_toolkit import analyze_project, format_issues_for_llm
import json

class AuditorAgent(BaseAgent):
    
    def __init__(self):
        super().__init__(name="Auditor", model="gemini-2.5-flash")
    
    def execute(self, state: RefactoringState) -> RefactoringState:
        print(f"\n{'='*60}")
        print(f"🔍 {self.name}: Starting analysis")
        print(f"{'='*60}")
        
        state.current_agent = self.name
        state.agent_status = AgentStatus.RUNNING
        
        try:
            # 1. Analyser avec le toolkit
            print("📊 Analyzing with toolkit...")
            audit_report = analyze_project(state.target_dir)
            
            state.files_to_process = audit_report['files_analyzed']
            state.pylint_score_initial = audit_report['pylint_score']
            state.pylint_score_current = audit_report['pylint_score']
            
            print(f"  Files: {len(state.files_to_process)}")
            print(f"  Score: {audit_report['pylint_score']:.2f}/10")
            print(f"  Issues: {len(audit_report['issues'])}")
            
            # 2. Préparer le prompt pour Gemini
            issues_text = format_issues_for_llm(audit_report['issues'], max_issues=10)
            
            prompt = f"""You are a Python code auditor. Create a refactoring plan.

Files: {len(state.files_to_process)}
Pylint Score: {audit_report['pylint_score']:.2f}/10
Issues: {len(audit_report['issues'])}

Top Issues:
{issues_text}

Create a prioritized plan (max 5 actions) in JSON:
{{
  "plan": ["Fix syntax error in file.py line X", "Add missing import", ...]
}}

Return ONLY the JSON, no markdown.
"""
            
            # 3. Appeler Gemini
            print("🤖 Calling Gemini for plan generation...")
            response = self._call_llm(prompt, temperature=0.3)
            
            # 4. Parser la réponse
            plan = self._parse_plan(response)
            print(f"  Plan: {len(plan)} actions")
            
            # 5. Mettre à jour l'état
            state.audit_report = {
                "pylint_score": audit_report['pylint_score'],
                "issues": audit_report['issues'],
                "plan": plan
            }
            
            # 6. Logger
            log_experiment(
                agent_name=self.name,
                model_used=self.model,
                action=ActionType.ANALYSIS,
                details={
                    "files_analyzed": state.files_to_process,
                    "input_prompt": prompt,
                    "output_response": response,
                    "pylint_score": audit_report['pylint_score']
                },
                status="SUCCESS"
            )
            
            state.agent_status = AgentStatus.SUCCESS
            print(f"✅ {self.name}: Completed\n")
            return state
            
        except Exception as e:
            print(f"❌ {self.name}: Failed: {e}")
            state.agent_status = AgentStatus.FAILED
            state.error_message = str(e)
            return state
    
    def _parse_plan(self, llm_response: str) -> list:
        """Parse le plan du LLM"""
        try:
            # Nettoyer
            response = llm_response.strip()
            response = response.replace("```json", "").replace("```", "").strip()
            
            # Parser JSON
            data = json.loads(response)
            
            if isinstance(data, dict) and 'plan' in data:
                return data['plan'][:5]  # Max 5 actions
            elif isinstance(data, list):
                return data[:5]
            else:
                return ["Fix all detected issues"]
        except:
            # Fallback
            return ["Fix syntax errors", "Add missing imports", "Improve code style"]