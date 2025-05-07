from app import create_app, db
from app.models import Medication, DrugInteraction, InteractionSeverity, Prescription
from app.models import Patient, Physician
from datetime import datetime
import random

def insert_medication_data():
    app = create_app()
    with app.app_context():
        # Delete existing data (if needed)
        try:
            db.session.query(DrugInteraction).delete()
            db.session.query(Medication).delete()
            db.session.commit()
            print("Successfully cleared existing medication and drug interaction data")
        except Exception as e:
            db.session.rollback()
            print(f"Error clearing data: {e}")
        
        # Add medication data
        medications = [
            {
                'MedicationCode': 'MED001',
                'MedicationName': 'Aspirin',
                'QuantityOnHand': 150,
                'QuantityOnOrder': 50,
                'UnitCost': 5.99,
                'YearToDateUsage': 300
            },
            {
                'MedicationCode': 'MED002',
                'MedicationName': 'Ibuprofen',
                'QuantityOnHand': 120,
                'QuantityOnOrder': 30,
                'UnitCost': 7.50,
                'YearToDateUsage': 250
            },
            {
                'MedicationCode': 'MED003',
                'MedicationName': 'Paracetamol',
                'QuantityOnHand': 200,
                'QuantityOnOrder': 100,
                'UnitCost': 4.25,
                'YearToDateUsage': 350
            },
            {
                'MedicationCode': 'MED004',
                'MedicationName': 'Amoxicillin',
                'QuantityOnHand': 80,
                'QuantityOnOrder': 50,
                'UnitCost': 12.75,
                'YearToDateUsage': 150
            },
            {
                'MedicationCode': 'MED005',
                'MedicationName': 'Ciprofloxacin',
                'QuantityOnHand': 60,
                'QuantityOnOrder': 40,
                'UnitCost': 18.50,
                'YearToDateUsage': 90
            },
            {
                'MedicationCode': 'MED006',
                'MedicationName': 'Lisinopril',
                'QuantityOnHand': 100,
                'QuantityOnOrder': 50,
                'UnitCost': 15.25,
                'YearToDateUsage': 120
            },
            {
                'MedicationCode': 'MED007',
                'MedicationName': 'Metformin',
                'QuantityOnHand': 120,
                'QuantityOnOrder': 60,
                'UnitCost': 9.99,
                'YearToDateUsage': 180
            },
            {
                'MedicationCode': 'MED008',
                'MedicationName': 'Atorvastatin',
                'QuantityOnHand': 90,
                'QuantityOnOrder': 45,
                'UnitCost': 22.50,
                'YearToDateUsage': 110
            },
            {
                'MedicationCode': 'MED009',
                'MedicationName': 'Omeprazole',
                'QuantityOnHand': 110,
                'QuantityOnOrder': 40,
                'UnitCost': 11.75,
                'YearToDateUsage': 130
            },
            {
                'MedicationCode': 'MED010',
                'MedicationName': 'Simvastatin',
                'QuantityOnHand': 70,
                'QuantityOnOrder': 35,
                'UnitCost': 18.25,
                'YearToDateUsage': 85
            },
            {
                'MedicationCode': 'MED011',
                'MedicationName': 'Warfarin',
                'QuantityOnHand': 50,
                'QuantityOnOrder': 30,
                'UnitCost': 14.50,
                'YearToDateUsage': 65
            },
            {
                'MedicationCode': 'MED012',
                'MedicationName': 'Clopidogrel',
                'QuantityOnHand': 40,
                'QuantityOnOrder': 20,
                'UnitCost': 25.99,
                'YearToDateUsage': 55
            },
            {
                'MedicationCode': 'MED013',
                'MedicationName': 'Insulin',
                'QuantityOnHand': 30,
                'QuantityOnOrder': 20,
                'UnitCost': 42.75,
                'YearToDateUsage': 45
            },
            {
                'MedicationCode': 'MED014',
                'MedicationName': 'Levothyroxine',
                'QuantityOnHand': 75,
                'QuantityOnOrder': 35,
                'UnitCost': 16.25,
                'YearToDateUsage': 90
            },
            {
                'MedicationCode': 'MED015',
                'MedicationName': 'Hydrochlorothiazide',
                'QuantityOnHand': 65,
                'QuantityOnOrder': 30,
                'UnitCost': 8.50,
                'YearToDateUsage': 80
            },
            {
                'MedicationCode': 'MED016',
                'MedicationName': 'Prednisone',
                'QuantityOnHand': 45,
                'QuantityOnOrder': 25,
                'UnitCost': 10.25,
                'YearToDateUsage': 60
            },
            {
                'MedicationCode': 'MED017',
                'MedicationName': 'Fluoxetine',
                'QuantityOnHand': 55,
                'QuantityOnOrder': 25,
                'UnitCost': 19.75,
                'YearToDateUsage': 70
            },
            {
                'MedicationCode': 'MED018',
                'MedicationName': 'Sertraline',
                'QuantityOnHand': 50,
                'QuantityOnOrder': 25,
                'UnitCost': 21.50,
                'YearToDateUsage': 65
            },
            {
                'MedicationCode': 'MED019',
                'MedicationName': 'Diazepam',
                'QuantityOnHand': 20,
                'QuantityOnOrder': 10,
                'UnitCost': 17.25,
                'YearToDateUsage': 30
            },
            {
                'MedicationCode': 'MED020',
                'MedicationName': 'Lorazepam',
                'QuantityOnHand': 15,
                'QuantityOnOrder': 15,
                'UnitCost': 18.99,
                'YearToDateUsage': 25
            }
        ]
        
        # Bulk add medications
        for med_data in medications:
            medication = Medication(**med_data)
            db.session.add(medication)
        
        try:
            db.session.commit()
            print(f"Successfully added {len(medications)} medications")
        except Exception as e:
            db.session.rollback()
            print(f"Error adding medications: {e}")
            return

        # Drug interactions
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
        
        for interaction_data in interactions:
            interaction = DrugInteraction(**interaction_data)
            db.session.add(interaction)
        
        try:
            db.session.commit()
            print(f"Successfully added {len(interactions)} drug interactions")
        except Exception as e:
            db.session.rollback()
            print(f"Error adding drug interactions: {e}")
            return
            
        # Add prescription data for existing patients
        try:
            # Get existing patients and physicians
            patients = Patient.query.all()
            physicians = Physician.query.all()
            
            if patients and physicians:
                print("Adding prescription data for existing patients...")
                
                # Get the maximum prescription ID
                prescription_id_start = db.session.query(db.func.max(Prescription.PrescriptionID)).scalar()
                if prescription_id_start is None:
                    prescription_id_start = 1000
                
                for i, patient in enumerate(patients):
                    # Add 1-3 prescriptions for each patient
                    num_prescriptions = random.randint(1, 3)
                    for j in range(num_prescriptions):
                        prescription_id = prescription_id_start + i*3 + j + 1
                        
                        # Randomly select medication and physician
                        med_code = medications[random.randint(0, len(medications)-1)]['MedicationCode']
                        physician = random.choice(physicians)
                        
                        # Randomly generate dosage and frequency
                        dosage_options = ["10mg", "20mg", "30mg", "50mg", "100mg"]
                        frequency_options = ["Once daily", "Twice daily", "Three times daily", "As needed", "Every 4-6 hours"]
                        
                        prescription = {
                            'PrescriptionID': prescription_id,
                            'PatientID': patient.PatientID,
                            'MedicationCode': med_code,
                            'EmpID': physician.EmpID,
                            'Dosage': random.choice(dosage_options),
                            'Frequency': random.choice(frequency_options)
                        }
                        
                        prescription_obj = Prescription(**prescription)
                        db.session.add(prescription_obj)
                
                db.session.commit()
                print(f"Successfully added prescription data for {len(patients)} patients")
            else:
                print("No existing patients or physicians found, skipping prescription data")
                
        except Exception as e:
            db.session.rollback()
            print(f"Error adding prescription data: {e}")

if __name__ == '__main__':
    insert_medication_data() 