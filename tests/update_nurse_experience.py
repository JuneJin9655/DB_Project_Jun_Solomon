from app import create_app, db
from app.models import Nurse, ClinicPersonnel
import random

def update_nurse_experience():
    """Update Years of Experience and Grade fields for all nurses"""
    app = create_app()
    with app.app_context():
        nurses = Nurse.query.all()
        
        print(f"Found {len(nurses)} nurses")
        
        # Define possible grades
        grades = ["Junior", "Intermediate", "Senior", "Lead", "Chief"]
        
        # Check current experience and grades
        for nurse in nurses:
            print(f"Nurse {nurse.EmpID} ({nurse.personnel.Name if nurse.personnel else 'Unknown'}):")
            print(f"  - Current experience: {nurse.YearsOfExperience if nurse.YearsOfExperience is not None else 'None'} years")
            print(f"  - Current grade: {nurse.Grade or 'None'}")
        
        # Update experience and grade for each nurse
        updates_made = 0
        for nurse in nurses:
            # Determine years of experience (2-25 years)
            years_experience = random.randint(2, 25)
            
            # Determine grade based on experience
            if years_experience < 5:
                grade = "Junior"
            elif years_experience < 10:
                grade = "Intermediate"
            elif years_experience < 15:
                grade = "Senior"
            elif years_experience < 20:
                grade = "Lead"
            else:
                grade = "Chief"
            
            # Update the nurse's fields
            try:
                nurse.YearsOfExperience = years_experience
                nurse.Grade = grade
                db.session.commit()
                updates_made += 1
                print(f"\nUpdated Nurse {nurse.EmpID} ({nurse.personnel.Name if nurse.personnel else 'Unknown'}):")
                print(f"  - New experience: {years_experience} years")
                print(f"  - New grade: {grade}")
            except Exception as e:
                db.session.rollback()
                print(f"Error updating nurse {nurse.EmpID}: {e}")
        
        print(f"\nSuccessfully updated experience and grade for {updates_made} nurses")

if __name__ == "__main__":
    update_nurse_experience() 