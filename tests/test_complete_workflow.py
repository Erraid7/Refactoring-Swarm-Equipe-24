"""
Test d'intégration complet du workflow
"""
import sys
from pathlib import Path
# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_complete_workflow():
    """Test le workflow complet avec les agents intégrés"""
    print("\n" + "="*70)
    print("🚀 TESTING COMPLETE WORKFLOW WITH INTEGRATED AGENTS")
    print("="*70)
    
    try:
        from src.orchestration.workflow import run_refactoring_workflow
        
        # Test sur notre cas de test
        target_dir = "./sandbox/test_toolkit"
        
        print(f"\n📂 Target directory: {target_dir}")
        print(f"🔄 Max iterations: 3 (for testing)")
        
        # Lancer le workflow
        result = run_refactoring_workflow(
            target_dir=target_dir,
            max_iterations=3,
            verbose=True
        )
        
        # Vérifier les résultats
        print("\n" + "="*70)
        print("📊 WORKFLOW RESULTS")
        print("="*70)
        
        print(f"Success: {result['success']}")
        print(f"Iterations: {result['iterations']}")
        print(f"Pylint Before: {result['pylint_before']:.2f}")
        print(f"Pylint After: {result['pylint_after']:.2f}")
        print(f"Execution Time: {result['execution_time']:.2f}s")
        
        if result['error']:
            print(f"Error: {result['error']}")
        
        # Vérifier les logs
        print("\n📋 Checking logs...")
        log_file = Path("logs/experiment_data.json")
        if log_file.exists():
            import json
            with open(log_file) as f:
                data = json.load(f)
            
            # The log file is an array of log entries
            if isinstance(data, list):
                iterations = data
                print(f"  ✅ Log file exists with {len(iterations)} entries")
                
                # Vérifier que tous les agents ont loggé
                agents_seen = set()
                for entry in iterations:
                    if isinstance(entry, dict):
                        agents_seen.add(entry.get('agent', 'unknown'))
                
                expected_agents = {'Auditor', 'Fixer', 'Judge'}
                if expected_agents.issubset(agents_seen):
                    print(f"  ✅ All agents logged their actions")
                else:
                    print(f"  ⚠️  Missing agents in logs: {expected_agents - agents_seen}")
            else:
                print(f"  ⚠️  Unexpected log file format")
        else:
            print(f"  ❌ Log file not found!")
        
        print("\n✅ WORKFLOW TEST COMPLETED")
        return True
        
    except Exception as e:
        print(f"\n❌ Workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_workflow()
    sys.exit(0 if success else 1)