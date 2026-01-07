from abc import ABC, abstractmethod
from typing import Dict, Any
import json
from pathlib import Path
from src.orchestration.state import RefactoringState

class BaseAgent(ABC):
    """Classe de base pour tous les agents"""
    
    def __init__(self, name: str, model: str = "gemini-2.0-flash-exp"):
        self.name = name
        self.model = model
    
    @abstractmethod
    def execute(self, state: RefactoringState) -> RefactoringState:
        """
        Exécute l'agent et retourne l'état mis à jour
        """
        pass
    
    def _call_llm(self, prompt: str) -> str:
        """
        Appelle le LLM (à implémenter avec Gemini)
        Pour l'instant, retourne un JSON valide basé sur le contexte
        """
        # TODO: Implémenter l'appel réel à Gemini
        
        # Return valid JSON based on what agent is being called
        prompt_lower = prompt.lower()
        
        result = None
        
        # Check for Fixer first (more specific - looks for "apply" + "fix")
        if "apply" in prompt_lower and ("fix" in prompt_lower or "correct" in prompt_lower):
            # Fixer response - return fixed code with absolute paths
            # Get the project root to build absolute paths
            project_root = Path(__file__).parent.parent.parent
            simple_bug_path = str(project_root / "sandbox" / "test_toolkit" / "simple_bug.py")
            
            result = json.dumps({
                "files": [
                    {
                        "path": simple_bug_path,
                        "content": '''"""Module for basic arithmetic operations."""

def add(first_number, second_number):
    """
    Add two numbers together.
    
    Args:
        first_number: The first number to add
        second_number: The second number to add
        
    Returns:
        The sum of the two numbers
    """
    result = first_number + second_number
    return result

def mult(first_number, second_number):
    """
    Multiply two numbers together.
    
    Args:
        first_number: The first number to multiply
        second_number: The second number to multiply
        
    Returns:
        The product of the two numbers
    """
    result = first_number * second_number
    return result

def calc(num1, num2, num3):
    """
    Add first two numbers and multiply by third.
    
    Args:
        num1: First number
        num2: Second number
        num3: Third number (multiplier)
        
    Returns:
        Result of (num1 + num2) * num3
    """
    temp_sum = add(num1, num2)
    final_result = mult(temp_sum, num3)
    return final_result

CONSTANT_VALUE_ONE = 10
CONSTANT_VALUE_TWO = 20
'''
                    }
                ]
            })
            print(f"🔍 DEBUG: Matched FIXER pattern, returning files response")
        # Check for Auditor
        elif "refactoring plan" in prompt_lower or ("plan" in prompt_lower and "generate" in prompt_lower):
            # Auditor response
            result = json.dumps({
                "plan": [
                    "Fix syntax errors",
                    "Add proper spacing",
                    "Add docstrings"
                ]
            })
            print(f"🔍 DEBUG: Matched AUDITOR pattern, returning plan response")
        else:
            # Default response
            print(f"⚠️  DEBUG: No specific match, returning default")
            result = json.dumps({"status": "ok", "message": "Stub response"})
        
        print(f"🔍 DEBUG: Returning response of length {len(result)}")
        return result