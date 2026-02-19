"""
Test du toolkit Fixer
"""
import json
import sys
from pathlib import Path
# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root)) 

from src.tools.fixer_toolkit import (
    prepare_context_for_fixer,
    apply_fixes,
    format_files_for_llm
)

def test_fixer_toolkit():
    """Test des fonctions du Fixer"""
    print("\n" + "="*60)
    print("🔧 Testing Fixer Toolkit")
    print("="*60)
    
    target_dir = str(project_root / "sandbox" / "test_toolkit")
    
    try:
        # Simuler un audit_report (normalement vient de l'Auditor)
        mock_audit_report = {
            "pylint_score": 3.5,
            "issues": [
                {"file": "simple_bug.py", "line": 4, "message": "Missing colon"},
                {"file": "simple_bug.py", "line": 7, "message": "Bad spacing"}
            ],
            "plan": [
                "Fix syntax error on line 4",
                "Fix spacing issues on line 7"
            ],
            "files_analyzed": [str(Path(target_dir) / "simple_bug.py")]
        }
        
        # Test 1: Préparer le contexte
        print("\n📦 Test 1: Preparing context for Fixer...")
        context = prepare_context_for_fixer(
            files_to_fix=mock_audit_report['files_analyzed'],
            audit_report=mock_audit_report,
            target_dir=target_dir,
            max_files=3
        )
        
        assert 'files' in context, "Missing files in context"
        assert 'plan' in context, "Missing plan in context"
        print(f"  ✅ Context prepared")
        print(f"  📂 Files in context: {len(context['files'])}")
        print(f"  📋 Plan items: {len(context['plan'])}")
        
        # Test 2: Formater les fichiers pour LLM
        print("\n📝 Test 2: Formatting files for LLM...")
        formatted = format_files_for_llm(context['files'])
        assert isinstance(formatted, str), "Should return a string"
        print(f"  ✅ Files formatted (length: {len(formatted)} chars)")
        print(f"  Preview:\n{formatted[:300]}...")
        
        # Test 3: Appliquer des fixes (avec du code corrigé manuellement)
        print("\n✍️  Test 3: Applying fixes...")
        
        # Simuler une réponse LLM corrigée
        fixed_code = '''"""Simple fixed code"""

def add_numbers(a, b):  # Fixed: added colon
    """Add two numbers"""
    return a + b

def multiply(x, y):  # Fixed: spacing
    """Multiply two numbers"""
    result = x * y  # Fixed: spacing
    return result
'''
        
        mock_llm_response = {
            "files": [
                {
                    "path": str(Path(target_dir) / "simple_bug.py"),
                    "content": fixed_code
                }
            ]
        }
        
        # Créer une backup d'abord
        original_file = Path(target_dir) / "simple_bug.py"
        backup_file = Path(target_dir) / "simple_bug.py.backup"
        if original_file.exists():
            import shutil
            shutil.copy(original_file, backup_file)
            print(f"  💾 Backup created: {backup_file}")
        
        # Appliquer les fixes
        result = apply_fixes(mock_llm_response, target_dir)
        
        assert result['success'], f"Apply fixes failed: {result.get('errors')}"
        print(f"  ✅ Fixes applied successfully")
        print(f"  📝 Files modified: {result['files_modified']}")
        
        # Vérifier que le fichier a été modifié
        modified_content = original_file.read_text()
        assert "def add_numbers(a, b):" in modified_content, "Fix not applied"
        print(f"  ✅ File content verified")
        
        # Restaurer le backup
        if backup_file.exists():
            shutil.copy(backup_file, original_file)
            backup_file.unlink()
            print(f"  🔄 Original file restored")
        
        print("\n✅ Fixer Toolkit: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    success = test_fixer_toolkit()
    sys.exit(0 if success else 1)