from app import create_app, db
from app.models import Clinic, Owner, MedicalCorporation

def insert_clinic_data():
    """Insert basic clinic, owner, and medical corporation data"""
    app = create_app()
    with app.app_context():
        # Check if clinics already exist
        existing_clinics = Clinic.query.all()
        if existing_clinics:
            print(f"Found {len(existing_clinics)} existing clinics, skipping clinic creation.")
            return
        
        print("Adding clinic data...")
        
        try:
            # Create main clinic
            clinic = Clinic(
                ClinicID=1,
                ClinicName="Newark Medical Associates",
                Address="500 Medical Plaza, Newark, NJ 07102"
            )
            db.session.add(clinic)
            db.session.flush()  # Flush to get the ID
            
            # Create owner
            owner = Owner(
                OwnerID=1,
                Percentage=100.0  # Full ownership
            )
            db.session.add(owner)
            db.session.flush()
            
            # Create medical corporation
            corp = MedicalCorporation(
                CorpName="Newark Healthcare System",
                OwnerID=owner.OwnerID,
                ClinicID=clinic.ClinicID,
                Percentage=100.0,
                CorpHeadquarters="100 Corporate Drive, Newark, NJ 07102"
            )
            db.session.add(corp)
            
            db.session.commit()
            print(f"Added clinic: {clinic.ClinicName}")
            print(f"Added medical corporation: {corp.CorpName}")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error adding clinic data: {e}")

if __name__ == "__main__":
    insert_clinic_data() 