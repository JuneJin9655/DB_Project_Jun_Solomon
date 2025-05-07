from app import create_app, db
import os
import importlib.util
import sys

def load_module(module_name, file_path):
    """Dynamically load a module from a file path"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def update_all_nurse_data():
    """Run all nurse data update scripts in the correct order"""
    print("Starting complete update of nurse data...")
    
    # Get the current directory (tests)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Step 1: Add nurse skills data
    print("\n=== Step 1: Adding nurse skills ===")
    nurse_skills_module = load_module("add_nurse_skills", os.path.join(current_dir, "add_nurse_skills.py"))
    nurse_skills_module.add_nurse_skills()
    
    # Step 2: Update nursing units
    print("\n=== Step 2: Updating nursing units ===")
    nursing_units_module = load_module("update_nursing_units", os.path.join(current_dir, "update_nursing_units.py"))
    nursing_units_module.update_nursing_units()
    
    # Step 3: Update nurse experience and grades
    print("\n=== Step 3: Updating nurse experience and grades ===")
    nurse_experience_module = load_module("update_nurse_experience", os.path.join(current_dir, "update_nurse_experience.py"))
    nurse_experience_module.update_nurse_experience()
    
    # Step 4: Verify data consistency with general balance_relationships
    print("\n=== Step 4: Verifying data consistency ===")
    balance_module = load_module("balance_relationships", os.path.join(current_dir, "balance_relationships.py"))
    balance_module.balance_relationships()
    
    # Step 5: Verify final state
    print("\n=== Step 5: Checking final data state ===")
    check_module = load_module("check_data", os.path.join(current_dir, "check_data.py"))
    check_module.check_data()
    
    print("\nAll nurse data has been successfully updated!")

if __name__ == "__main__":
    update_all_nurse_data() 