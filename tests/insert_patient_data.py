from app import create_app, db
from app.models import Patient, Illness, Physician, Gender, Allergy
from datetime import datetime, timedelta
from sqlalchemy import text
import random

def insert_patient_data():
    app = create_app()
    with app.app_context():
        # Get existing data we'll need
        physicians = Physician.query.all()
        illnesses = Illness.query.all()
        allergies = Allergy.query.all()
        
        if not physicians:
            print("No physicians found. Make sure to insert physician data first.")
            return
            
        if not illnesses:
            print("No illnesses found. Make sure to insert illness data first.")
            return
        
        # Get the max patient ID
        patient_id_start = db.session.query(db.func.max(Patient.PatientID)).scalar()
        if patient_id_start is None:
            patient_id_start = 2000
        
        # Patient data
        patients_data = [
            {
                'Name': 'Emily Johnson',
                'Gender': Gender.FEMALE,
                'Phone': '555-0301',
                'DOB': datetime(1985, 3, 15),
                'Address': '123 Cedar Lane, Newark, NJ',
                'BloodType': 'O+',
                'HDL': 55,
                'LDL': 90,
                'Triglyceride': 120,
                'IsInpatient': False
            },
            {
                'Name': 'James Wilson',
                'Gender': Gender.MALE,
                'Phone': '555-0302',
                'DOB': datetime(1976, 7, 22),
                'Address': '456 Birch Street, Newark, NJ',
                'BloodType': 'B-',
                'HDL': 45,
                'LDL': 110,
                'Triglyceride': 140,
                'IsInpatient': False
            },
            {
                'Name': 'Sophia Martinez',
                'Gender': Gender.FEMALE,
                'Phone': '555-0303',
                'DOB': datetime(1990, 11, 8),
                'Address': '789 Elm Road, Newark, NJ',
                'BloodType': 'AB+',
                'HDL': 60,
                'LDL': 80,
                'Triglyceride': 100,
                'IsInpatient': False
            },
            {
                'Name': 'Michael Brown',
                'Gender': Gender.MALE,
                'Phone': '555-0304',
                'DOB': datetime(1982, 4, 30),
                'Address': '321 Oak Avenue, Newark, NJ',
                'BloodType': 'A-',
                'HDL': 50,
                'LDL': 95,
                'Triglyceride': 130,
                'IsInpatient': True
            },
            {
                'Name': 'Olivia Davis',
                'Gender': Gender.FEMALE,
                'Phone': '555-0305',
                'DOB': datetime(1995, 8, 12),
                'Address': '654 Pine Blvd, Newark, NJ',
                'BloodType': 'O-',
                'HDL': 65,
                'LDL': 75,
                'Triglyceride': 90,
                'IsInpatient': False
            },
            {
                'Name': 'William Taylor',
                'Gender': Gender.MALE,
                'Phone': '555-0306',
                'DOB': datetime(1972, 2, 25),
                'Address': '987 Maple Court, Newark, NJ',
                'BloodType': 'B+',
                'HDL': 40,
                'LDL': 120,
                'Triglyceride': 160,
                'IsInpatient': True
            },
            {
                'Name': 'Emma Garcia',
                'Gender': Gender.FEMALE,
                'Phone': '555-0307',
                'DOB': datetime(1988, 9, 17),
                'Address': '741 Spruce Lane, Newark, NJ',
                'BloodType': 'AB-',
                'HDL': 55,
                'LDL': 85,
                'Triglyceride': 110,
                'IsInpatient': False
            },
            {
                'Name': 'Alexander Rodriguez',
                'Gender': Gender.MALE,
                'Phone': '555-0308',
                'DOB': datetime(1979, 5, 3),
                'Address': '852 Willow Drive, Newark, NJ',
                'BloodType': 'A+',
                'HDL': 48,
                'LDL': 105,
                'Triglyceride': 135,
                'IsInpatient': False
            },
            {
                'Name': 'Ava Lopez',
                'Gender': Gender.FEMALE,
                'Phone': '555-0309',
                'DOB': datetime(1993, 12, 1),
                'Address': '369 Aspen Circle, Newark, NJ',
                'BloodType': 'O+',
                'HDL': 62,
                'LDL': 78,
                'Triglyceride': 95,
                'IsInpatient': False
            },
            {
                'Name': 'Daniel Lee',
                'Gender': Gender.MALE,
                'Phone': '555-0310',
                'DOB': datetime(1984, 6, 10),
                'Address': '456 Fir Street, Newark, NJ',
                'BloodType': 'B+',
                'HDL': 52,
                'LDL': 92,
                'Triglyceride': 125,
                'IsInpatient': True
            }
        ]
        
        patients_added = 0
        ssn_base = 100000000  # Start of SSN range
        
        print("Adding patient data...")
        
        for i, patient_data in enumerate(patients_data):
            patient_id = patient_id_start + i + 1
            
            # Generate a unique SSN
            ssn = f"PAT{ssn_base + patient_id}"
            
            # Select a random physician as primary physician
            physician = random.choice(physicians)
            
            # Select a random allergy (or None)
            allergy = random.choice([None] + allergies) if allergies else None
            
            try:
                # Create a new patient with validation bypass flag
                patient = Patient(
                    PatientID=patient_id,
                    SSN=ssn,
                    PrimaryPhysicianID=physician.EmpID,
                    AllergyCode=allergy.AllergyCode if allergy else None,
                    **patient_data
                )
                
                # Set flag to bypass illness validation
                patient._skip_illness_check = True
                db.session.add(patient)
                db.session.commit()
                
                # Now add a diagnosis (illness) for this patient
                # Select 1-3 random illnesses
                num_illnesses = random.randint(1, 3)
                for _ in range(num_illnesses):
                    illness = random.choice(illnesses)
                    
                    # Create a diagnosis
                    # Use a date within the last year
                    days_ago = random.randint(1, 365)
                    diagnosis_date = datetime.now() - timedelta(days=days_ago)
                    
                    # Build the SQL query with proper text() wrapper
                    sql_query = text(f"""
                    INSERT INTO Diagnosis (PatientID, EmpID, ConsultationDate, IllnessCode, AllergyCode)
                    VALUES ({patient_id}, {physician.EmpID}, '{diagnosis_date.date()}', '{illness.IllnessCode}', 
                            {'NULL' if not patient.AllergyCode else "'" + patient.AllergyCode + "'"})
                    """)
                    
                    # Execute the raw SQL query to avoid relationship validation issues
                    db.session.execute(sql_query)
                
                db.session.commit()
                patients_added += 1
                print(f"Added patient {patient_id}: {patient_data['Name']}")
                
            except Exception as e:
                db.session.rollback()
                print(f"Error adding patient {patient_data['Name']}: {e}")
                
        print(f"Successfully added {patients_added} patients")

if __name__ == '__main__':
    insert_patient_data() 