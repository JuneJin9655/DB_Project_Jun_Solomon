from app import create_app, db
from app.models import ClinicPersonnel, Physician, Nurse, Surgeon, Gender, SurgeryType
import random

def insert_personnel_data():
    app = create_app()
    with app.app_context():
        # Check if there are surgery types for nurses to be assigned to
        surgery_types = SurgeryType.query.all()
        if not surgery_types:
            print("No surgery types found. Some nurses may not be assigned to surgery types.")
        
        # Get the max employee ID
        emp_id_start = db.session.query(db.func.max(ClinicPersonnel.EmpID)).scalar()
        if emp_id_start is None:
            emp_id_start = 1000
        
        # Physicians data
        physicians_data = [
            {
                'Name': 'Dr. Emily Chen',
                'Gender': Gender.FEMALE,
                'Address': '123 Maple Street, Newark, NJ',
                'Phone': '555-1101',
                'Salary': 145000,
                'SSN': 'PHY001',
                'Specialty': 'Neurology',
                'IsActive': True,
                'IsChief': False
            },
            {
                'Name': 'Dr. Marcus Rodriguez',
                'Gender': Gender.MALE,
                'Address': '456 Oak Avenue, Newark, NJ',
                'Phone': '555-1102',
                'Salary': 160000,
                'SSN': 'PHY002',
                'Specialty': 'Pediatrics',
                'IsActive': True,
                'IsChief': False
            },
            {
                'Name': 'Dr. Sarah Kim',
                'Gender': Gender.FEMALE,
                'Address': '789 Pine Road, Newark, NJ',
                'Phone': '555-1103',
                'Salary': 175000,
                'SSN': 'PHY003',
                'Specialty': 'Oncology',
                'IsActive': True,
                'IsChief': False
            },
            {
                'Name': 'Dr. Raj Patel',
                'Gender': Gender.MALE,
                'Address': '101 Cedar Lane, Newark, NJ',
                'Phone': '555-1104',
                'Salary': 155000,
                'SSN': 'PHY004',
                'Specialty': 'Endocrinology',
                'IsActive': True,
                'IsChief': False
            }
        ]
        
        # Nurses data
        nurses_data = [
            {
                'Name': 'Nina Thompson',
                'Gender': Gender.FEMALE,
                'Address': '222 Elm Street, Newark, NJ',
                'Phone': '555-2201',
                'Salary': 75000,
                'SSN': 'NRS001',
                'YearsOfExperience': 8,
                'Grade': 'Senior',
                'NursingUnits': 'Intensive Care'
            },
            {
                'Name': 'James Wilson',
                'Gender': Gender.MALE,
                'Address': '333 Willow Drive, Newark, NJ',
                'Phone': '555-2202',
                'Salary': 68000,
                'SSN': 'NRS002',
                'YearsOfExperience': 5,
                'Grade': 'Mid-level',
                'NursingUnits': 'Emergency'
            },
            {
                'Name': 'Sophia Martinez',
                'Gender': Gender.FEMALE,
                'Address': '444 Birch Boulevard, Newark, NJ',
                'Phone': '555-2203',
                'Salary': 72000,
                'SSN': 'NRS003',
                'YearsOfExperience': 7,
                'Grade': 'Senior',
                'NursingUnits': 'Pediatric'
            },
            {
                'Name': 'Michael Taylor',
                'Gender': Gender.MALE,
                'Address': '555 Spruce Court, Newark, NJ',
                'Phone': '555-2204',
                'Salary': 70000,
                'SSN': 'NRS004',
                'YearsOfExperience': 6,
                'Grade': 'Mid-level',
                'NursingUnits': 'Surgical'
            }
        ]
        
        # Surgeons data
        surgeons_data = [
            {
                'Name': 'Dr. Olivia Johnson',
                'Gender': Gender.FEMALE,
                'Address': '666 Redwood Lane, Newark, NJ',
                'Phone': '555-3301',
                'Salary': 200000,
                'SSN': 'SRG001',
                'ContractLength': 36,
                'ContractType': 'Full-time',
                'Specialty': 'Neurosurgery'
            },
            {
                'Name': 'Dr. William Brown',
                'Gender': Gender.MALE,
                'Address': '777 Aspen Way, Newark, NJ',
                'Phone': '555-3302',
                'Salary': 220000,
                'SSN': 'SRG002',
                'ContractLength': 24,
                'ContractType': 'Full-time',
                'Specialty': 'Orthopedic Surgery'
            },
            {
                'Name': 'Dr. Emma Davis',
                'Gender': Gender.FEMALE,
                'Address': '888 Sequoia Circle, Newark, NJ',
                'Phone': '555-3303',
                'Salary': 210000,
                'SSN': 'SRG003',
                'ContractLength': 36,
                'ContractType': 'Full-time',
                'Specialty': 'Cardiothoracic Surgery'
            },
            {
                'Name': 'Dr. David Wilson',
                'Gender': Gender.MALE,
                'Address': '999 Fir Street, Newark, NJ',
                'Phone': '555-3304',
                'Salary': 230000,
                'SSN': 'SRG004',
                'ContractLength': 24,
                'ContractType': 'Full-time',
                'Specialty': 'General Surgery'
            }
        ]
        
        physicians_added = 0
        nurses_added = 0
        surgeons_added = 0
        
        clinic_id = 1  # Assuming this is the main clinic
        
        # Add physicians
        for i, physician_data in enumerate(physicians_data):
            try:
                # Check if SSN already exists
                existing_personnel = ClinicPersonnel.query.filter_by(SSN=physician_data['SSN']).first()
                if existing_personnel:
                    print(f"Personnel with SSN {physician_data['SSN']} already exists, skipping...")
                    continue
                
                emp_id = emp_id_start + i + 1
                
                # First create the base personnel record
                personnel = ClinicPersonnel(
                    EmpID=emp_id,
                    Name=physician_data['Name'],
                    Address=physician_data['Address'],
                    Gender=physician_data['Gender'],
                    Phone=physician_data['Phone'],
                    Salary=physician_data['Salary'],
                    SSN=physician_data['SSN'],
                    ClinicID=clinic_id
                )
                
                db.session.add(personnel)
                db.session.flush()  # Flush to get the EmpID
                
                # Then create the physician record
                physician = Physician(
                    EmpID=emp_id,
                    Specialty=physician_data['Specialty'],
                    IsActive=physician_data['IsActive'],
                    IsChief=physician_data['IsChief'],
                    ClinicID=clinic_id
                )
                
                db.session.add(physician)
                db.session.commit()
                
                physicians_added += 1
                print(f"Added physician: {physician_data['Name']}, ID: {emp_id}")
                
            except Exception as e:
                db.session.rollback()
                print(f"Error adding physician {physician_data['Name']}: {e}")
        
        # Update the starting ID for nurses
        emp_id_start = db.session.query(db.func.max(ClinicPersonnel.EmpID)).scalar()
        
        # Add nurses
        for i, nurse_data in enumerate(nurses_data):
            try:
                # Check if SSN already exists
                existing_personnel = ClinicPersonnel.query.filter_by(SSN=nurse_data['SSN']).first()
                if existing_personnel:
                    print(f"Personnel with SSN {nurse_data['SSN']} already exists, skipping...")
                    continue
                
                emp_id = emp_id_start + i + 1
                
                # First create the base personnel record
                personnel = ClinicPersonnel(
                    EmpID=emp_id,
                    Name=nurse_data['Name'],
                    Address=nurse_data['Address'],
                    Gender=nurse_data['Gender'],
                    Phone=nurse_data['Phone'],
                    Salary=nurse_data['Salary'],
                    SSN=nurse_data['SSN'],
                    ClinicID=clinic_id
                )
                
                db.session.add(personnel)
                db.session.flush()  # Flush to get the EmpID
                
                # Assign a surgery type if available
                surgery_type_code = None
                if surgery_types:
                    surgery_type = random.choice(surgery_types)
                    surgery_type_code = surgery_type.SurgeryCode
                
                # Then create the nurse record
                nurse = Nurse(
                    EmpID=emp_id,
                    YearsOfExperience=nurse_data['YearsOfExperience'],
                    Grade=nurse_data['Grade'],
                    NursingUnits=nurse_data['NursingUnits'],
                    SurgeryTypeCode=surgery_type_code
                )
                
                db.session.add(nurse)
                db.session.commit()
                
                nurses_added += 1
                print(f"Added nurse: {nurse_data['Name']}, ID: {emp_id}")
                
            except Exception as e:
                db.session.rollback()
                print(f"Error adding nurse {nurse_data['Name']}: {e}")
        
        # Update the starting ID for surgeons
        emp_id_start = db.session.query(db.func.max(ClinicPersonnel.EmpID)).scalar()
        
        # Add surgeons
        for i, surgeon_data in enumerate(surgeons_data):
            try:
                # Check if SSN already exists
                existing_personnel = ClinicPersonnel.query.filter_by(SSN=surgeon_data['SSN']).first()
                if existing_personnel:
                    print(f"Personnel with SSN {surgeon_data['SSN']} already exists, skipping...")
                    continue
                
                emp_id = emp_id_start + i + 1
                
                # First create the base personnel record
                personnel = ClinicPersonnel(
                    EmpID=emp_id,
                    Name=surgeon_data['Name'],
                    Address=surgeon_data['Address'],
                    Gender=surgeon_data['Gender'],
                    Phone=surgeon_data['Phone'],
                    Salary=surgeon_data['Salary'],
                    SSN=surgeon_data['SSN'],
                    ClinicID=clinic_id
                )
                
                db.session.add(personnel)
                db.session.flush()  # Flush to get the EmpID
                
                # Then create the surgeon record
                surgeon = Surgeon(
                    EmpID=emp_id,
                    ContractLength=surgeon_data['ContractLength'],
                    ContractType=surgeon_data['ContractType'],
                    Specialty=surgeon_data['Specialty']
                )
                
                db.session.add(surgeon)
                db.session.commit()
                
                surgeons_added += 1
                print(f"Added surgeon: {surgeon_data['Name']}, ID: {emp_id}")
                
            except Exception as e:
                db.session.rollback()
                print(f"Error adding surgeon {surgeon_data['Name']}: {e}")
        
        print(f"\nSummary:")
        print(f"Added {physicians_added} physicians")
        print(f"Added {nurses_added} nurses")
        print(f"Added {surgeons_added} surgeons")
        print(f"Total personnel added: {physicians_added + nurses_added + surgeons_added}")

if __name__ == '__main__':
    insert_personnel_data() 