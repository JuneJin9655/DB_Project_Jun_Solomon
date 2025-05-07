from app import create_app, db
from app.models import Patient, Physician, Prescription, Medication, DrugInteraction, InteractionSeverity
import random

def insert_prescription_data():
    app = create_app()
    with app.app_context():
        # Get existing patients and physicians
        patients = Patient.query.all()
        physicians = Physician.query.all()
        medications = Medication.query.all()
        
        if not patients or not physicians or not medications:
            print("No patients, physicians, or medications found. Make sure to insert this data first.")
            return
        
        # Check if prescriptions already exist
        existing_prescriptions = Prescription.query.all()
        if existing_prescriptions:
            print(f"Found {len(existing_prescriptions)} existing prescriptions. Will add 10 more.")
            
        print(f"Adding additional prescription data...")
        
        # Get the maximum prescription ID
        prescription_id_start = db.session.query(db.func.max(Prescription.PrescriptionID)).scalar()
        if prescription_id_start is None:
            prescription_id_start = 1000
        else:
            prescription_id_start += 1
        
        prescriptions_added = 0
        
        # Add exactly 10 new prescriptions
        for i in range(10):
            # Randomly select patient, medication and physician
            patient = random.choice(patients)
            medication = random.choice(medications)
            physician = random.choice(physicians)
            
            # Check if this prescription already exists
            existing = Prescription.query.filter_by(
                PatientID=patient.PatientID,
                MedicationCode=medication.MedicationCode
            ).first()
            
            # If exists, try a different medication
            if existing:
                # Try up to 5 times to find a non-duplicate
                for _ in range(5):
                    medication = random.choice(medications)
                    existing = Prescription.query.filter_by(
                        PatientID=patient.PatientID,
                        MedicationCode=medication.MedicationCode
                    ).first()
                    if not existing:
                        break
                
                # If we still have a duplicate, skip this prescription
                if existing:
                    print(f"Could not find a non-duplicate medication for patient {patient.PatientID}, skipping")
                    continue
            
            # Randomly generate dosage and frequency
            dosage_options = ["10mg", "20mg", "30mg", "50mg", "100mg"]
            frequency_options = ["Once daily", "Twice daily", "Three times daily", "As needed", "Every 4-6 hours"]
            
            try:
                prescription = Prescription(
                    PrescriptionID=prescription_id_start + i,
                    PatientID=patient.PatientID,
                    MedicationCode=medication.MedicationCode,
                    EmpID=physician.EmpID,
                    Dosage=random.choice(dosage_options),
                    Frequency=random.choice(frequency_options)
                )
                
                db.session.add(prescription)
                db.session.commit()
                prescriptions_added += 1
                print(f"Added prescription {prescription_id_start + i} for patient {patient.Name} - {medication.MedicationName}")
                
            except Exception as e:
                db.session.rollback()
                print(f"Error adding prescription for patient {patient.PatientID}: {e}")
        
        print(f"Successfully added {prescriptions_added} prescriptions")
        
        # Add drug interactions if they don't exist yet
        existing_interactions = DrugInteraction.query.all()
        if not existing_interactions:
            print("Adding drug interactions...")
            
            # Define common drug interactions
            interactions = [
                # Warfarin interactions
                {'Medication1': 'MED011', 'Medication2': 'MED001', 'Severity': InteractionSeverity.SEVERE}, # Warfarin + Aspirin
                {'Medication1': 'MED011', 'Medication2': 'MED002', 'Severity': InteractionSeverity.SEVERE}, # Warfarin + Ibuprofen
                {'Medication1': 'MED011', 'Medication2': 'MED012', 'Severity': InteractionSeverity.MODERATE}, # Warfarin + Clopidogrel
                
                # Antibiotic interactions
                {'Medication1': 'MED004', 'Medication2': 'MED005', 'Severity': InteractionSeverity.LITTLE}, # Amoxicillin + Ciprofloxacin
                
                # Antihypertensive interactions
                {'Medication1': 'MED006', 'Medication2': 'MED015', 'Severity': InteractionSeverity.MODERATE}, # Lisinopril + Hydrochlorothiazide
                
                # Psychiatric medication interactions
                {'Medication1': 'MED017', 'Medication2': 'MED019', 'Severity': InteractionSeverity.SEVERE}, # Fluoxetine + Diazepam
                {'Medication1': 'MED018', 'Medication2': 'MED020', 'Severity': InteractionSeverity.SEVERE}, # Sertraline + Lorazepam
                {'Medication1': 'MED017', 'Medication2': 'MED018', 'Severity': InteractionSeverity.MODERATE}, # Fluoxetine + Sertraline
                
                # Gastrointestinal medication interactions
                {'Medication1': 'MED009', 'Medication2': 'MED004', 'Severity': InteractionSeverity.MODERATE}, # Omeprazole + Amoxicillin
                
                # Cholesterol medication interactions
                {'Medication1': 'MED008', 'Medication2': 'MED010', 'Severity': InteractionSeverity.LITTLE}, # Atorvastatin + Simvastatin
                
                # Other interactions
                {'Medication1': 'MED007', 'Medication2': 'MED013', 'Severity': InteractionSeverity.MODERATE}, # Metformin + Insulin
                {'Medication1': 'MED016', 'Medication2': 'MED014', 'Severity': InteractionSeverity.LITTLE}, # Prednisone + Levothyroxine
            ]
            
            interactions_added = 0
            
            for interaction_data in interactions:
                # Check if medications exist
                med1 = Medication.query.get(interaction_data['Medication1'])
                med2 = Medication.query.get(interaction_data['Medication2'])
                
                if not med1 or not med2:
                    print(f"Skipping interaction - medication not found: {interaction_data['Medication1']} or {interaction_data['Medication2']}")
                    continue
                
                try:
                    interaction = DrugInteraction(**interaction_data)
                    db.session.add(interaction)
                    db.session.commit()
                    interactions_added += 1
                except Exception as e:
                    db.session.rollback()
                    print(f"Error adding drug interaction: {e}")
            
            print(f"Successfully added {interactions_added} drug interactions")
        else:
            print(f"Found {len(existing_interactions)} existing drug interactions. Skipping insertion.")

if __name__ == '__main__':
    insert_prescription_data() 