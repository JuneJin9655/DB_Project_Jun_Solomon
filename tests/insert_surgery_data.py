from app import create_app, db
from app.models import SurgeryType, SurgerySkill, Surgeon, Patient, SurgerySchedule, OperatingRoom, SurgeryCategory
from datetime import datetime, timedelta
import random

def insert_surgery_data():
    app = create_app()
    with app.app_context():
        # Check if surgery types already exist
        existing_surgery_types = SurgeryType.query.all()
        if existing_surgery_types:
            print(f"Found {len(existing_surgery_types)} existing surgery types")
        else:
            print("No surgery types found. Adding surgery types...")
            
            # Surgery types data
            surgery_types_data = [
                {
                    'SurgeryCode': 'CARD001',
                    'Name': 'Coronary Artery Bypass Surgery',
                    'Category': SurgeryCategory.HOSPITALIZATION,
                    'AnatomicalLocation': 'Heart',
                    'SpecialNeeds': 'Requires heart-lung machine'
                },
                {
                    'SurgeryCode': 'ORTH001',
                    'Name': 'Total Knee Replacement',
                    'Category': SurgeryCategory.HOSPITALIZATION,
                    'AnatomicalLocation': 'Knee',
                    'SpecialNeeds': 'Requires special prosthetics'
                },
                {
                    'SurgeryCode': 'NEUR001',
                    'Name': 'Craniotomy',
                    'Category': SurgeryCategory.HOSPITALIZATION,
                    'AnatomicalLocation': 'Brain',
                    'SpecialNeeds': 'Requires specialized neurological monitoring'
                },
                {
                    'SurgeryCode': 'GAST001',
                    'Name': 'Appendectomy',
                    'Category': SurgeryCategory.HOSPITALIZATION,
                    'AnatomicalLocation': 'Abdomen',
                    'SpecialNeeds': 'Standard surgical equipment'
                },
                {
                    'SurgeryCode': 'DERM001',
                    'Name': 'Skin Biopsy',
                    'Category': SurgeryCategory.OUTPATIENT,
                    'AnatomicalLocation': 'Skin',
                    'SpecialNeeds': 'Local anesthesia only'
                },
                {
                    'SurgeryCode': 'ENT001',
                    'Name': 'Tonsillectomy',
                    'Category': SurgeryCategory.OUTPATIENT,
                    'AnatomicalLocation': 'Throat',
                    'SpecialNeeds': 'General anesthesia required'
                },
                {
                    'SurgeryCode': 'OPHT001',
                    'Name': 'Cataract Surgery',
                    'Category': SurgeryCategory.OUTPATIENT,
                    'AnatomicalLocation': 'Eye',
                    'SpecialNeeds': 'Specialized ophthalmic equipment'
                },
                {
                    'SurgeryCode': 'ORTH002',
                    'Name': 'Arthroscopic Knee Surgery',
                    'Category': SurgeryCategory.OUTPATIENT,
                    'AnatomicalLocation': 'Knee',
                    'SpecialNeeds': 'Arthroscopic equipment'
                }
            ]
            
            # Add surgery types
            surgery_types_added = 0
            for surgery_type_data in surgery_types_data:
                try:
                    # Check if already exists
                    existing = SurgeryType.query.filter_by(SurgeryCode=surgery_type_data['SurgeryCode']).first()
                    if existing:
                        print(f"Surgery type {surgery_type_data['SurgeryCode']} already exists, skipping...")
                        continue
                    
                    surgery_type = SurgeryType(**surgery_type_data)
                    db.session.add(surgery_type)
                    db.session.commit()
                    
                    surgery_types_added += 1
                    print(f"Added surgery type: {surgery_type_data['Name']}")
                    
                except Exception as e:
                    db.session.rollback()
                    print(f"Error adding surgery type {surgery_type_data['Name']}: {e}")
            
            print(f"Successfully added {surgery_types_added} surgery types")
        
        # Now add surgery skills for each surgery type
        surgery_types = SurgeryType.query.all()
        
        # Check if surgery skills already exist
        existing_skills = SurgerySkill.query.all()
        if existing_skills:
            print(f"Found {len(existing_skills)} existing surgery skills")
        else:
            print("No surgery skills found. Adding surgery skills...")
            
            skills_added = 0
            
            for surgery_type in surgery_types:
                # Define skills for each surgery type
                if 'CARD' in surgery_type.SurgeryCode:
                    skills_data = [
                        {'SkillCode': f"{surgery_type.SurgeryCode}_SKILL1", 'Description': 'Cardiac bypass procedure', 'SurgeryCode': surgery_type.SurgeryCode},
                        {'SkillCode': f"{surgery_type.SurgeryCode}_SKILL2", 'Description': 'Heart-lung machine operation', 'SurgeryCode': surgery_type.SurgeryCode}
                    ]
                elif 'ORTH' in surgery_type.SurgeryCode:
                    skills_data = [
                        {'SkillCode': f"{surgery_type.SurgeryCode}_SKILL1", 'Description': 'Joint replacement', 'SurgeryCode': surgery_type.SurgeryCode},
                        {'SkillCode': f"{surgery_type.SurgeryCode}_SKILL2", 'Description': 'Orthopedic equipment', 'SurgeryCode': surgery_type.SurgeryCode}
                    ]
                elif 'NEUR' in surgery_type.SurgeryCode:
                    skills_data = [
                        {'SkillCode': f"{surgery_type.SurgeryCode}_SKILL1", 'Description': 'Neurological monitoring', 'SurgeryCode': surgery_type.SurgeryCode},
                        {'SkillCode': f"{surgery_type.SurgeryCode}_SKILL2", 'Description': 'Brain surgery techniques', 'SurgeryCode': surgery_type.SurgeryCode}
                    ]
                else:
                    skills_data = [
                        {'SkillCode': f"{surgery_type.SurgeryCode}_SKILL1", 'Description': f"Basic {surgery_type.Name} skills", 'SurgeryCode': surgery_type.SurgeryCode},
                        {'SkillCode': f"{surgery_type.SurgeryCode}_SKILL2", 'Description': f"Advanced {surgery_type.Name} techniques", 'SurgeryCode': surgery_type.SurgeryCode}
                    ]
                
                for skill_data in skills_data:
                    try:
                        # Check if already exists
                        existing = SurgerySkill.query.filter_by(SkillCode=skill_data['SkillCode']).first()
                        if existing:
                            print(f"Skill {skill_data['SkillCode']} already exists, skipping...")
                            continue
                        
                        skill = SurgerySkill(**skill_data)
                        db.session.add(skill)
                        db.session.commit()
                        
                        skills_added += 1
                        print(f"Added skill: {skill_data['Description']} for {surgery_type.Name}")
                        
                    except Exception as e:
                        db.session.rollback()
                        print(f"Error adding skill {skill_data['Description']}: {e}")
            
            print(f"Successfully added {skills_added} surgery skills")
        
        # Add operating rooms if they don't exist
        existing_rooms = OperatingRoom.query.all()
        if existing_rooms:
            print(f"Found {len(existing_rooms)} existing operating rooms")
        else:
            print("No operating rooms found. Adding operating rooms...")
            
            rooms_added = 0
            for i in range(1, 6):  # Add 5 operating rooms
                try:
                    room = OperatingRoom(OpRoomID=i)
                    db.session.add(room)
                    db.session.commit()
                    
                    rooms_added += 1
                    print(f"Added operating room #{i}")
                    
                except Exception as e:
                    db.session.rollback()
                    print(f"Error adding operating room #{i}: {e}")
            
            print(f"Successfully added {rooms_added} operating rooms")
        
        # Now add surgery schedules
        # Get surgeons, patients and surgery types
        surgeons = Surgeon.query.all()
        patients = Patient.query.all()
        operating_rooms = OperatingRoom.query.all()
        
        if not surgeons or not patients or not operating_rooms:
            print("Missing required data (surgeons, patients, or operating rooms). Cannot add surgery schedules.")
            return
        
        # Check existing surgery schedules
        existing_schedules = SurgerySchedule.query.all()
        if existing_schedules:
            print(f"Found {len(existing_schedules)} existing surgery schedules. Will add 10 more.")
        
        print("Adding surgery schedules...")
        
        # Get the maximum schedule ID
        schedule_id_start = db.session.query(db.func.max(SurgerySchedule.ScheduleID)).scalar()
        if schedule_id_start is None:
            schedule_id_start = 1000
        else:
            schedule_id_start += 1
        
        schedules_added = 0
        
        # Generate dates starting from one week ahead, spanning over a month
        start_date = datetime.now().date() + timedelta(days=7)
        date_range = [start_date + timedelta(days=x) for x in range(0, 30)]
        
        # Add exactly 10 new surgery schedules
        for i in range(10):
            try:
                # Randomly select surgeon, patient, surgery type and operating room
                surgeon = random.choice(surgeons)
                patient = random.choice(patients)
                surgery_type = random.choice(surgery_types)
                operating_room = random.choice(operating_rooms)
                
                # Check if this combination already exists
                existing = SurgerySchedule.query.filter_by(
                    PatientID=patient.PatientID,
                    EmpID=surgeon.EmpID,
                    SurgeryCode=surgery_type.SurgeryCode
                ).first()
                
                # If exists, try a different combination
                if existing:
                    # Try up to 5 times to find a non-duplicate
                    for _ in range(5):
                        patient = random.choice(patients)
                        surgeon = random.choice(surgeons)
                        surgery_type = random.choice(surgery_types)
                        
                        existing = SurgerySchedule.query.filter_by(
                            PatientID=patient.PatientID,
                            EmpID=surgeon.EmpID,
                            SurgeryCode=surgery_type.SurgeryCode
                        ).first()
                        
                        if not existing:
                            break
                    
                    # If we still have a duplicate, skip this schedule
                    if existing:
                        print(f"Could not find a non-duplicate combination for surgery schedule, skipping")
                        continue
                
                # Select a random date from the range
                surgery_date = random.choice(date_range)
                
                # Create the surgery schedule
                schedule = SurgerySchedule(
                    ScheduleID=schedule_id_start + i,
                    PatientID=patient.PatientID,
                    EmpID=surgeon.EmpID,
                    Date=surgery_date,
                    SurgeryCode=surgery_type.SurgeryCode,
                    OpRoomID=operating_room.OpRoomID
                )
                
                db.session.add(schedule)
                db.session.commit()
                
                schedules_added += 1
                print(f"Added surgery schedule {schedule_id_start + i} for patient {patient.Name} - {surgery_type.Name}")
                
            except Exception as e:
                db.session.rollback()
                print(f"Error adding surgery schedule: {e}")
        
        print(f"Successfully added {schedules_added} surgery schedules")

if __name__ == '__main__':
    insert_surgery_data() 