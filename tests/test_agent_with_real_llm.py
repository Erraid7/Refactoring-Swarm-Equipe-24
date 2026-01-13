"""
Test d'un agent avec appel LLM réel
"""

# Add project root to Python path
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agents.base_agent import BaseAgent
from src.orchestration.state import RefactoringState

class SimpleTestAgent(BaseAgent):
    """Agent de test minimaliste"""
    
    def execute(self, state: RefactoringState) -> RefactoringState:
        print(f"\n🤖 {self.name}: Testing LLM call...")
        
        prompt = """You are a Python expert. Analyze this buggy code and return a JSON plan.

Code:
```python
def add(a, b)  # Missing colon
    return a + b
```

Return a JSON object with a refactoring plan:
{
  "plan": ["action 1", "action 2", ...]
}
"""
        
        response = self._call_llm(prompt, temperature=0.3)
        
        print(f"📝 LLM Response:")
        print(response)
        
        return state

def test_simple_agent():
    """Test un agent simple avec LLM"""
    print("\n" + "="*60)
    print("🧪 Testing Agent with Real LLM")
    print("="*60)
    
    try:
        # Créer un état de test
        state = RefactoringState(target_dir="./sandbox/test")
        
        # Créer et exécuter l'agent
        agent = SimpleTestAgent("TestAgent")
        state = agent.execute(state)
        
        print("\n✅ Agent test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    success = test_simple_agent()
    sys.exit(0 if success else 1)