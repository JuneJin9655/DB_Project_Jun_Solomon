from app import create_app, db
from app.models import SurgeryType, Surgeon, Patient, SurgerySchedule, OperatingRoom
from datetime import datetime, timedelta
import random

def insert_surgery_schedules():
    app = create_app()
    with app.app_context():
        # Get surgeons, patients, surgery types and operating rooms
        surgeons = Surgeon.query.all()
        patients = Patient.query.all()
        surgery_types = SurgeryType.query.all()
        operating_rooms = OperatingRoom.query.all()
        
        if not surgeons or not patients or not surgery_types or not operating_rooms:
            print("Missing required data (surgeons, patients, surgery types, or operating rooms). Cannot add surgery schedules.")
            return
        
        # Check existing surgery schedules
        existing_schedules = SurgerySchedule.query.all()
        if existing_schedules:
            print(f"Found {len(existing_schedules)} existing surgery schedules. Will add 15 more.")
        
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
        
        # Create a set to track existing combinations
        existing_combinations = set()
        for schedule in existing_schedules:
            existing_combinations.add((schedule.PatientID, schedule.EmpID, schedule.SurgeryCode))
        
        # Add 15 new surgery schedules
        for i in range(15):
            for _ in range(10):  # Try up to 10 times to find a non-duplicate
                # Randomly select surgeon, patient, surgery type and operating room
                surgeon = random.choice(surgeons)
                patient = random.choice(patients)
                surgery_type = random.choice(surgery_types)
                operating_room = random.choice(operating_rooms)
                
                # Check if this combination already exists
                combination = (patient.PatientID, surgeon.EmpID, surgery_type.SurgeryCode)
                if combination not in existing_combinations:
                    break
            
            # If we still have a duplicate after 10 attempts, skip this schedule
            if combination in existing_combinations:
                print(f"Could not find a non-duplicate combination for surgery schedule after 10 attempts, skipping")
                continue
            
            # Select a random date from the range
            surgery_date = random.choice(date_range)
            
            try:
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
                
                # Add to set of existing combinations
                existing_combinations.add(combination)
                
                schedules_added += 1
                print(f"Added surgery schedule {schedule_id_start + i} for patient {patient.Name} - {surgery_type.Name}")
                
            except Exception as e:
                db.session.rollback()
                print(f"Error adding surgery schedule: {e}")
        
        print(f"Successfully added {schedules_added} surgery schedules")

if __name__ == '__main__':
    insert_surgery_schedules() 