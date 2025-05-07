from app import create_app, db
from sqlalchemy import text
import os
import importlib

def reset_database():
    """Delete all data from the database"""
    app = create_app()
    with app.app_context():
        # Tables to clear in reverse order of dependencies
        tables = [
            'NurseSkill', 'SurgerySchedule', 'Prescription', 'Diagnosis', 
            'Consultation', 'Inpatient', 'DrugInteraction', 'Medication', 
            'Surgeon', 'Nurse', 'Physician', 'ClinicPersonnel', 'Patient', 
            'SurgerySkill', 'SurgeryType', 'OperatingRoom', 'Bed',
            'Illness', 'Allergy', 'MedicalCorporation', 'Owner', 'Clinic'
        ]
        
        for table in tables:
            try:
                db.session.execute(text(f"DELETE FROM {table}"))
                print(f"Cleared table: {table}")
            except Exception as e:
                print(f"Error clearing table {table}: {e}")
                db.session.rollback()
        
        try:
            db.session.commit()
            print("All tables cleared successfully")
        except Exception as e:
            db.session.rollback()
            print(f"Error committing transaction: {e}")

def create_new_data():
    """Import and run all data creation scripts in the correct order"""
    # List of scripts to run in order
    scripts = [
        "insert_clinic_data",        # First: basic clinic and personnel records
        "insert_bed_data",           # Beds for inpatients
        "insert_patient_data",       # All patients
        "insert_personnel_data",     # All personnel (physicians, nurses, surgeons)
        "insert_inpatient_data",     # Link patients to beds and nurses
        "insert_illness_data",       # Illnesses and allergies
        "insert_consultation_data",  # Consultations and diagnoses
        "insert_medication_data",    # Medications and drug interactions  
        "insert_prescription_data",  # Prescriptions
        "insert_surgery_types",      # Surgery types and skills
        "insert_surgery_schedules",  # Surgery schedules
        "balance_relationships"      # Ensure all relationships are balanced
    ]
    
    for script in scripts:
        try:
            # Check if the script file exists
            if os.path.exists(f"{script}.py"):
                # Import the script and run its main function
                print(f"\nRunning {script}...")
                module = importlib.import_module(script)
                
                # Determine which function to call
                if hasattr(module, script):
                    func = getattr(module, script)
                    func()
                elif hasattr(module, "insert_data"):
                    module.insert_data()
                else:
                    print(f"No entry function found in {script}")
            else:
                print(f"Script {script}.py not found")
        except Exception as e:
            print(f"Error running {script}: {e}")

if __name__ == "__main__":
    print("Resetting database...")
    reset_database()
    print("\nCreating new data...")
    create_new_data()
    print("\nCompleted database refresh with balanced relationships") 