from app import create_app, db
from app.models import Illness, Allergy

def insert_illness_data():
    """Insert illness and allergy data"""
    app = create_app()
    with app.app_context():
        # Check if data already exists
        existing_illnesses = Illness.query.all()
        existing_allergies = Allergy.query.all()
        
        if existing_illnesses and existing_allergies:
            print(f"Found {len(existing_illnesses)} existing illnesses and {len(existing_allergies)} existing allergies.")
            return
        
        # Illnesses data
        illnesses_data = [
            {'IllnessCode': 'ILL001', 'Description': 'Hypertension'},
            {'IllnessCode': 'ILL002', 'Description': 'Type 2 Diabetes'},
            {'IllnessCode': 'ILL003', 'Description': 'Asthma'},
            {'IllnessCode': 'ILL004', 'Description': 'Coronary Artery Disease'},
            {'IllnessCode': 'ILL005', 'Description': 'Osteoarthritis'},
            {'IllnessCode': 'ILL006', 'Description': 'Depression'},
            {'IllnessCode': 'ILL007', 'Description': 'Chronic Obstructive Pulmonary Disease'},
            {'IllnessCode': 'ILL008', 'Description': 'Cancer'},
            {'IllnessCode': 'ILL009', 'Description': 'Stroke'},
            {'IllnessCode': 'ILL010', 'Description': 'Alzheimer\'s Disease'}
        ]
        
        # Allergies data
        allergies_data = [
            {'AllergyCode': 'ALL001', 'AllergyName': 'Penicillin'},
            {'AllergyCode': 'ALL002', 'AllergyName': 'Peanuts'},
            {'AllergyCode': 'ALL003', 'AllergyName': 'Shellfish'},
            {'AllergyCode': 'ALL004', 'AllergyName': 'Latex'},
            {'AllergyCode': 'ALL005', 'AllergyName': 'Bee Stings'},
            {'AllergyCode': 'ALL006', 'AllergyName': 'Sulfa Drugs'},
            {'AllergyCode': 'ALL007', 'AllergyName': 'Dust Mites'},
            {'AllergyCode': 'ALL008', 'AllergyName': 'Tree Nuts'}
        ]
        
        # Add illnesses
        illnesses_added = 0
        for illness_data in illnesses_data:
            try:
                # Check if already exists
                existing = Illness.query.filter_by(IllnessCode=illness_data['IllnessCode']).first()
                if existing:
                    print(f"Illness {illness_data['IllnessCode']} already exists, skipping...")
                    continue
                
                illness = Illness(**illness_data)
                db.session.add(illness)
                db.session.commit()
                
                illnesses_added += 1
                print(f"Added illness: {illness_data['Description']}")
                
            except Exception as e:
                db.session.rollback()
                print(f"Error adding illness {illness_data['Description']}: {e}")
        
        # Add allergies
        allergies_added = 0
        for allergy_data in allergies_data:
            try:
                # Check if already exists
                existing = Allergy.query.filter_by(AllergyCode=allergy_data['AllergyCode']).first()
                if existing:
                    print(f"Allergy {allergy_data['AllergyCode']} already exists, skipping...")
                    continue
                
                allergy = Allergy(**allergy_data)
                db.session.add(allergy)
                db.session.commit()
                
                allergies_added += 1
                print(f"Added allergy: {allergy_data['AllergyName']}")
                
            except Exception as e:
                db.session.rollback()
                print(f"Error adding allergy {allergy_data['AllergyName']}: {e}")
        
        print(f"\nSummary:")
        print(f"Added {illnesses_added} illnesses")
        print(f"Added {allergies_added} allergies")

if __name__ == "__main__":
    insert_illness_data() 