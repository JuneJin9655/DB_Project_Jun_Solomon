from app import create_app, db
from app.models import Bed, Wing, BedLabel
import random

def insert_bed_data():
    app = create_app()
    with app.app_context():
        # Check existing beds
        existing_beds = Bed.query.all()
        existing_bed_keys = set()
        
        for bed in existing_beds:
            existing_bed_keys.add((bed.PatientRoomID, bed.BedLabel))
            
        print(f"Found {len(existing_beds)} existing beds in the database.")
        
        # Define wings
        wings = [Wing.BLUE, Wing.GREEN]
        
        # Define rooms (10 rooms per wing)
        rooms_per_wing = 10
        beds_added = 0
        
        # For each wing, create rooms and beds
        for wing in wings:
            for room_num in range(1, rooms_per_wing + 1):
                # Create a unique room ID based on wing and room number
                if wing == Wing.BLUE:
                    patient_room_id = 100 + room_num
                    unit = f"Cardiac Unit {random.randint(1, 3)}"
                else:
                    patient_room_id = 200 + room_num
                    unit = f"General Unit {random.randint(4, 7)}"
                
                # Each room has 2 beds (A and B)
                for bed_label in [BedLabel.A, BedLabel.B]:
                    # Skip if this bed already exists
                    if (patient_room_id, bed_label) in existing_bed_keys:
                        print(f"Bed {patient_room_id}{bed_label.value} already exists, skipping.")
                        continue
                        
                    room_identifier = f"{patient_room_id}{bed_label.value}"
                    
                    # Create the bed
                    bed = Bed(
                        PatientRoomID=patient_room_id,
                        BedLabel=bed_label,
                        RoomNum=room_identifier,
                        Unit=unit,
                        Wing=wing
                    )
                    
                    try:
                        db.session.add(bed)
                        beds_added += 1
                        print(f"Added bed {room_identifier} in {wing.value} Wing, {unit}")
                    except Exception as e:
                        db.session.rollback()
                        print(f"Error adding bed {room_identifier}: {e}")
        
        try:
            db.session.commit()
            print(f"Successfully added {beds_added} beds")
        except Exception as e:
            db.session.rollback()
            print(f"Error committing beds to database: {e}")

if __name__ == '__main__':
    insert_bed_data() 