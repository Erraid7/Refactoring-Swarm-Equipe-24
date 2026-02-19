"""
Agent Correcteur - Applique les corrections au code
Utilise Gemini + fixer_toolkit du Toolsmith
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
        super().__init__(name="Fixer", model="gemini-2.5-flash")
    
    def execute(self, state: RefactoringState) -> RefactoringState:
        """Applique les corrections au code"""
        print(f"\n{'='*60}")
        print(f"🔧 {self.name}: Applying fixes")
        print(f"{'='*60}")
        
        state.current_agent = self.name
        state.agent_status = AgentStatus.RUNNING
        
        try:
            # Vérifier qu'on a un rapport d'audit
            if not state.audit_report:
                raise ValueError("No audit report available. Run Auditor first.")
            
            # Étape 1: Préparer le contexte (limite les fichiers pour éviter token overflow)
            print(f"📦 Preparing context for fixing...")
            context = prepare_context_for_fixer(
                files_to_fix=state.files_to_process,
                audit_report=state.audit_report,
                target_dir=state.target_dir,
                max_files=3  # Limiter à 3 fichiers par itération
            )
            
            print(f"  ✅ Context prepared")
            print(f"  📂 Files to fix: {len(context['files'])}")
            for f in context['files']:
                print(f"     - {f['path']}")
            
            # Étape 2: Formater les fichiers pour le prompt
            files_text = format_files_for_llm(context['files'])
            
            # Étape 3: Construire le prompt avec feedback si itération > 1
            prompt = self._build_fix_prompt(
                files_text=files_text,
                plan=context['plan'],
                iteration=state.current_iteration,
                previous_errors=state.test_results.get('errors', []) if state.test_results else []
            )
            
            # Étape 4: Appeler Gemini
            print(f"🤖 Calling Gemini to generate fixes...")
            llm_response = self._call_llm(prompt, temperature=0.2, max_tokens=8192)  # More tokens for large files
            
            # Étape 5: Parser la réponse
            print(f"📝 Parsing LLM response...")
            
            # Check response length - if too short, might be truncated
            if len(llm_response) < 200:
                print(f"  ⚠️  Warning: Very short response ({len(llm_response)} chars) - might be incomplete")
            
            fixed_files = self._parse_fixes(llm_response)
            
            print(f"  ✅ Fixes parsed: {len(fixed_files['files'])} files")
            
            # Étape 6: Appliquer les fixes avec le toolkit
            print(f"✍️  Applying fixes to disk...")
            result = apply_fixes(fixed_files, state.target_dir)
            
            if not result['success']:
                raise Exception(f"Failed to apply fixes: {result.get('errors')}")
            
            print(f"  ✅ Fixes applied successfully")
            for modified_file in result['files_modified']:
                print(f"     ✏️  {modified_file}")
            
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
            print(f"✅ {self.name}: Completed successfully\n")
            return state
            
        except Exception as e:
            print(f"❌ {self.name}: Failed with error: {e}")
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
                    "error": str(e),
                    "iteration": state.current_iteration
                },
                status="FAILED"
            )
            
            return state
    
    def _build_fix_prompt(self, files_text: str, plan: list, iteration: int, previous_errors: list) -> str:
        """Construit le prompt pour Gemini"""
        
        # Contexte d'itération
        iteration_context = f"This is iteration {iteration}."
        if iteration == 1:
            iteration_context += " This is your first attempt."
        
        # Section feedback des erreurs précédentes
        feedback_section = ""
        if iteration > 1 and previous_errors:
            errors_preview = "\n".join(previous_errors[:3])  # Limiter à 3 erreurs
            feedback_section = f"""
⚠️ **CRITICAL - Previous Attempt Failed:**
The code you fixed in the previous iteration did not pass the tests.
Here are the test errors you MUST fix:

{errors_preview}

You MUST address these specific errors in your current fixes.
Learn from the previous attempt and fix the root cause.
"""
        
        prompt = f"""You are an expert Python code fixer. {iteration_context}

{feedback_section}

**Refactoring Plan to Apply:**
{chr(10).join(f'{i+1}. {action}' for i, action in enumerate(plan))}

**Code to Fix:**
{files_text}

**Your Task:**
1. Apply ALL fixes from the refactoring plan above
2. Fix syntax errors FIRST (missing colons, parentheses, quotes, indentation)
3. Ensure the code is syntactically valid Python
4. Maintain all existing functionality
5. Keep all imports and dependencies
6. Add missing docstrings where needed

**Critical Rules:**
- Return COMPLETE file contents (not partial code or diffs)
- Every function/class must be complete and properly indented
- Test syntax mentally: does it have all colons, parentheses, quotes?
- If the plan mentions specific line numbers, fix those exact locations
- Do NOT add new features, only fix what's broken
- Preserve all existing logic and behavior

**Output Format:**
Return a JSON object with this EXACT structure:

{{
  "files": [
    {{
      "path": "/absolute/path/to/file.py",
      "content": "complete fixed code here"
    }}
  ]
}}

CRITICAL JSON RULES:
1. NO markdown code blocks (no ```)
2. Use double quotes ONLY - never triple quotes or Python docstring syntax
3. For newlines in content: use actual \\n character (JSON will handle it)
4. For quotes inside strings: use \\" 
5. Keep all file content on ONE line with \\n for line breaks
6. Test mentally: can standard JSON parser read this?

Example of CORRECT format:
{{"files": [{{"path": "test.py", "content": "def hello():\\n    return 'world'\\n"}}]}}

Now generate the fixed code following these rules EXACTLY.
- No markdown, no code blocks, no explanations
"""
        return prompt
    
    def _parse_fixes(self, llm_response: str) -> dict:
        """Parse la réponse de Gemini pour extraire les fichiers corrigés"""
        try:
            # Nettoyer la réponse (enlever markdown si présent)
            response = llm_response.strip()
            
            # Enlever les backticks markdown si présents
            if response.startswith("```"):
                lines = response.split("\n")
                # Trouver la première ligne sans ```
                start_idx = 0
                for i, line in enumerate(lines):
                    if not line.strip().startswith("```"):
                        start_idx = i
                        break
                # Trouver la dernière ligne sans ```
                end_idx = len(lines)
                for i in range(len(lines)-1, -1, -1):
                    if not lines[i].strip().startswith("```"):
                        end_idx = i + 1
                        break
                response = "\n".join(lines[start_idx:end_idx])
            
            response = response.replace("```json", "").replace("```", "").strip()
            
            # Fix common LLM mistakes: triple quotes in JSON
            # Replace Python triple quotes with escaped quotes
            if '"""' in response:
                print(f"  ⚠️  Fixing triple quotes in LLM response...")
                # More robust replacement: handle docstrings properly
                import re
                # Replace """ with escaped quotes, preserving the content
                response = re.sub(r'"""([^"]*?)"""', r'"\1"', response, flags=re.DOTALL)
            
            # Parser le JSON
            try:
                data = json.loads(response)
            except json.JSONDecodeError as e:
                # If JSON parsing fails, print more context
                print(f"  ❌ JSON parse error: {e}")
                print(f"  📄 Full response ({len(response)} chars):")
                print(f"     {response[:500]}...")
                if len(response) < 1000:
                    print(f"\n  Complete response:\n{response}")
                raise ValueError(f"LLM returned invalid JSON: {e}")
            
            # Valider la structure
            if not isinstance(data, dict):
                raise ValueError("Response must be a JSON object")
            
            if 'files' not in data:
                raise ValueError("Missing 'files' key in response")
            
            if not isinstance(data['files'], list):
                raise ValueError("'files' must be a list")
            
            # Valider chaque fichier
            for i, file_entry in enumerate(data['files']):
                if not isinstance(file_entry, dict):
                    raise ValueError(f"File entry {i} must be a dict")
                
                if 'path' not in file_entry:
                    raise ValueError(f"File entry {i} missing 'path'")
                
                if 'content' not in file_entry:
                    raise ValueError(f"File entry {i} missing 'content'")
            
            print(f"  ✅ JSON parsed successfully")
            return data
            
        except json.JSONDecodeError as e:
            print(f"  ❌ Failed to parse JSON: {e}")
            print(f"  Response preview: {llm_response[:200]}...")
            raise ValueError(f"LLM returned invalid JSON: {e}")
        
        except ValueError as e:
            print(f"  ❌ Validation error: {e}")
            raise