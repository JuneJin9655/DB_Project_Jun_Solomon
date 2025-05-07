from app import create_app, db
from app.models import Patient, Physician, Consultation, Diagnosis, Illness
from datetime import datetime, timedelta
import random

def insert_consultation_data():
    app = create_app()
    with app.app_context():
        # Get existing data
        patients = Patient.query.all()
        physicians = Physician.query.all()
        illnesses = Illness.query.all()
        
        if not patients or not physicians or not illnesses:
            print("No patients, physicians, or illnesses found. Make sure to insert this data first.")
            return
        
        # Delete existing consultations and diagnoses (optional)
        try:
            print("Cleaning existing consultation data...")
            Consultation.query.delete()
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error clearing data: {e}")
        
        print(f"Adding consultation data for {len(patients)} patients...")
        
        # Get the max consultation ID
        consultation_id_start = db.session.query(db.func.max(Consultation.ConsultationID)).scalar()
        if consultation_id_start is None:
            consultation_id_start = 1000
        
        # Get existing diagnoses
        diagnoses = Diagnosis.query.all()
        
        # First, create consultations for existing diagnoses
        consultations_added = 0
        
        # Group diagnoses by unique (PatientID, EmpID, ConsultationDate)
        diagnosis_groups = {}
        for diagnosis in diagnoses:
            key = (diagnosis.PatientID, diagnosis.EmpID, diagnosis.ConsultationDate)
            if key not in diagnosis_groups:
                diagnosis_groups[key] = []
            diagnosis_groups[key].append(diagnosis)
            
        print(f"Found {len(diagnosis_groups)} existing diagnosis groups to create consultations for")
        
        # Create consultations for each diagnosis group
        for i, ((patient_id, emp_id, consult_date), diagnoses_list) in enumerate(diagnosis_groups.items()):
            try:
                # Create a consultation
                consultation = Consultation(
                    ConsultationID=consultation_id_start + consultations_added + 1,
                    PatientID=patient_id,
                    EmpID=emp_id,
                    ConsultationDate=consult_date
                )
                
                db.session.add(consultation)
                db.session.commit()
                consultations_added += 1
                
                # Log progress
                if i % 10 == 0:
                    print(f"Progress: {i+1}/{len(diagnosis_groups)} consultation groups processed...")
            except Exception as e:
                db.session.rollback()
                print(f"Error adding consultation for PatientID={patient_id}, EmpID={emp_id}, Date={consult_date}: {e}")
        
        print(f"Successfully added {consultations_added} consultations for existing diagnoses")
        
        # Now add more consultations with their own diagnoses
        print("Adding additional consultations...")
        
        # Generate dates from the last year up to today (avoiding future dates)
        today = datetime.now().date()
        date_range = [today - timedelta(days=x) for x in range(0, 365)]
        
        additional_consultations = 0
        additional_diagnoses = 0
        
        for i, patient in enumerate(patients):
            try:
                # Give each patient 1-3 more consultations
                num_consultations = random.randint(1, 3)
                
                for j in range(num_consultations):
                    # Create a new consultation with a date that doesn't already exist
                    attempts = 0
                    valid_date = False
                    consultation_date = None
                    physician = None
                    
                    while not valid_date and attempts < 10:
                        consultation_date = random.choice(date_range)
                        physician = random.choice(physicians)
                        key = (patient.PatientID, physician.EmpID, consultation_date)
                        
                        # Make sure this isn't a duplicate of an existing consultation
                        if key not in diagnosis_groups:
                            valid_date = True
                        else:
                            attempts += 1
                    
                    if not valid_date:
                        print(f"Couldn't find a non-duplicate date for patient {patient.PatientID} after 10 attempts, skipping")
                        continue
                    
                    # Create the consultation
                    consultation = Consultation(
                        ConsultationID=consultation_id_start + consultations_added + additional_consultations + 1,
                        PatientID=patient.PatientID,
                        EmpID=physician.EmpID,
                        ConsultationDate=consultation_date
                    )
                    
                    db.session.add(consultation)
                    db.session.commit()
                    additional_consultations += 1
                    
                    # Add 1-2 diagnoses for each consultation
                    num_diagnoses = random.randint(1, 2)
                    for _ in range(num_diagnoses):
                        # Pick a random illness
                        illness = random.choice(illnesses)
                        
                        try:
                            # Create a diagnosis
                            diagnosis = Diagnosis(
                                PatientID=patient.PatientID,
                                EmpID=physician.EmpID,
                                ConsultationDate=consultation_date,
                                IllnessCode=illness.IllnessCode,
                                AllergyCode=patient.AllergyCode  # Use patient's allergy if any
                            )
                            
                            db.session.add(diagnosis)
                            db.session.commit()
                            additional_diagnoses += 1
                        except Exception as e:
                            db.session.rollback()
                            print(f"Error adding diagnosis for consultation: {e}")
                    
                    # Add this to our tracking dictionary to avoid duplicates in future iterations
                    diagnosis_groups[key] = []
                
                # Log progress
                if (i + 1) % 5 == 0:
                    print(f"Progress: {i+1}/{len(patients)} patients processed for additional consultations...")
            
            except Exception as e:
                db.session.rollback()
                print(f"Error processing patient {patient.PatientID}: {e}")
        
        print(f"Successfully added {additional_consultations} additional consultations with {additional_diagnoses} diagnoses")
        print(f"Total consultations added: {consultations_added + additional_consultations}")

if __name__ == '__main__':
    insert_consultation_data() 