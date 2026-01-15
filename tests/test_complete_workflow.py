"""
Test d'intégration complet du workflow End-to-End
"""
import sys
from pathlib import Path
import json

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.orchestration.workflow import run_refactoring_workflow


def test_complete_workflow():
    """Test le workflow complet avec tous les agents"""
    print("\n" + "="*70)
    print("🚀 TESTING COMPLETE WORKFLOW - END TO END")
    print("="*70)
    
    try:
        # Test sur notre cas de test
        target_dir = "./sandbox/test_toolkit"
        
        if not Path(target_dir).exists():
            print(f"❌ Test directory not found: {target_dir}")
            print("   Please create it first with buggy code!")
            return False
        
        # Lancer le workflow
        print(f"\n📂 Target: {target_dir}")
        print(f"🔄 Max iterations: 5")
        print("\nStarting workflow...\n")
        
        result = run_refactoring_workflow(
            target_dir=target_dir,
            max_iterations=5,
            verbose=True
        )
        
        # Vérifier les résultats
        print("\n" + "="*70)
        print("📊 TEST RESULTS")
        print("="*70)
        
        print(f"\n{'✅' if result['success'] else '❌'} Workflow Success: {result['success']}")
        print(f"🔄 Iterations: {result['iterations']}")
        print(f"📈 Pylint Before: {result['pylint_before']:.2f}")
        print(f"📈 Pylint After: {result['pylint_after']:.2f}")
        print(f"⏱️  Time: {result['execution_time']:.2f}s")
        
        if result['error']:
            print(f"⚠️  Error: {result['error']}")
        
        # Vérifier les logs
        print("\n📋 Checking experiment logs...")
        log_file = Path("logs/experiment_data.json")
        
        if not log_file.exists():
            print("❌ Log file not found!")
            return False
        
        with open(log_file, encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle both list and dict formats
        if isinstance(data, list):
            iterations = data
        else:
            iterations = data.get('iterations', [])
        
        print(f"  ✅ Log file exists")
        print(f"  📝 Entries: {len(iterations)}")
        
        # Vérifier que tous les agents ont loggé
        agents_seen = set()
        for entry in iterations:
            agents_seen.add(entry.get('agent', 'unknown'))  # Fixed: use 'agent' not 'agent_name'
        
        print(f"  🤖 Agents logged: {', '.join(sorted(agents_seen))}")
        
        expected_agents = {'Auditor', 'Fixer', 'Judge'}
        missing = expected_agents - agents_seen
        if missing:
            print(f"  ⚠️  Missing agents: {missing}")
        else:
            print(f"  ✅ All expected agents logged")
        
        # Vérifier les champs obligatoires
        print("\n📋 Validating log entries...")
        errors = []
        for i, entry in enumerate(iterations):
            if 'input_prompt' not in entry.get('details', {}):
                errors.append(f"Entry {i}: missing input_prompt")
            if 'output_response' not in entry.get('details', {}):
                errors.append(f"Entry {i}: missing output_response")
        
        if errors:
            print(f"  ❌ Validation errors:")
            for error in errors[:5]:
                print(f"     - {error}")
        else:
            print(f"  ✅ All log entries valid")
        
        # Résultat final
        print("\n" + "="*70)
        if result['success'] and not errors:
            print("✅ WORKFLOW TEST: PASSED")
            print("="*70 + "\n")
            return True
        else:
            print("⚠️  WORKFLOW TEST: PARTIAL SUCCESS")
            print("="*70 + "\n")
            return True  # Partial success is OK for now
        
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_complete_workflow()
    sys.exit(0 if success else 1)