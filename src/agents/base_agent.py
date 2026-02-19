"""
Classe de base pour tous les agents
Gère l'appel au LLM Gemini
"""

from abc import ABC, abstractmethod
from typing import Optional
import os
from dotenv import load_dotenv

# Import de Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️  Warning: google-generativeai not installed")

from src.orchestration.state import RefactoringState


class BaseAgent(ABC):
    """Classe de base pour tous les agents"""
    
    def __init__(self, name: str, model: str = "gemini-2.5-flash"):
        self.name = name
        self.model = model
        self.llm_client = None
        
        # Charger la clé API
        load_dotenv()
        self.api_key = os.getenv("GOOGLE_API_KEY")
        
        # Initialiser Gemini si disponible
        if GEMINI_AVAILABLE and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.llm_client = genai.GenerativeModel(self.model)
                print(f"✅ {self.name}: Gemini initialized with model {self.model}")
            except Exception as e:
                print(f"⚠️  {self.name}: Failed to initialize Gemini: {e}")
                self.llm_client = None
        else:
            if not GEMINI_AVAILABLE:
                print(f"⚠️  {self.name}: Gemini library not available")
            if not self.api_key:
                print(f"⚠️  {self.name}: GOOGLE_API_KEY not found in .env")
    
    @abstractmethod
    def execute(self, state: RefactoringState) -> RefactoringState:
        """
        Exécute l'agent et retourne l'état mis à jour
        Doit être implémenté par chaque agent
        """
        pass
    
    def _call_llm(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2048) -> str:
        """
        Appelle le LLM Gemini et retourne la réponse
        
        Args:
            prompt: Le prompt à envoyer
            temperature: Créativité (0.0 = déterministe, 1.0 = créatif)
            max_tokens: Nombre maximum de tokens dans la réponse
        
        Returns:
            La réponse du LLM sous forme de string
        """
        # Mode STUB si Gemini n'est pas disponible
        if not self.llm_client:
            print(f"⚠️  {self.name}: LLM not available, using STUB mode")
            return self._stub_response(prompt)
        
        try:
            print(f"🤖 {self.name}: Calling Gemini API...")
            print(f"   Model: {self.model}")
            print(f"   Temperature: {temperature}")
            print(f"   Prompt length: {len(prompt)} chars")
            
            # Configuration de génération
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                candidate_count=1
            )
            
            # Appel à Gemini
            response = self.llm_client.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Extraire le texte de la réponse
            if response.candidates:
                response_text = response.text
                print(f"✅ {self.name}: Received response ({len(response_text)} chars)")
                return response_text
            else:
                print(f"⚠️  {self.name}: No candidates in response")
                return self._stub_response(prompt)
            
        except Exception as e:
            print(f"❌ {self.name}: LLM call failed: {e}")
            print(f"   Falling back to STUB mode")
            return self._stub_response(prompt)
    
    def _stub_response(self, prompt: str) -> str:
        """
        Réponse de fallback quand Gemini n'est pas disponible
        Utilisé pour tester le workflow sans API
        """
        # Analyser le prompt pour donner une réponse semi-intelligente
        prompt_lower = prompt.lower()
        
        # Si c'est l'Auditor (demande un plan)
        if "plan" in prompt_lower or "refactoring" in prompt_lower:
            return '''{
  "plan": [
    "Fix syntax errors (missing colons, parentheses)",
    "Add missing imports",
    "Fix indentation issues",
    "Add docstrings to functions",
    "Improve variable naming"
  ]
}'''
        
        # Si c'est le Fixer (demande du code corrigé)
        elif "fix" in prompt_lower or "content" in prompt_lower:
            return '''{
  "files": [
    {
      "path": "/path/to/file.py",
      "content": "# Fixed code would go here\\npass"
    }
  ]
}'''
        
        # Réponse générique
        else:
            return "STUB: LLM response"