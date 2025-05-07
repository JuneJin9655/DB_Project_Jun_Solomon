from app import create_app, db
from app.models import Nurse, SurgerySkill, NurseSkill, SurgeryType

def check_data():
    """Check the current state of data related to nurse skills"""
    app = create_app()
    with app.app_context():
        # Get counts
        nurses = Nurse.query.all()
        skills = SurgerySkill.query.all()
        nurse_skills = NurseSkill.query.all()
        surgery_types = SurgeryType.query.all()
        
        print(f"Total Nurses: {len(nurses)}")
        print(f"Total Surgery Skills: {len(skills)}")
        print(f"Total Nurse Skills: {len(nurse_skills)}")
        print(f"Total Surgery Types: {len(surgery_types)}")
        
        # Check how many nurses have skills
        nurses_with_skills = {}
        for nurse in nurses:
            skill_count = NurseSkill.query.filter_by(EmpID=nurse.EmpID).count()
            nurses_with_skills[nurse.EmpID] = skill_count
        
        nurses_without_skills = [n.EmpID for n in nurses if nurses_with_skills.get(n.EmpID, 0) == 0]
        print(f"\nNurses without any skills: {len(nurses_without_skills)}")
        
        if nurses_without_skills:
            print("Nurse IDs without skills:")
            for emp_id in nurses_without_skills:
                nurse = Nurse.query.get(emp_id)
                print(f"  - Nurse ID {emp_id}: {nurse.personnel.Name if nurse.personnel else 'Unknown'}")
        
        # Print skill distribution
        print("\nSkill distribution among nurses:")
        for emp_id, count in nurses_with_skills.items():
            if count > 0:
                nurse = Nurse.query.get(emp_id)
                print(f"  - Nurse ID {emp_id} ({nurse.personnel.Name if nurse.personnel else 'Unknown'}): {count} skills")

if __name__ == "__main__":
    check_data() 