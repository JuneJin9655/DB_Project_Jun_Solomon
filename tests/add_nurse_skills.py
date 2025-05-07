from app import create_app, db
from app.models import Nurse, SurgerySkill, NurseSkill, SurgeryType
import random

def add_nurse_skills():
    """Add surgery skills to nurses and ensure even distribution"""
    app = create_app()
    with app.app_context():
        nurses = Nurse.query.all()
        skills = SurgerySkill.query.all()
        
        print(f"Found {len(nurses)} nurses and {len(skills)} skills")
        
        # Check existing nurse skills
        existing_nurse_skills = NurseSkill.query.all()
        if existing_nurse_skills:
            print(f"Found {len(existing_nurse_skills)} existing nurse skills")
            
            # First check if we need to add more
            if len(existing_nurse_skills) >= len(nurses) * 3:
                print("Each nurse already has a good number of skills. No need to add more.")
                return
        
        # Clear existing nurse skills first to rebuild them
        try:
            db.session.query(NurseSkill).delete()
            db.session.commit()
            print("Cleared existing nurse skills to rebuild them")
        except Exception as e:
            db.session.rollback()
            print(f"Error clearing existing nurse skills: {e}")
        
        # For each nurse, assign multiple skills based on their specialty
        skills_added = 0
        for nurse in nurses:
            # Determine how many skills to assign (3-5 per nurse)
            num_skills = random.randint(3, 5)
            print(f"\nAdding {num_skills} skills to Nurse {nurse.EmpID} ({nurse.personnel.Name if nurse.personnel else 'Unknown'})")
            
            # Filter skills relevant to nurse's specialty or assigned surgery type
            relevant_skills = []
            if nurse.SurgeryTypeCode:
                # Get skills related to the nurse's assigned surgery type
                relevant_skills = [skill for skill in skills if skill.SurgeryCode == nurse.SurgeryTypeCode]
            
            # If no relevant skills found or not enough, add skills from any category
            available_skills = relevant_skills if relevant_skills else skills
            
            # If we still need more skills, use random ones
            if len(available_skills) < num_skills:
                available_skills = skills
            
            # Randomly select skills to assign
            selected_skills = random.sample(available_skills, min(num_skills, len(available_skills)))
            
            # Add each skill to the nurse
            for skill in selected_skills:
                try:
                    nurse_skill = NurseSkill(
                        EmpID=nurse.EmpID,
                        SkillCode=skill.SkillCode
                    )
                    db.session.add(nurse_skill)
                    db.session.commit()
                    skills_added += 1
                    print(f"  - Added skill {skill.SkillCode}: {skill.Description}")
                except Exception as e:
                    db.session.rollback()
                    print(f"  - Error adding skill {skill.SkillCode}: {e}")
        
        print(f"\nSuccessfully added {skills_added} skills to {len(nurses)} nurses")
        
        # Balance surgery types by assigning nurses to surgery types
        balance_surgery_type_nurses()

def balance_surgery_type_nurses():
    """Make sure each surgery type has at least 2 nurses assigned"""
    surgery_types = SurgeryType.query.all()
    nurses = Nurse.query.all()
    
    print("\nBalancing surgery type - nurse assignments...")
    
    for surgery_type in surgery_types:
        # Check how many nurses are assigned to this surgery type
        assigned_nurses = Nurse.query.filter_by(SurgeryTypeCode=surgery_type.SurgeryCode).all()
        print(f"Surgery type {surgery_type.SurgeryCode} ({surgery_type.Name}) has {len(assigned_nurses)} nurses assigned")
        
        # If less than 2 nurses, assign more
        if len(assigned_nurses) < 2:
            needed = 2 - len(assigned_nurses)
            print(f"  - Need to assign {needed} more nurses")
            
            # Find nurses without surgery type or with fewer skills
            available_nurses = [n for n in nurses if n.SurgeryTypeCode is None or n.SurgeryTypeCode != surgery_type.SurgeryCode]
            
            # Sort by those with fewest skills first
            available_nurses.sort(key=lambda n: len(n.skills))
            
            # Assign needed nurses
            for i in range(min(needed, len(available_nurses))):
                try:
                    available_nurses[i].SurgeryTypeCode = surgery_type.SurgeryCode
                    db.session.commit()
                    print(f"  - Assigned nurse {available_nurses[i].EmpID} to surgery type {surgery_type.SurgeryCode}")
                    
                    # Also assign skills related to this surgery type to the nurse
                    skills = SurgerySkill.query.filter_by(SurgeryCode=surgery_type.SurgeryCode).all()
                    for skill in skills:
                        # Check if nurse already has this skill
                        if not NurseSkill.query.filter_by(EmpID=available_nurses[i].EmpID, SkillCode=skill.SkillCode).first():
                            nurse_skill = NurseSkill(
                                EmpID=available_nurses[i].EmpID,
                                SkillCode=skill.SkillCode
                            )
                            db.session.add(nurse_skill)
                            db.session.commit()
                            print(f"    - Added skill {skill.SkillCode} to nurse {available_nurses[i].EmpID}")
                except Exception as e:
                    db.session.rollback()
                    print(f"  - Error assigning nurse to surgery type: {e}")

if __name__ == "__main__":
    add_nurse_skills() 