from app import create_app, db
from app.models import SurgeryType, SurgerySkill, SurgeryCategory
import random

def insert_surgery_types():
    app = create_app()
    with app.app_context():
        # Check if surgery types already exist
        existing_surgery_types = SurgeryType.query.all()
        if existing_surgery_types:
            print(f"Found {len(existing_surgery_types)} existing surgery types. Will add more.")
        
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
            },
            {
                'SurgeryCode': 'CARD002',
                'Name': 'Heart Valve Replacement',
                'Category': SurgeryCategory.HOSPITALIZATION,
                'AnatomicalLocation': 'Heart',
                'SpecialNeeds': 'Cardiac support equipment'
            },
            {
                'SurgeryCode': 'VASC001',
                'Name': 'Carotid Endarterectomy',
                'Category': SurgeryCategory.HOSPITALIZATION,
                'AnatomicalLocation': 'Neck',
                'SpecialNeeds': 'Vascular instrumentation'
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
        skill_codes = {skill.SkillCode for skill in existing_skills}
        print(f"Found {len(existing_skills)} existing surgery skills")
        
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
            elif 'VASC' in surgery_type.SurgeryCode:
                skills_data = [
                    {'SkillCode': f"{surgery_type.SurgeryCode}_SKILL1", 'Description': 'Vascular repair techniques', 'SurgeryCode': surgery_type.SurgeryCode},
                    {'SkillCode': f"{surgery_type.SurgeryCode}_SKILL2", 'Description': 'Blood flow monitoring', 'SurgeryCode': surgery_type.SurgeryCode}
                ]
            elif 'OPHT' in surgery_type.SurgeryCode:
                skills_data = [
                    {'SkillCode': f"{surgery_type.SurgeryCode}_SKILL1", 'Description': 'Precise ocular handling', 'SurgeryCode': surgery_type.SurgeryCode},
                    {'SkillCode': f"{surgery_type.SurgeryCode}_SKILL2", 'Description': 'Microscopic surgery techniques', 'SurgeryCode': surgery_type.SurgeryCode}
                ]
            else:
                skills_data = [
                    {'SkillCode': f"{surgery_type.SurgeryCode}_SKILL1", 'Description': f"Basic {surgery_type.Name} skills", 'SurgeryCode': surgery_type.SurgeryCode},
                    {'SkillCode': f"{surgery_type.SurgeryCode}_SKILL2", 'Description': f"Advanced {surgery_type.Name} techniques", 'SurgeryCode': surgery_type.SurgeryCode}
                ]
            
            for skill_data in skills_data:
                # Skip if skill code already exists
                if skill_data['SkillCode'] in skill_codes:
                    print(f"Skill {skill_data['SkillCode']} already exists, skipping...")
                    continue
                
                try:
                    skill = SurgerySkill(**skill_data)
                    db.session.add(skill)
                    db.session.commit()
                    
                    # Add to set of existing skill codes
                    skill_codes.add(skill_data['SkillCode'])
                    
                    skills_added += 1
                    print(f"Added skill: {skill_data['Description']} for {surgery_type.Name}")
                    
                except Exception as e:
                    db.session.rollback()
                    print(f"Error adding skill {skill_data['Description']}: {e}")
        
        print(f"Successfully added {skills_added} surgery skills")

if __name__ == '__main__':
    insert_surgery_types() 