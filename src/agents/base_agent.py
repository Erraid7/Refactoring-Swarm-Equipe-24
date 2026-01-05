from abc import ABC, abstractmethod
from typing import Dict, Any
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
        Pour l'instant, retourne un placeholder
        """
        # TODO: Implémenter l'appel réel à Gemini
        return f"[STUB] LLM response for prompt: {prompt[:50]}..."