from app import create_app, db
from app.models import Patient, Gender, HeartRisk
from datetime import datetime
import random

def insert_patient_data():
    """Insert sample patient data into the database"""
    app = create_app()
    with app.app_context():
        # Check for existing patients
        existing_patients = Patient.query.count()
        if existing_patients > 0:
            print(f"Found {existing_patients} existing patients in the database.")
            return
        
        # Check for physicians
        from app.models import Physician
        physicians = Physician.query.filter_by(IsActive=True).all()
        if not physicians:
            print("No active physicians found. Please add physicians first.")
            return
        
        patients_data = [
            {
                'PatientID': 2001,
                'SSN': 'SSN-2001',
                'Name': 'Alice Johnson',
                'Gender': Gender.FEMALE,
                'Phone': '555-1001',
                'DOB': datetime(1985, 3, 15),
                'Address': '123 Main St, Newark, NJ',
                'BloodType': 'A+',
                'HDL': 65,
                'LDL': 110,
                'Triglyceride': 120,
                'IsInpatient': False,
                'IsEmployee': False,
                'HeartRiskLevel': HeartRisk.LOW
            },
            {
                'PatientID': 2002,
                'SSN': 'SSN-2002',
                'Name': 'Bob Williams',
                'Gender': Gender.MALE,
                'Phone': '555-1002',
                'DOB': datetime(1978, 7, 22),
                'Address': '456 Oak Ave, Newark, NJ',
                'BloodType': 'O-',
                'HDL': 45,
                'LDL': 145,
                'Triglyceride': 180,
                'IsInpatient': True,
                'IsEmployee': False,
                'HeartRiskLevel': HeartRisk.MODERATE
            },
            {
                'PatientID': 2003,
                'SSN': 'SSN-2003',
                'Name': 'Carol Davis',
                'Gender': Gender.FEMALE,
                'Phone': '555-1003',
                'DOB': datetime(1992, 5, 8),
                'Address': '789 Pine St, Newark, NJ',
                'BloodType': 'B+',
                'HDL': 70,
                'LDL': 90,
                'Triglyceride': 100,
                'IsInpatient': False,
                'IsEmployee': True,
                'HeartRiskLevel': HeartRisk.NONE
            },
            {
                'PatientID': 2004,
                'SSN': 'SSN-2004',
                'Name': 'David Brown',
                'Gender': Gender.MALE,
                'Phone': '555-1004',
                'DOB': datetime(1965, 11, 30),
                'Address': '101 Cedar Rd, Newark, NJ',
                'BloodType': 'AB+',
                'HDL': 35,
                'LDL': 160,
                'Triglyceride': 220,
                'IsInpatient': True,
                'IsEmployee': False,
                'HeartRiskLevel': HeartRisk.HIGH
            },
            {
                'PatientID': 2005,
                'SSN': 'SSN-2005',
                'Name': 'Eva Miller',
                'Gender': Gender.FEMALE,
                'Phone': '555-1005',
                'DOB': datetime(1988, 9, 17),
                'Address': '202 Maple Dr, Newark, NJ',
                'BloodType': 'A-',
                'HDL': 55,
                'LDL': 120,
                'Triglyceride': 140,
                'IsInpatient': False,
                'IsEmployee': False,
                'HeartRiskLevel': HeartRisk.LOW
            },
            {
                'PatientID': 2006,
                'SSN': 'SSN-2006',
                'Name': 'Frank Taylor',
                'Gender': Gender.MALE,
                'Phone': '555-1006',
                'DOB': datetime(1972, 4, 5),
                'Address': '303 Elm St, Newark, NJ',
                'BloodType': 'O+',
                'HDL': 50,
                'LDL': 130,
                'Triglyceride': 150,
                'IsInpatient': True,
                'IsEmployee': False,
                'HeartRiskLevel': HeartRisk.MODERATE
            },
            {
                'PatientID': 2007,
                'SSN': 'SSN-2007',
                'Name': 'Grace Wilson',
                'Gender': Gender.FEMALE,
                'Phone': '555-1007',
                'DOB': datetime(1995, 8, 12),
                'Address': '404 Birch Ave, Newark, NJ',
                'BloodType': 'B-',
                'HDL': 60,
                'LDL': 100,
                'Triglyceride': 110,
                'IsInpatient': False,
                'IsEmployee': True,
                'HeartRiskLevel': HeartRisk.NONE
            },
            {
                'PatientID': 2008,
                'SSN': 'SSN-2008',
                'Name': 'Henry Moore',
                'Gender': Gender.MALE,
                'Phone': '555-1008',
                'DOB': datetime(1960, 2, 28),
                'Address': '505 Walnut Rd, Newark, NJ',
                'BloodType': 'AB-',
                'HDL': 40,
                'LDL': 150,
                'Triglyceride': 200,
                'IsInpatient': True,
                'IsEmployee': False,
                'HeartRiskLevel': HeartRisk.HIGH
            }
        ]
        
        # Distribute patients among physicians
        for patient_data in patients_data:
            # Set primary physician
            physician = random.choice(physicians)
            patient_data['PrimaryPhysicianID'] = physician.EmpID
            
            # Set EmpID if this patient is an employee
            if patient_data['IsEmployee']:
                from app.models import ClinicPersonnel
                employees = ClinicPersonnel.query.all()
                if employees:
                    employee = random.choice(employees)
                    patient_data['EmpID'] = employee.EmpID
            
            # Create patient with validation bypass
            patient = Patient(**patient_data)
            patient._skip_illness_check = True  # Bypass illness validation
            
            db.session.add(patient)
        
        try:
            db.session.commit()
            print(f"Successfully added {len(patients_data)} patients.")
        except Exception as e:
            db.session.rollback()
            print(f"Error adding patients: {e}")

if __name__ == "__main__":
    insert_patient_data() 