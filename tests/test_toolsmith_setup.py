"""
Test de vérification de l'installation des toolkits du Toolsmith
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_toolkit_imports():
    """Vérifie que tous les toolkits peuvent être importés"""
    print("🔍 Testing toolkit imports...")
    
    try:
        from src.tools.auditor_toolkit import analyze_project, format_issues_for_llm
        print("  ✅ auditor_toolkit imported successfully")
    except ImportError as e:
        print(f"  ❌ Failed to import auditor_toolkit: {e}")
        return False
    
    try:
        from src.tools.fixer_toolkit import apply_fixes, prepare_context_for_fixer
        print("  ✅ fixer_toolkit imported successfully")
    except ImportError as e:
        print(f"  ❌ Failed to import fixer_toolkit: {e}")
        return False
    
    try:
        from src.tools.judge_toolkit import evaluate_code, format_test_feedback_for_fixer
        print("  ✅ judge_toolkit imported successfully")
    except ImportError as e:
        print(f"  ❌ Failed to import judge_toolkit: {e}")
        return False
    
    print("\n✅ All toolkits are properly installed!")
    return True

if __name__ == "__main__":
    success = test_toolkit_imports()
    sys.exit(0 if success else 1)