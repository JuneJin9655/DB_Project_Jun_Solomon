from app import create_app, db
from app.models import Nurse, Inpatient, Patient
import random

def update_inpatient_nursing_units():
    """Update nursing units for inpatients, distributing them across units 1-7"""
    app = create_app()
    with app.app_context():
        # Get all inpatients and nurses
        inpatients = Inpatient.query.all()
        nurses = Nurse.query.all()
        
        print(f"Found {len(inpatients)} inpatients and {len(nurses)} nurses")
        
        # Assign nursing units (1-7) to each nurse
        nurse_units = {}
        for idx, nurse in enumerate(nurses):
            # Assign 1-2 nursing units to each nurse
            units = [str((idx*2) % 7 + 1), str((idx*2+1) % 7 + 1)]
            nurse_units[nurse.EmpID] = units
            print(f"Nurse {nurse.EmpID} ({nurse.personnel.Name}) assigned to units {', '.join(units)}")
        
        # Update nursing unit for each inpatient
        updates_made = 0
        unit_counts = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0}
        
        for inpatient in inpatients:
            if not inpatient.EmpID:
                continue
                
            # Choose a unit from those assigned to the nurse
            if inpatient.EmpID in nurse_units:
                available_units = nurse_units[inpatient.EmpID]
                unit = random.choice(available_units)
                
                try:
                    old_unit = inpatient.NursingUnits
                    inpatient.NursingUnits = unit
                    db.session.commit()
                    
                    unit_counts[unit] += 1
                    updates_made += 1
                    
                    print(f"Inpatient {inpatient.PatientID} updated from unit {old_unit} to unit {unit}")
                except Exception as e:
                    db.session.rollback()
                    print(f"Error updating inpatient {inpatient.PatientID}: {e}")
        
        print("\nNursing unit distribution after update:")
        for unit, count in unit_counts.items():
            print(f"Unit {unit}: {count} inpatients")
            
        print(f"\nSuccessfully updated nursing units for {updates_made} inpatients")
        
if __name__ == "__main__":
    update_inpatient_nursing_units() 