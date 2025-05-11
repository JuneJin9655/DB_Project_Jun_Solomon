from app import create_app, db
from app.models import Patient, Physician, Nurse, Surgeon, ClinicPersonnel
from app.models import Inpatient, Consultation, Diagnosis, Prescription, SurgerySchedule
from app.models import Medication, SurgeryType, SurgerySkill, NurseSkill, Illness, Bed
from datetime import datetime, timedelta
import random

def balance_relationships():
    """Ensure all entities have proper relationships with even distribution"""
    app = create_app()
    with app.app_context():
        print("Balancing relationships between entities...")
        
        # 1. Make sure each physician has at least some patients
        balance_physicians_patients()
        
        # 2. Ensure all nurses have inpatients assigned
        balance_nurses_inpatients()
        
        # 3. Make sure all surgeons have surgeries scheduled
        balance_surgeons_surgeries()
        
        # 4. Ensure all surgery types are used in schedules
        balance_surgery_types()
        
        # 5. Make sure all patients have at least one consultation
        balance_patient_consultations()
        
        # 6. Ensure all patients have at least one prescription
        balance_patient_prescriptions()
        
        print("All relationships have been balanced.")

def balance_physicians_patients():
    """Ensure all physicians have patients assigned"""
    physicians = Physician.query.all()
    patients = Patient.query.all()
    
    print("\nBalancing physician-patient relationships...")
    
    # Check if we have all required data
    if not physicians:
        print("No physicians found. Cannot balance physician-patient relationships.")
        return
        
    if not patients:
        print("No patients found. Cannot balance physician-patient relationships.")
        return
    
    # Track how many patients each physician has
    physician_patients = {}
    for physician in physicians:
        patient_count = Patient.query.filter_by(PrimaryPhysicianID=physician.EmpID).count()
        physician_patients[physician.EmpID] = patient_count
        print(f"Physician {physician.EmpID} has {patient_count} patients")
    
    # Get physicians with no patients and unassigned patients
    physicians_without_patients = [p for p, count in physician_patients.items() if count == 0]
    
    # Assign patients to physicians with no patients
    changes_made = 0
    for physician_id in physicians_without_patients:
        # Find patients with the least assigned physicians
        for patient in patients:
            if Patient.query.filter_by(PrimaryPhysicianID=patient.PrimaryPhysicianID).count() > 3:
                # This physician has many patients, reassign one
                try:
                    patient.PrimaryPhysicianID = physician_id
                    db.session.commit()
                    changes_made += 1
                    print(f"Assigned patient {patient.PatientID} to physician {physician_id}")
                    break
                except Exception as e:
                    db.session.rollback()
                    print(f"Error assigning patient to physician: {e}")
    
    # If no changes were made but still have physicians without patients, assign new patients
    if changes_made == 0 and physicians_without_patients:
        # Find patients without assigned physicians and assign them
        for patient in patients:
            if patient.PrimaryPhysicianID is None:
                try:
                    physician_id = physicians_without_patients.pop(0)
                    patient.PrimaryPhysicianID = physician_id
                    db.session.commit()
                    changes_made += 1
                    print(f"Assigned unassigned patient {patient.PatientID} to physician {physician_id}")
                    
                    if not physicians_without_patients:
                        break
                except Exception as e:
                    db.session.rollback()
                    print(f"Error assigning patient to physician: {e}")
    
    print(f"Made {changes_made} changes to physician-patient assignments")

def balance_nurses_inpatients():
    """Ensure all nurses have at least some inpatients assigned"""
    nurses = Nurse.query.all()
    inpatients = Inpatient.query.all()
    beds = Bed.query.all()
    
    print("\nBalancing nurse-inpatient relationships...")
    
    # Check if we have all required data
    if not nurses:
        print("No nurses found. Cannot balance nurse-inpatient relationships.")
        return
        
    if not inpatients:
        print("No inpatients found. Cannot balance nurse-inpatient relationships.")
        return
    
    # Track how many inpatients each nurse has
    nurse_inpatients = {}
    for nurse in nurses:
        inpatient_count = Inpatient.query.filter_by(EmpID=nurse.EmpID).count()
        nurse_inpatients[nurse.EmpID] = inpatient_count
        print(f"Nurse {nurse.EmpID} has {inpatient_count} inpatients")
    
    # Get nurses with no inpatients
    nurses_without_inpatients = [n.EmpID for n in nurses if nurse_inpatients.get(n.EmpID, 0) == 0]
    
    # Assign inpatients to nurses with none
    changes_made = 0
    for nurse_id in nurses_without_inpatients:
        # First check for inpatients without assigned nurses
        unassigned_inpatients = Inpatient.query.filter(Inpatient.EmpID.is_(None)).all()
        
        if unassigned_inpatients:
            for inpatient in unassigned_inpatients:
                try:
                    inpatient.EmpID = nurse_id
                    db.session.commit()
                    changes_made += 1
                    print(f"Assigned inpatient {inpatient.PatientID} to nurse {nurse_id}")
                    break
                except Exception as e:
                    db.session.rollback()
                    print(f"Error assigning inpatient to nurse: {e}")
        else:
            # If no unassigned inpatients, reassign from nurses with many inpatients
            for inpatient in inpatients:
                current_nurse_id = inpatient.EmpID
                if current_nurse_id and nurse_inpatients.get(current_nurse_id, 0) > 2:
                    try:
                        inpatient.EmpID = nurse_id
                        db.session.commit()
                        nurse_inpatients[current_nurse_id] -= 1
                        nurse_inpatients[nurse_id] = nurse_inpatients.get(nurse_id, 0) + 1
                        changes_made += 1
                        print(f"Reassigned inpatient {inpatient.PatientID} from nurse {current_nurse_id} to nurse {nurse_id}")
                        break
                    except Exception as e:
                        db.session.rollback()
                        print(f"Error reassigning inpatient: {e}")
    
    print(f"Made {changes_made} changes to nurse-inpatient assignments")

def balance_surgeons_surgeries():
    """Ensure all surgeons have surgeries scheduled"""
    surgeons = Surgeon.query.all()
    surgery_types = SurgeryType.query.all()
    patients = Patient.query.all()
    operating_rooms = db.session.query(db.func.max(SurgerySchedule.OpRoomID)).scalar() or 1
    
    print("\nBalancing surgeon-surgery relationships...")
    
    # Check if we have all required data
    if not surgeons:
        print("No surgeons found. Cannot balance surgeon-surgery relationships.")
        return
        
    if not patients:
        print("No patients found. Cannot balance surgeon-surgery relationships.")
        return
        
    if not surgery_types:
        print("No surgery types found. Cannot balance surgeon-surgery relationships.")
        return
    
    # Track scheduled surgeries per surgeon
    surgeon_surgeries = {}
    for surgeon in surgeons:
        surgery_count = SurgerySchedule.query.filter_by(EmpID=surgeon.EmpID).count()
        surgeon_surgeries[surgeon.EmpID] = surgery_count
        print(f"Surgeon {surgeon.EmpID} has {surgery_count} scheduled surgeries")
    
    # Get surgeons with no surgeries
    surgeons_without_surgeries = [s.EmpID for s in surgeons if surgeon_surgeries.get(s.EmpID, 0) == 0]
    
    # Get the maximum schedule ID
    max_schedule_id = db.session.query(db.func.max(SurgerySchedule.ScheduleID)).scalar() or 1000
    
    # Add surgeries for surgeons without any
    changes_made = 0
    for surgeon_id in surgeons_without_surgeries:
        # Find a patient without too many surgeries
        for patient in patients:
            if SurgerySchedule.query.filter_by(PatientID=patient.PatientID).count() < 2:
                # This patient doesn't have many surgeries scheduled
                try:
                    # Schedule a new surgery
                    surgery_type = random.choice(surgery_types)
                    surgery_date = datetime.now().date() + timedelta(days=random.randint(7, 30))
                    
                    max_schedule_id += 1
                    schedule = SurgerySchedule(
                        ScheduleID=max_schedule_id,
                        PatientID=patient.PatientID,
                        EmpID=surgeon_id,
                        Date=surgery_date,
                        SurgeryCode=surgery_type.SurgeryCode,
                        OpRoomID=random.randint(1, operating_rooms)
                    )
                    
                    db.session.add(schedule)
                    db.session.commit()
                    
                    changes_made += 1
                    print(f"Added surgery schedule for surgeon {surgeon_id} with patient {patient.PatientID}")
                    break
                except Exception as e:
                    db.session.rollback()
                    print(f"Error adding surgery schedule: {e}")
    
    print(f"Made {changes_made} changes to surgeon-surgery schedules")

def balance_surgery_types():
    """Ensure all surgery types are used in schedules"""
    surgery_types = SurgeryType.query.all()
    surgeons = Surgeon.query.all()
    patients = Patient.query.all()
    operating_rooms = db.session.query(db.func.max(SurgerySchedule.OpRoomID)).scalar() or 1
    
    print("\nBalancing surgery type usage...")
    
    # Check if we have all required data
    if not patients:
        print("No patients found. Cannot balance surgery types.")
        return
        
    if not surgeons:
        print("No surgeons found. Cannot balance surgery types.")
        return
    
    # Track which surgery types are used
    surgery_type_usage = {}
    for surgery_type in surgery_types:
        usage_count = SurgerySchedule.query.filter_by(SurgeryCode=surgery_type.SurgeryCode).count()
        surgery_type_usage[surgery_type.SurgeryCode] = usage_count
        print(f"Surgery type {surgery_type.Name} is used in {usage_count} schedules")
    
    # Get unused surgery types
    unused_surgery_types = [st.SurgeryCode for st in surgery_types if surgery_type_usage.get(st.SurgeryCode, 0) == 0]
    
    # Get the maximum schedule ID
    max_schedule_id = db.session.query(db.func.max(SurgerySchedule.ScheduleID)).scalar() or 1000
    
    # Add schedules for unused surgery types
    changes_made = 0
    for surgery_code in unused_surgery_types:
        # Find a surgeon with the fewest surgeries
        surgeon = min(surgeons, key=lambda s: SurgerySchedule.query.filter_by(EmpID=s.EmpID).count())
        
        # Find a patient with fewest surgeries
        patient = min(patients, key=lambda p: SurgerySchedule.query.filter_by(PatientID=p.PatientID).count())
        
        try:
            # Schedule a new surgery with this type
            surgery_date = datetime.now().date() + timedelta(days=random.randint(7, 30))
            
            max_schedule_id += 1
            schedule = SurgerySchedule(
                ScheduleID=max_schedule_id,
                PatientID=patient.PatientID,
                EmpID=surgeon.EmpID,
                Date=surgery_date,
                SurgeryCode=surgery_code,
                OpRoomID=random.randint(1, operating_rooms)
            )
            
            db.session.add(schedule)
            db.session.commit()
            
            changes_made += 1
            print(f"Added surgery schedule for type {surgery_code} with surgeon {surgeon.EmpID} and patient {patient.PatientID}")
        except Exception as e:
            db.session.rollback()
            print(f"Error adding surgery schedule: {e}")
    
    print(f"Made {changes_made} changes to surgery type usage")

def balance_patient_consultations():
    """Ensure all patients have at least one consultation"""
    patients = Patient.query.all()
    physicians = Physician.query.all()
    illnesses = Illness.query.all()
    
    print("\nBalancing patient consultations...")
    
    # Check if we have all required data
    if not patients:
        print("No patients found. Cannot balance consultations.")
        return
        
    if not physicians:
        print("No physicians found. Cannot balance consultations.")
        return
    
    # Track consultations per patient
    patient_consultations = {}
    for patient in patients:
        consult_count = Consultation.query.filter_by(PatientID=patient.PatientID).count()
        patient_consultations[patient.PatientID] = consult_count
    
    # Get patients with no consultations
    patients_without_consultations = [p.PatientID for p in patients if patient_consultations.get(p.PatientID, 0) == 0]
    
    # Get the maximum consultation ID
    max_consultation_id = db.session.query(db.func.max(Consultation.ConsultationID)).scalar() or 1000
    
    # Add consultations for patients without any
    changes_made = 0
    for patient_id in patients_without_consultations:
        # Get the patient's primary physician
        patient = Patient.query.get(patient_id)
        physician_id = patient.PrimaryPhysicianID
        
        # If no primary physician, assign one
        if not physician_id and physicians:
            physician_id = random.choice(physicians).EmpID
            patient.PrimaryPhysicianID = physician_id
            db.session.flush()
            
        if physician_id:
            try:
                # Add a consultation
                consult_date = datetime.now().date() - timedelta(days=random.randint(1, 60))
                
                max_consultation_id += 1
                consultation = Consultation(
                    ConsultationID=max_consultation_id,
                    PatientID=patient_id,
                    EmpID=physician_id,
                    ConsultationDate=consult_date
                )
                
                db.session.add(consultation)
                db.session.flush()
                
                # Add a diagnosis if there are illnesses
                if illnesses:
                    illness = random.choice(illnesses)
                    diagnosis = Diagnosis(
                        PatientID=patient_id,
                        EmpID=physician_id,
                        ConsultationDate=consult_date,
                        IllnessCode=illness.IllnessCode
                    )
                    
                    db.session.add(diagnosis)
                
                db.session.commit()
                changes_made += 1
                print(f"Added consultation and diagnosis for patient {patient_id} with physician {physician_id}")
            except Exception as e:
                db.session.rollback()
                print(f"Error adding consultation: {e}")
    
    print(f"Made {changes_made} changes to patient consultations")

def balance_patient_prescriptions():
    """Ensure all patients have at least one prescription"""
    patients = Patient.query.all()
    physicians = Physician.query.all()
    medications = Medication.query.all()
    
    print("\nBalancing patient prescriptions...")
    
    # Check if we have all required data
    if not patients:
        print("No patients found. Cannot balance prescriptions.")
        return
        
    if not physicians:
        print("No physicians found. Cannot balance prescriptions.")
        return
    
    # Skip if no medications available
    if not medications:
        print("No medications available, skipping prescription balancing")
        return
    
    # Track prescriptions per patient
    patient_prescriptions = {}
    for patient in patients:
        prescription_count = Prescription.query.filter_by(PatientID=patient.PatientID).count()
        patient_prescriptions[patient.PatientID] = prescription_count
    
    # Get patients with no prescriptions
    patients_without_prescriptions = [p.PatientID for p in patients if patient_prescriptions.get(p.PatientID, 0) == 0]
    
    # Get the maximum prescription ID
    max_prescription_id = db.session.query(db.func.max(Prescription.PrescriptionID)).scalar() or 1000
    
    # Add prescriptions for patients without any
    changes_made = 0
    for patient_id in patients_without_prescriptions:
        # Get the patient's primary physician
        patient = Patient.query.get(patient_id)
        physician_id = patient.PrimaryPhysicianID
        
        # If no primary physician, assign one
        if not physician_id and physicians:
            physician_id = random.choice(physicians).EmpID
            patient.PrimaryPhysicianID = physician_id
            db.session.flush()
            
        if physician_id and medications:
            try:
                # Select a medication
                medication = random.choice(medications)
                
                # Common dosages and frequencies
                dosages = ["10mg", "20mg", "30mg", "50mg", "100mg"]
                frequencies = ["Once daily", "Twice daily", "Three times daily", "As needed", "Every 4-6 hours"]
                
                max_prescription_id += 1
                prescription = Prescription(
                    PrescriptionID=max_prescription_id,
                    PatientID=patient_id,
                    EmpID=physician_id,
                    MedicationCode=medication.MedicationCode,
                    Dosage=random.choice(dosages),
                    Frequency=random.choice(frequencies)
                )
                
                db.session.add(prescription)
                db.session.commit()
                
                changes_made += 1
                print(f"Added prescription for patient {patient_id} with physician {physician_id} for medication {medication.MedicationName}")
            except Exception as e:
                db.session.rollback()
                print(f"Error adding prescription: {e}")
    
    print(f"Made {changes_made} changes to patient prescriptions")

if __name__ == "__main__":
    balance_relationships() 