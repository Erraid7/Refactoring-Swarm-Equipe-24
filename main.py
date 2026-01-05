import argparse
import sys
from pathlib import Path
from src.orchestration.workflow import run_refactoring_workflow

def main():
    """Point d'entrée principal du système"""
    parser = argparse.ArgumentParser(
        description="The Refactoring Swarm - Multi-agent code refactoring"
    )
    parser.add_argument(
        '--target_dir',
        type=str,
        required=True,
        help='Directory containing Python code to refactor'
    )
    parser.add_argument(
        '--max_iterations',
        type=int,
        default=10,
        help='Maximum number of refactoring iterations (default: 10)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Validation
    target_path = Path(args.target_dir)
    if not target_path.exists():
        print(f"❌ Error: Directory '{args.target_dir}' does not exist")
        sys.exit(1)
    
    print(f"🚀 Starting Refactoring Swarm...")
    print(f"📂 Target: {args.target_dir}")
    print(f"🔄 Max iterations: {args.max_iterations}")
    print("-" * 50)
    
    try:
        # Lancer le workflow
        result = run_refactoring_workflow(
            target_dir=args.target_dir,
            max_iterations=args.max_iterations,
            verbose=args.verbose
        )
        
        if result['success']:
            print(f"\n✅ Refactoring completed successfully!")
            print(f"📊 Pylint improvement: {result['pylint_before']} → {result['pylint_after']}")
            print(f"🔄 Total iterations: {result['iterations']}")
        else:
            print(f"\n❌ Refactoring failed: {result['error']}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()