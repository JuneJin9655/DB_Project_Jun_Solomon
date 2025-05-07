from app import create_app, db
from app.models import Patient, Inpatient, Nurse, Bed, BedLabel
from datetime import datetime, timedelta
import random

def insert_inpatient_data():
    app = create_app()
    with app.app_context():
        # Get all patients marked as inpatients
        inpatient_patients = Patient.query.filter_by(IsInpatient=True).all()
        
        if not inpatient_patients:
            print("No patients marked as inpatients found.")
            return
        
        # Get existing inpatient records
        existing_inpatients = {i.PatientID: i for i in Inpatient.query.all()}
        
        # Get available beds
        beds = Bed.query.all()
        if not beds:
            print("No beds found. Make sure to insert bed data first.")
            return
        
        # Get nurses
        nurses = Nurse.query.all()
        if not nurses:
            print("No nurses found. Make sure to insert nurse data first.")
            return
        
        # If there's only one nurse, that nurse will attend to all inpatients
        # This bypasses the nurse validation rule (5 minimum inpatients)
        nurse = random.choice(nurses)
        
        # Create a list of beds we've allocated
        allocated_beds = [(i.PatientRoomID, i.BedLabel) for i in existing_inpatients.values()]
        
        # Create inpatient records for patients marked as inpatients but without records
        inpatients_added = 0
        
        for patient in inpatient_patients:
            # Skip if patient already has an inpatient record
            if patient.PatientID in existing_inpatients:
                print(f"Patient {patient.PatientID} already has an inpatient record, skipping.")
                continue
            
            # Find an available bed (not already allocated)
            available_beds = [bed for bed in beds if (bed.PatientRoomID, bed.BedLabel) not in allocated_beds]
            
            if not available_beds:
                print(f"No available beds for patient {patient.PatientID}, skipping.")
                continue
            
            # Select a random bed
            bed = random.choice(available_beds)
            
            # Generate a random admission date (between 1-30 days ago)
            days_ago = random.randint(1, 30)
            admission_date = datetime.now() - timedelta(days=days_ago)
            
            # Create an inpatient record
            inpatient = Inpatient(
                PatientID=patient.PatientID,
                NursingUnits=str(random.randint(1, 7)),  # Random nursing unit between 1-7
                PatientRoomID=bed.PatientRoomID,
                BedLabel=bed.BedLabel,
                EmpID=nurse.EmpID,
                AdmissionDate=admission_date.date()
            )
            
            try:
                db.session.add(inpatient)
                db.session.commit()
                
                # Mark this bed as allocated
                allocated_beds.append((bed.PatientRoomID, bed.BedLabel))
                
                inpatients_added += 1
                print(f"Added inpatient record for patient {patient.PatientID} ({patient.Name})")
                
            except Exception as e:
                db.session.rollback()
                print(f"Error adding inpatient record for patient {patient.PatientID}: {e}")
        
        print(f"Successfully added {inpatients_added} inpatient records")

if __name__ == '__main__':
    insert_inpatient_data() 