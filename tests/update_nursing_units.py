from app import create_app, db
from app.models import Nurse, ClinicPersonnel
import random

def update_nursing_units():
    """Update Nursing Units field for all nurses"""
    app = create_app()
    with app.app_context():
        nurses = Nurse.query.all()
        
        print(f"Found {len(nurses)} nurses")
        
        # Define possible nursing units
        nursing_units = [
            "Emergency Department",
            "Intensive Care Unit (ICU)",
            "Cardiology",
            "Pediatrics",
            "Oncology",
            "Orthopedics",
            "Neurology",
            "Surgery",
            "Post-Anesthesia Care Unit (PACU)",
            "Labor and Delivery",
            "Neonatal Intensive Care Unit (NICU)",
            "Medical-Surgical",
            "Telemetry",
            "Geriatrics",
            "Rehabilitation"
        ]
        
        # Check current nursing units
        for nurse in nurses:
            print(f"Nurse {nurse.EmpID} ({nurse.personnel.Name if nurse.personnel else 'Unknown'}) - Current units: {nurse.NursingUnits or 'None'}")
        
        # Update nursing units for each nurse
        updates_made = 0
        for nurse in nurses:
            # Determine nursing units for this nurse based on their surgery type
            if nurse.SurgeryTypeCode:
                # Assign units based on surgery specialty
                if "CARD" in nurse.SurgeryTypeCode:
                    primary_unit = "Cardiology"
                    secondary_units = random.sample([u for u in nursing_units if u != primary_unit], 2)
                elif "ORTH" in nurse.SurgeryTypeCode:
                    primary_unit = "Orthopedics"
                    secondary_units = random.sample([u for u in nursing_units if u != primary_unit], 2)
                elif "NEUR" in nurse.SurgeryTypeCode:
                    primary_unit = "Neurology"
                    secondary_units = random.sample([u for u in nursing_units if u != primary_unit], 2)
                elif "OPHT" in nurse.SurgeryTypeCode:
                    primary_unit = "Surgery"
                    secondary_units = random.sample([u for u in nursing_units if u != primary_unit], 2)
                elif "DERM" in nurse.SurgeryTypeCode:
                    primary_unit = "Medical-Surgical"
                    secondary_units = random.sample([u for u in nursing_units if u != primary_unit], 2)
                elif "ENT" in nurse.SurgeryTypeCode:
                    primary_unit = "Surgery"
                    secondary_units = ["Post-Anesthesia Care Unit (PACU)"] + random.sample([u for u in nursing_units if u not in ["Surgery", "Post-Anesthesia Care Unit (PACU)"]], 1)
                elif "GAST" in nurse.SurgeryTypeCode:
                    primary_unit = "Surgery"
                    secondary_units = ["Medical-Surgical"] + random.sample([u for u in nursing_units if u not in ["Surgery", "Medical-Surgical"]], 1)
                elif "VASC" in nurse.SurgeryTypeCode:
                    primary_unit = "Cardiology"
                    secondary_units = ["Surgery"] + random.sample([u for u in nursing_units if u not in ["Cardiology", "Surgery"]], 1)
                else:
                    # Default case
                    primary_unit = "Surgery"
                    secondary_units = random.sample([u for u in nursing_units if u != primary_unit], 2)
                
                # Combine units with primary first
                assigned_units = [primary_unit] + secondary_units
            else:
                # For nurses without surgery specialty, assign random units
                assigned_units = random.sample(nursing_units, 3)
            
            # Join the units with commas
            units_string = ", ".join(assigned_units)
            
            # Update the nurse's NursingUnits field
            try:
                nurse.NursingUnits = units_string
                db.session.commit()
                updates_made += 1
                print(f"Updated Nurse {nurse.EmpID} ({nurse.personnel.Name if nurse.personnel else 'Unknown'}) - New units: {units_string}")
            except Exception as e:
                db.session.rollback()
                print(f"Error updating nurse {nurse.EmpID}: {e}")
        
        print(f"\nSuccessfully updated nursing units for {updates_made} nurses")

if __name__ == "__main__":
    update_nursing_units() 