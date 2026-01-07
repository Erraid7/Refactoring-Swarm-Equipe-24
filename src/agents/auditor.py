"""
Agent Auditeur - Analyse le code et crée un plan de refactoring
Utilise le auditor_toolkit du Toolsmith
"""

from src.agents.base_agent import BaseAgent
from src.orchestration.state import RefactoringState, AgentStatus
from src.utils.logger import log_experiment, ActionType
from src.tools.auditor_toolkit import (
    analyze_project,
    format_issues_for_llm,
    get_files_to_analyze
)
import json

class AuditorAgent(BaseAgent):
    """Agent qui analyse le code et crée un plan de refactoring"""
    
    def __init__(self):
        super().__init__(name="Auditor", model="gemini-2.0-flash-exp")
    
    def execute(self, state: RefactoringState) -> RefactoringState:
        """Analyse le code et produit un rapport d'audit"""
        print(f"\n{'='*60}")
        print(f"🔍 {self.name} Agent: Starting code analysis")
        print(f"{'='*60}")
        
        state.current_agent = self.name
        state.agent_status = AgentStatus.RUNNING
        
        try:
            # Étape 1: Analyser le projet avec le toolkit du Toolsmith
            print(f"📊 Analyzing project: {state.target_dir}")
            audit_report = analyze_project(state.target_dir)
            
            # Étape 2: Populer state.files_to_process
            state.files_to_process = audit_report['files_analyzed']
            
            # Étape 3: Sauvegarder les scores initiaux
            state.pylint_score_initial = audit_report['pylint_score']
            state.pylint_score_current = audit_report['pylint_score']
            
            print(f"  ✅ Analysis complete")
            print(f"  📂 Files analyzed: {len(state.files_to_process)}")
            print(f"  📈 Pylint score: {audit_report['pylint_score']:.2f}/10")
            print(f"  ⚠️  Issues found: {len(audit_report['issues'])}")
            
            # Étape 4: Formater les issues pour le LLM (limite tokens)
            issues_text = format_issues_for_llm(
                audit_report['issues'],
                max_issues=15  # Limiter pour ne pas saturer le prompt
            )
            
            # Étape 5: Créer le prompt pour le LLM
            prompt = self._build_analysis_prompt(audit_report, issues_text)
            
            # Étape 6: Appeler le LLM pour obtenir un plan de refactoring
            print(f"🤖 Calling LLM to generate refactoring plan...")
            llm_response = self._call_llm(prompt)
            
            # Étape 7: Parser la réponse du LLM
            plan = self._parse_refactoring_plan(llm_response)
            
            print(f"  ✅ Refactoring plan generated ({len(plan)} actions)")
            for i, action in enumerate(plan[:3], 1):  # Afficher les 3 premières
                print(f"     {i}. {action}")
            if len(plan) > 3:
                print(f"     ... and {len(plan)-3} more actions")
            
            # Étape 8: Créer le rapport final et mettre à jour l'état
            state.audit_report = {
                "pylint_score": audit_report['pylint_score'],
                "issues": audit_report['issues'],
                "plan": plan,
                "files_analyzed": audit_report['files_analyzed'],
                "critical_issues": audit_report.get('critical_issues', [])
            }
            
            # Étape 9: Logger l'expérience (OBLIGATOIRE)
            log_experiment(
                agent_name=self.name,
                model_used=self.model,
                action=ActionType.ANALYSIS,
                details={
                    "files_analyzed": state.files_to_process,
                    "input_prompt": prompt,
                    "output_response": llm_response,
                    "pylint_score": audit_report['pylint_score'],
                    "issues_count": len(audit_report['issues']),
                    "plan_items": len(plan)
                },
                status="SUCCESS"
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
                action=ActionType.ANALYSIS,
                details={
                    "input_prompt": f"Analysis of {state.target_dir}",
                    "output_response": f"Error: {str(e)}",
                    "error": str(e)
                },
                status="FAILED"
            )
            
            return state
    
    def _build_analysis_prompt(self, audit_report: dict, issues_text: str) -> str:
        """Construit le prompt pour le LLM"""
        prompt = f"""You are an expert Python code auditor. You have analyzed a Python project and found several issues.

**Project Statistics:**
- Files analyzed: {len(audit_report['files_analyzed'])}
- Average Pylint score: {audit_report['pylint_score']:.2f}/10
- Total issues found: {len(audit_report['issues'])}

**Issues Detected:**
{issues_text}

**Your Task:**
Create a prioritized refactoring plan to fix these issues. Focus on:
1. Critical errors (syntax errors, undefined names) - HIGHEST PRIORITY
2. Important issues (logic errors, missing imports)
3. Code quality improvements (styling, documentation)

**Instructions:**
- Create a maximum of 8 specific, actionable steps
- Each step should be clear and focused on ONE type of fix
- Prioritize fixes that will make tests pass
- Return your plan as a JSON array of strings

**Output Format (JSON only, no markdown):**
{{
  "plan": [
    "Fix syntax error in file.py line X: add missing colon",
    "Add missing import for datetime in module.py",
    "..."
  ]
}}
"""
        return prompt
    
    def _parse_refactoring_plan(self, llm_response: str) -> list:
        """Parse la réponse du LLM pour extraire le plan"""
        try:
            # Nettoyer la réponse (enlever markdown si présent)
            response = llm_response.strip()
            
            # Enlever les backticks markdown
            if response.startswith("```"):
                lines = response.split("\n")
                response = "\n".join(lines[1:-1])  # Enlever première et dernière ligne
            
            response = response.replace("```json", "").replace("```", "").strip()
            
            # Parser le JSON
            data = json.loads(response)
            
            if isinstance(data, dict) and 'plan' in data:
                plan = data['plan']
            elif isinstance(data, list):
                plan = data
            else:
                raise ValueError("Invalid plan format")
            
            # Valider et limiter le plan
            if not isinstance(plan, list):
                raise ValueError("Plan must be a list")
            
            # Limiter à 8 actions maximum
            plan = plan[:8]
            
            return plan
            
        except json.JSONDecodeError as e:
            print(f"⚠️  Failed to parse LLM response as JSON: {e}")
            print(f"   Falling back to line-by-line parsing")
            
            # Fallback: parser ligne par ligne
            lines = llm_response.split('\n')
            plan = []
            for line in lines:
                line = line.strip()
                # Chercher des lignes qui ressemblent à des actions
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                    # Nettoyer la ligne
                    clean_line = line.lstrip('0123456789.-•)]} \t')
                    if clean_line:
                        plan.append(clean_line)
            
            return plan[:8] if plan else ["Fix all detected issues"]