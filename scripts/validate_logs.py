
import json
import sys

def validate_logs(filepath="logs/experiment_data.json"):
    print(f"🔍 Validation de {filepath}...")
    
    try:
        with open(filepath) as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ Fichier introuvable!")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ JSON invalide: {e}")
        return False
    
    errors = []
    
    
    if "experiment_id" not in data:
        errors.append("experiment_id manquant")
    if "iterations" not in data:
        errors.append("iterations manquant")
    
    
    valid_actions = {"ANALYSIS", "FIX", "DEBUG", "GENERATION"}
    
    for i, entry in enumerate(data.get("iterations", [])):
        prefix = f"Entrée #{i+1}"
        
        if "input_prompt" not in entry.get("details", {}):
            errors.append(f"{prefix}: input_prompt manquant")
        if "output_response" not in entry.get("details", {}):
            errors.append(f"{prefix}: output_response manquant")
        if entry.get("action") not in valid_actions:
            errors.append(f"{prefix}: action invalide '{entry.get('action')}'")
    
    if errors:
        print("❌ Erreurs trouvées:")
        for e in errors:
            print(f"  - {e}")
        return False
    
    print(f"✅ Log valide! ({len(data['iterations'])} entrées)")
    return True

if __name__ == "__main__":
    success = validate_logs()
    sys.exit(0 if success else 1)