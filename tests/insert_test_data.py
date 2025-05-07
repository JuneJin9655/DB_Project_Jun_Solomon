from datetime import datetime, timedelta
from app import create_app, db
from app.models import (
    ClinicPersonnel, Physician, Nurse, Surgeon,
    Patient, Inpatient, SurgeryType, SurgerySkill,
    SurgerySchedule, Bed, Gender, SurgeryCategory,
    Wing, BedLabel, Clinic, Illness, Diagnosis
)
from sqlalchemy.exc import IntegrityError

def insert_test_data():
    app = create_app()
    with app.app_context():
        # Check if the clinic already exists
        existing_clinic = db.session.query(Clinic).filter_by(ClinicID=1).first()
        if not existing_clinic:
            # Create clinic first
            clinic = Clinic(
                ClinicID=1,
                ClinicName='Newark Medical Associates',
                Address='100 Main Street, Newark, NJ'
            )
            db.session.add(clinic)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                print("Clinic already exists, continuing with other data...")

        # Check if personnel already exist
        personnel_data = [
            {
                'EmpID': 1001,
                'Name': 'Dr. John Smith',
                'Address': '123 Oak Street, Newark',
                'Gender': Gender.MALE,
                'Phone': '555-0101',
                'Salary': 120000,
                'SSN': 'SSN001',
                'ClinicID': 1
            },
            {
                'EmpID': 1002,
                'Name': 'Sarah Johnson',
                'Address': '456 Maple Avenue, Newark',
                'Gender': Gender.FEMALE,
                'Phone': '555-0102',
                'Salary': 75000,
                'SSN': 'SSN002',
                'ClinicID': 1
            },
            {
                'EmpID': 1003,
                'Name': 'Dr. Michael Brown',
                'Address': '789 Pine Road, Newark',
                'Gender': Gender.MALE,
                'Phone': '555-0103',
                'Salary': 180000,
                'SSN': 'SSN003',
                'ClinicID': 1
            }
        ]

        for data in personnel_data:
            existing_personnel = db.session.query(ClinicPersonnel).filter_by(EmpID=data['EmpID']).first()
            if not existing_personnel:
                personnel = ClinicPersonnel(**data)
                db.session.add(personnel)
        
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            print("Some personnel already exist, continuing...")

        # Check if physician already exists
        existing_physician = db.session.query(Physician).filter_by(EmpID=1001).first()
        if not existing_physician:
            physician = Physician(
                EmpID=1001,
                Specialty='Cardiology',
                IsActive=True,
                IsChief=True,
                ClinicID=1
            )
            db.session.add(physician)

        # Check if nurse already exists
        existing_nurse = db.session.query(Nurse).filter_by(EmpID=1002).first()
        if not existing_nurse:
            nurse = Nurse(
                EmpID=1002,
                YearsOfExperience=5,
                Grade='Senior',
                NursingUnits='Cardiac Ward'
            )
            db.session.add(nurse)

        # Check if surgeon already exists
        existing_surgeon = db.session.query(Surgeon).filter_by(EmpID=1003).first()
        if not existing_surgeon:
            surgeon = Surgeon(
                EmpID=1003,
                ContractLength=24,
                ContractType='Full-time',
                Specialty='Cardiac Surgery'
            )
            db.session.add(surgeon)

        # Check if bed already exists
        existing_bed = db.session.query(Bed).filter_by(PatientRoomID=101, BedLabel=BedLabel.A).first()
        if not existing_bed:
            bed = Bed(
                PatientRoomID=101,
                BedLabel=BedLabel.A,
                RoomNum='101A',
                Unit='Cardiac Ward',
                Wing=Wing.BLUE
            )
            db.session.add(bed)

        # Check if illness already exists
        existing_illness = db.session.query(Illness).filter_by(IllnessCode='CAD001').first()
        if not existing_illness:
            illness = Illness(
                IllnessCode='CAD001',
                Description='Coronary Artery Disease'
            )
            db.session.add(illness)
        
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            print("Some records already exist, continuing...")

        # Check if patient already exists
        existing_patient = db.session.query(Patient).filter_by(PatientID=2001).first()
        existing_diagnosis = db.session.query(Diagnosis).filter_by(PatientID=2001, EmpID=1001).first()
        
        if not existing_patient and not existing_diagnosis:
            # Create patient with validation bypass flag
            patient = Patient(
                PatientID=2001,
                SSN='PAT001',
                Name='Robert Wilson',
                Gender=Gender.MALE,
                Phone='555-0201',
                DOB=datetime(1980, 1, 1),
                Address='321 Riverside Drive, Newark',
                BloodType='A+',
                HDL=50,
                LDL=100,
                Triglyceride=150,
                PrimaryPhysicianID=1001
            )
            # Set the flag to bypass illness validation
            patient._skip_illness_check = True
            db.session.add(patient)

            try:
                # Commit the patient first
                db.session.commit()
                
                # Now create diagnosis
                diagnosis = Diagnosis(
                    PatientID=2001,
                    EmpID=1001,
                    ConsultationDate=datetime.now(),
                    IllnessCode='CAD001'
                )
                db.session.add(diagnosis)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                print("Patient or diagnosis already exists, continuing...")

        # Check if inpatient already exists
        existing_inpatient = db.session.query(Inpatient).filter_by(PatientID=2001).first()
        if not existing_inpatient:
            inpatient = Inpatient(
                PatientID=2001,
                NursingUnits='3',
                PatientRoomID=101,
                BedLabel=BedLabel.A,
                EmpID=1002,
                AdmissionDate=datetime.now()
            )
            db.session.add(inpatient)

        # Check if surgery type already exists
        existing_surgery_type = db.session.query(SurgeryType).filter_by(SurgeryCode='CARD001').first()
        if not existing_surgery_type:
            surgery_type = SurgeryType(
                SurgeryCode='CARD001',
                Name='Coronary Artery Bypass Surgery',
                Category=SurgeryCategory.HOSPITALIZATION,
                AnatomicalLocation='Heart',
                SpecialNeeds='Requires heart-lung machine'
            )
            db.session.add(surgery_type)

        # Check if surgery skill already exists
        existing_skill = db.session.query(SurgerySkill).filter_by(SkillCode='SKILL001').first()
        if not existing_skill:
            skill = SurgerySkill(
                SkillCode='SKILL001',
                Description='Coronary Bypass Surgery'
            )
            db.session.add(skill)
        
        try:
            db.session.commit()
            print("Test data insertion completed successfully!")
        except IntegrityError as e:
            db.session.rollback()
            print(f"Error inserting data: {e}")

if __name__ == '__main__':
    insert_test_data() 