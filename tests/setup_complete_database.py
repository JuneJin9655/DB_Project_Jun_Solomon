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

def setup_complete_database():
    """Run all database setup scripts in the correct order"""
    print("Starting complete database setup...")
    
    # Get the current directory (tests)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Step 1: Reset database and create initial structure
    print("\n=== Step 1: Resetting database and creating structure ===")
    reset_module = load_module("reset_and_create_data", os.path.join(current_dir, "reset_and_create_data.py"))
    reset_module.reset_and_create_data()
    
    # Step 2: Insert basic clinic data
    print("\n=== Step 2: Inserting clinic data ===")
    clinic_module = load_module("insert_clinic_data", os.path.join(current_dir, "insert_clinic_data.py"))
    clinic_module.insert_clinic_data()
    
    # Step 3: Insert personnel data
    print("\n=== Step 3: Inserting personnel data ===")
    personnel_module = load_module("insert_personnel_data", os.path.join(current_dir, "insert_personnel_data.py"))
    personnel_module.insert_personnel_data()
    
    # Step 4: Insert patient data
    print("\n=== Step 4: Inserting patient data ===")
    patient_module = load_module("insert_patient_data", os.path.join(current_dir, "insert_patient_data.py"))
    patient_module.insert_patient_data()
    
    # Step 5: Insert bed data
    print("\n=== Step 5: Inserting bed data ===")
    bed_module = load_module("insert_bed_data", os.path.join(current_dir, "insert_bed_data.py"))
    bed_module.insert_bed_data()
    
    # Step 6: Insert inpatient data
    print("\n=== Step 6: Inserting inpatient data ===")
    inpatient_module = load_module("insert_inpatient_data", os.path.join(current_dir, "insert_inpatient_data.py"))
    inpatient_module.insert_inpatient_data()
    
    # Step 7: Insert illness data
    print("\n=== Step 7: Inserting illness data ===")
    illness_module = load_module("insert_illness_data", os.path.join(current_dir, "insert_illness_data.py"))
    illness_module.insert_illness_data()
    
    # Step 8: Insert consultation and diagnosis data
    print("\n=== Step 8: Inserting consultation data ===")
    consultation_module = load_module("insert_consultation_data", os.path.join(current_dir, "insert_consultation_data.py"))
    consultation_module.insert_consultation_data()
    
    # Step 9: Insert medication data
    print("\n=== Step 9: Inserting medication data ===")
    medication_module = load_module("insert_medication_data", os.path.join(current_dir, "insert_medication_data.py"))
    medication_module.insert_medication_data()
    
    # Step 10: Insert prescription data
    print("\n=== Step 10: Inserting prescription data ===")
    prescription_module = load_module("insert_prescription_data", os.path.join(current_dir, "insert_prescription_data.py"))
    prescription_module.insert_prescription_data()
    
    # Step 11: Insert surgery type data
    print("\n=== Step 11: Inserting surgery type data ===")
    surgery_type_module = load_module("insert_surgery_types", os.path.join(current_dir, "insert_surgery_types.py"))
    surgery_type_module.insert_surgery_types()
    
    # Step 12: Insert surgery data
    print("\n=== Step 12: Inserting surgery data ===")
    surgery_module = load_module("insert_surgery_data", os.path.join(current_dir, "insert_surgery_data.py"))
    surgery_module.insert_surgery_data()
    
    # Step 13: Insert surgery schedules
    print("\n=== Step 13: Inserting surgery schedules ===")
    surgery_schedule_module = load_module("insert_surgery_schedules", os.path.join(current_dir, "insert_surgery_schedules.py"))
    surgery_schedule_module.insert_surgery_schedules()
    
    # Step 14: Run nurse data updates (all steps)
    print("\n=== Step 14: Running nurse data updates ===")
    
    # Add nurse skills
    print("    14.1: Adding nurse skills")
    nurse_skills_module = load_module("add_nurse_skills", os.path.join(current_dir, "add_nurse_skills.py"))
    nurse_skills_module.add_nurse_skills()
    
    # Update nursing units
    print("    14.2: Updating nursing units")
    nursing_units_module = load_module("update_nursing_units", os.path.join(current_dir, "update_nursing_units.py"))
    nursing_units_module.update_nursing_units()
    
    # Update nurse experience and grades
    print("    14.3: Updating nurse experience and grades")
    nurse_experience_module = load_module("update_nurse_experience", os.path.join(current_dir, "update_nurse_experience.py"))
    nurse_experience_module.update_nurse_experience()
    
    # Update numeric nursing units for nurses
    print("    14.4: Updating numeric nursing units for nurses")
    nurse_numeric_units_module = load_module("update_nurse_nursing_units", os.path.join(current_dir, "update_nurse_nursing_units.py"))
    nurse_numeric_units_module.update_nurse_nursing_units()
    
    # Step 15: Update inpatient nursing units
    print("\n=== Step 15: Updating inpatient nursing units ===")
    inpatient_units_module = load_module("update_inpatient_nursing_units", os.path.join(current_dir, "update_inpatient_nursing_units.py"))
    inpatient_units_module.update_inpatient_nursing_units()
    
    # Step 16: Balance relationships (final check)
    print("\n=== Step 16: Balancing relationships (final check) ===")
    balance_module = load_module("balance_relationships", os.path.join(current_dir, "balance_relationships.py"))
    balance_module.balance_relationships()
    
    # Step 17: Verify final state
    print("\n=== Step 17: Checking final data state ===")
    check_module = load_module("check_data", os.path.join(current_dir, "check_data.py"))
    check_module.check_data()
    
    print("\nDatabase setup complete! You can now run 'flask run' to start the application.")

if __name__ == "__main__":
    setup_complete_database() 