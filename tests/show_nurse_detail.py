from app import create_app, db
from app.models import Nurse, SurgerySkill, NurseSkill, SurgeryType, ClinicPersonnel, Inpatient, Bed

def show_nurse_detail():
    """Show detailed information about each nurse in the database"""
    app = create_app()
    with app.app_context():
        nurses = Nurse.query.all()
        
        print(f"=== DETAILED NURSE DATA ({len(nurses)} nurses) ===\n")
        
        for nurse in nurses:
            # Get personnel data
            personnel = ClinicPersonnel.query.get(nurse.EmpID)
            
            # Get surgery type data
            surgery_type = None
            if nurse.SurgeryTypeCode:
                surgery_type = SurgeryType.query.get(nurse.SurgeryTypeCode)
            
            # Get nurse skills
            nurse_skills = NurseSkill.query.filter_by(EmpID=nurse.EmpID).all()
            skill_details = []
            for ns in nurse_skills:
                skill = SurgerySkill.query.get(ns.SkillCode)
                if skill:
                    skill_details.append(f"{skill.SkillCode}: {skill.Description}")
            
            # Get inpatients assigned to this nurse
            inpatients = Inpatient.query.filter_by(EmpID=nurse.EmpID).all()
            
            # Print nurse details
            print(f"NURSE ID: {nurse.EmpID}")
            print(f"NAME: {personnel.Name if personnel else 'Unknown'}")
            print(f"SPECIALTY: {personnel.Specialty if hasattr(personnel, 'Specialty') else 'N/A'}")
            print(f"CONTACT INFO: {personnel.ContactInfo if hasattr(personnel, 'ContactInfo') else 'N/A'}")
            print(f"YEARS EXPERIENCE: {nurse.YearsOfExperience}")
            print(f"GRADE: {nurse.Grade}")
            print(f"NURSING UNITS: {nurse.NursingUnits}")
            print(f"SURGERY TYPE: {surgery_type.Name if surgery_type else 'None'} ({nurse.SurgeryTypeCode or 'None'})")
            
            print(f"\nSKILLS ({len(nurse_skills)}):")
            for skill in skill_details:
                print(f"  - {skill}")
            
            print(f"\nASSIGNED INPATIENTS ({len(inpatients)}):")
            for inpatient in inpatients:
                print(f"  - Patient ID: {inpatient.PatientID}, Room: {inpatient.PatientRoomID}, Bed Label: {inpatient.BedLabel}")
            
            print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    show_nurse_detail() 