"""
Agent Correcteur - Applique les corrections au code
Utilise le fixer_toolkit du Toolsmith
"""

from src.agents.base_agent import BaseAgent
from src.orchestration.state import RefactoringState, AgentStatus
from src.utils.logger import log_experiment, ActionType
from src.tools.fixer_toolkit import (
    prepare_context_for_fixer,
    apply_fixes,
    format_files_for_llm
)
import json

class FixerAgent(BaseAgent):
    """Agent qui applique les corrections au code"""
    
    def __init__(self):
        super().__init__(name="Fixer", model="gemini-2.0-flash-exp")
    
    def execute(self, state: RefactoringState) -> RefactoringState:
        """Applique les corrections au code"""
        print(f"\n{'='*60}")
        print(f"🔧 {self.name} Agent: Applying fixes")
        print(f"{'='*60}")
        
        state.current_agent = self.name
        state.agent_status = AgentStatus.RUNNING
        
        try:
            # Vérifier qu'on a un rapport d'audit
            if not state.audit_report:
                raise ValueError("No audit report available. Run Auditor first.")
            
            # Étape 1: Préparer le contexte (limite le nombre de fichiers)
            print(f"📦 Preparing context for fixing...")
            context = prepare_context_for_fixer(
                files_to_fix=state.files_to_process,
                audit_report=state.audit_report,
                target_dir=state.target_dir,
                max_files=3  # Limiter pour éviter de saturer le contexte LLM
            )
            
            print(f"  ✅ Context prepared")
            print(f"  📂 Files to fix: {len(context['files'])}")
            
            # Étape 2: Formater les fichiers pour le prompt
            files_text = format_files_for_llm(context['files'])
            
            # Étape 3: Créer le prompt pour le LLM
            prompt = self._build_fix_prompt(
                files_text=files_text,
                plan=context['plan'],
                iteration=state.current_iteration,
                previous_errors=state.test_results.get('errors', []) if state.test_results else []
            )
            
            # Étape 4: Appeler le LLM
            print(f"🤖 Calling LLM to generate fixes...")
            llm_response = self._call_llm(prompt)
            
            # Étape 5: Parser la réponse
            fixed_files = self._parse_fixes(llm_response)
            
            print(f"  ✅ Fixes generated for {len(fixed_files['files'])} files")
            
            # Étape 6: Appliquer les fixes avec le toolkit
            print(f"✍️  Applying fixes to files...")
            result = apply_fixes(fixed_files, state.target_dir)
            
            if not result['success']:
                raise Exception(f"Failed to apply fixes: {result.get('errors')}")
            
            print(f"  ✅ Fixes applied successfully")
            for modified_file in result['files_modified']:
                print(f"     - Modified: {modified_file}")
            
            # Étape 7: Mettre à jour l'état
            state.fixed_code = fixed_files
            
            # Étape 8: Logger l'expérience (OBLIGATOIRE)
            log_experiment(
                agent_name=self.name,
                model_used=self.model,
                action=ActionType.FIX,
                details={
                    "files_modified": result['files_modified'],
                    "input_prompt": prompt,
                    "output_response": llm_response,
                    "iteration": state.current_iteration,
                    "plan_applied": context['plan']
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
                action=ActionType.FIX,
                details={
                    "input_prompt": f"Fix code in {state.target_dir}",
                    "output_response": f"Error: {str(e)}",
                    "error": str(e)
                },
                status="FAILED"
            )
            
            return state
    
    def _build_fix_prompt(self, files_text: str, plan: list, iteration: int, previous_errors: list) -> str:
        """Construit le prompt pour le LLM"""
        
        # Contexte d'itération
        iteration_context = f"This is iteration {iteration}."
        
        # Feedback des erreurs précédentes
        feedback_section = ""
        if iteration > 1 and previous_errors:
            errors_preview = "\n".join(previous_errors[:3])  # Limiter à 3 erreurs
            feedback_section = f"""
**IMPORTANT - Previous Attempt Failed:**
The previous fixes did not work. Here are the test errors:
{errors_preview}

You MUST address these specific errors in your fixes.
"""
        
        prompt = f"""You are an expert Python code fixer. {iteration_context}

{feedback_section}

**Refactoring Plan:**
{chr(10).join(f'{i+1}. {action}' for i, action in enumerate(plan))}

**Code to Fix:**
{files_text}

**Your Task:**
1. Apply ALL fixes from the plan above
2. Ensure the code is syntactically correct
3. Maintain existing functionality
4. Keep all imports and dependencies intact
5. Add docstrings where missing

**Critical Rules:**
- Return COMPLETE file contents (not just changed lines)
- Fix ALL syntax errors FIRST (missing colons, parentheses, etc.)
- Test your fixes mentally before returning
- If unsure, err on the side of minimal changes

**Output Format (JSON only, no markdown):**
{{
  "files": [
    {{
      "path": "/absolute/path/to/file.py",
      "content": "complete fixed code here"
    }}
  ]
}}

Return ONLY the JSON, no explanation.
"""
        return prompt
    
    def _parse_fixes(self, llm_response: str) -> dict:
        """Parse la réponse du LLM pour extraire les fichiers corrigés"""
        try:
            # Debug
            print(f"🔍 DEBUG _parse_fixes: Response length={len(llm_response)}, starts with: {llm_response[:100]}")
            
            # Nettoyer la réponse
            response = llm_response.strip()
            
            # Enlever les backticks markdown
            if response.startswith("```"):
                lines = response.split("\n")
                response = "\n".join(lines[1:-1])
            
            response = response.replace("```json", "").replace("```", "").strip()
            
            print(f"🔍 DEBUG _parse_fixes: After cleaning: {response[:100]}")
            
            # Parser le JSON
            data = json.loads(response)
            
            print(f"🔍 DEBUG _parse_fixes: Parsed data type={type(data)}, keys={data.keys() if isinstance(data, dict) else 'N/A'}")
            
            # Valider la structure
            if not isinstance(data, dict) or 'files' not in data:
                raise ValueError("Invalid response format: missing 'files' key")
            
            if not isinstance(data['files'], list):
                raise ValueError("Invalid response format: 'files' must be a list")
            
            # Valider chaque fichier
            for file_entry in data['files']:
                if not isinstance(file_entry, dict):
                    raise ValueError("Each file entry must be a dict")
                if 'path' not in file_entry or 'content' not in file_entry:
                    raise ValueError("Each file must have 'path' and 'content'")
            
            return data
            
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse LLM response as JSON: {e}")
            raise ValueError(f"LLM returned invalid JSON: {e}")