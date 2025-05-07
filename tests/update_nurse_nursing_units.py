from app import create_app, db
from app.models import Nurse, ClinicPersonnel
import random

def update_nurse_nursing_units():
    """Update nursing units for nurses with numeric values 1-7"""
    app = create_app()
    with app.app_context():
        nurses = Nurse.query.all()
        
        print(f"Found {len(nurses)} nurses")
        
        # Print current nursing units
        for nurse in nurses:
            print(f"Nurse {nurse.EmpID} ({nurse.personnel.Name}) - Current units: {nurse.NursingUnits}")
        
        # Update nursing units for each nurse
        updates_made = 0
        nursing_unit_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}
        
        for idx, nurse in enumerate(nurses):
            # Each nurse is assigned two numeric units (1-7)
            # Distribute evenly but with some randomness
            unit1 = (idx % 7) + 1
            unit2 = ((idx + 3) % 7) + 1
            
            # Ensure two different units
            if unit1 == unit2:
                unit2 = (unit2 % 7) + 1
                
            # Assign both units as a comma-separated string
            units_str = f"{unit1},{unit2}"
            
            try:
                old_units = nurse.NursingUnits
                nurse.NursingUnits = units_str
                db.session.commit()
                
                nursing_unit_counts[unit1] += 1
                nursing_unit_counts[unit2] += 1
                updates_made += 1
                
                print(f"Nurse {nurse.EmpID} ({nurse.personnel.Name}) updated from {old_units} to {units_str}")
            except Exception as e:
                db.session.rollback()
                print(f"Error updating nurse {nurse.EmpID}: {e}")
        
        print("\nNursing unit distribution after update:")
        for unit, count in nursing_unit_counts.items():
            print(f"Unit {unit}: {count} nurses")
            
        print(f"\nSuccessfully updated nursing units for {updates_made} nurses")
        
if __name__ == "__main__":
    update_nurse_nursing_units() 