"""
Test du toolkit Auditor
"""
import json
import sys
from pathlib import Path
# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.tools.auditor_toolkit import (
    analyze_project, 
    format_issues_for_llm,
    get_files_to_analyze
)

def test_analyze_project():
    """Test de l'analyse complète d'un projet"""
    print("\n" + "="*60)
    print("🔍 Testing Auditor Toolkit")
    print("="*60)
    
    target_dir = str(project_root / "sandbox" / "test_toolkit")
    
    # Vérifier que le dossier existe
    if not Path(target_dir).exists():
        print(f"❌ Test directory not found: {target_dir}")
        print("   Create it first with the buggy code!")
        return False
    
    try:
        # Test 1: Analyser le projet
        print("\n📊 Test 1: Analyzing project...")
        audit_report = analyze_project(target_dir)
        
        # Vérifier la structure du rapport
        assert 'pylint_score' in audit_report, "Missing pylint_score"
        assert 'issues' in audit_report, "Missing issues"
        assert 'files_analyzed' in audit_report, "Missing files_analyzed"
        
        print(f"  ✅ Project analyzed successfully")
        print(f"  📈 Pylint Score: {audit_report['pylint_score']:.2f}/10")
        print(f"  📂 Files analyzed: {len(audit_report['files_analyzed'])}")
        print(f"  ⚠️  Issues found: {len(audit_report['issues'])}")
        
        # Test 2: Formatter les issues pour LLM
        print("\n📝 Test 2: Formatting issues for LLM...")
        formatted = format_issues_for_llm(audit_report['issues'], max_issues=5)
        assert isinstance(formatted, str), "formatted should be a string"
        assert len(formatted) > 0, "formatted string is empty"
        print(f"  ✅ Issues formatted (length: {len(formatted)} chars)")
        print(f"  Preview:\n{formatted[:200]}...")
        
        # Test 3: Obtenir la liste des fichiers
        print("\n📁 Test 3: Getting files to analyze...")
        files = get_files_to_analyze(target_dir)
        assert len(files) > 0, "No Python files found"
        print(f"  ✅ Found {len(files)} Python files")
        for f in files:
            print(f"     - {f}")
        
        print("\n✅ Auditor Toolkit: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    success = test_analyze_project()
    sys.exit(0 if success else 1)