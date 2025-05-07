# app/routes.py
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from app import db
from app.models import MedicalCorporation, Owner, Clinic, ClinicPersonnel, Physician, Nurse, Surgeon
from app.models import Patient, Inpatient, Consultation, Diagnosis, SurgerySchedule, Prescription, Medication
from app.models import Illness, Allergy, HeartRisk, SurgerySkill, NurseSkill, SurgeryType, OperatingRoom
from app.models import DrugInteraction, InteractionSeverity

main = Blueprint('main', __name__)

@main.route('/')
def home():
    """Home page with system overview and navigation"""
    # Count statistics for dashboard
    stats = {
        'physicians': Physician.query.count(),
        'nurses': Nurse.query.count(),
        'surgeons': Surgeon.query.count(),
        'patients': Patient.query.count(),
        'inpatients': Inpatient.query.count(),
        'consultations': Consultation.query.count(),
        'prescriptions': Prescription.query.count(),
        'surgeries': SurgerySchedule.query.count()
    }
    return render_template('home.html', stats=stats)

# Physician routes
@main.route('/physicians')
def physicians():
    """List all physicians"""
    physicians = Physician.query.join(ClinicPersonnel).all()
    return render_template('physicians/index.html', physicians=physicians)

@main.route('/physicians/<int:id>')
def physician_detail(id):
    """Show physician details and their patients"""
    physician = Physician.query.get_or_404(id)
    patients = Patient.query.filter_by(PrimaryPhysicianID=id).all()
    consultations = Consultation.query.filter_by(EmpID=id).all()
    prescriptions = Prescription.query.filter_by(EmpID=id).all()
    
    return render_template('physicians/detail.html', 
                          physician=physician, 
                          patients=patients,
                          consultations=consultations,
                          prescriptions=prescriptions)

# Patient routes
@main.route('/patients')
def patients():
    """List all patients"""
    patients = Patient.query.all()
    return render_template('patients/index.html', patients=patients)

@main.route('/patients/<int:id>')
def patient_detail(id):
    """Show patient details, medical history, and treatments"""
    patient = Patient.query.get_or_404(id)
    consultations = Consultation.query.filter_by(PatientID=id).order_by(Consultation.ConsultationDate.desc()).all()
    prescriptions = Prescription.query.filter_by(PatientID=id).all()
    diagnoses = Diagnosis.query.filter_by(PatientID=id).all()
    surgeries = SurgerySchedule.query.filter_by(PatientID=id).all()
    
    # Calculate heart risk if not already calculated
    if patient.HeartRiskLevel is None and patient.HDL and patient.LDL and patient.Triglyceride:
        patient.HeartRiskLevel = patient.calculate_heart_risk()
        db.session.commit()
    
    return render_template('patients/detail.html', 
                          patient=patient,
                          consultations=consultations,
                          prescriptions=prescriptions,
                          diagnoses=diagnoses,
                          surgeries=surgeries)

@main.route('/inpatients')
def inpatients():
    """List all inpatients"""
    inpatients = Inpatient.query.join(Patient).all()
    return render_template('patients/inpatients.html', inpatients=inpatients)

# Nurse routes
@main.route('/nurses')
def nurses():
    """List all nurses"""
    nurses = Nurse.query.join(ClinicPersonnel).all()
    return render_template('nurses/index.html', nurses=nurses)

@main.route('/nurses/<int:id>')
def nurse_detail(id):
    """Show nurse details, skills, and assigned patients"""
    nurse = Nurse.query.get_or_404(id)
    inpatients = Inpatient.query.filter_by(EmpID=id).all()
    skills = NurseSkill.query.filter_by(EmpID=id).all()
    
    return render_template('nurses/detail.html', 
                          nurse=nurse,
                          inpatients=inpatients,
                          skills=skills)

# Surgeon routes
@main.route('/surgeons')
def surgeons():
    """List all surgeons"""
    surgeons = Surgeon.query.join(ClinicPersonnel).all()
    return render_template('surgeons/index.html', surgeons=surgeons)

@main.route('/surgeons/<int:id>')
def surgeon_detail(id):
    """Show surgeon details and their scheduled surgeries"""
    surgeon = Surgeon.query.get_or_404(id)
    surgeries = SurgerySchedule.query.filter_by(EmpID=id).order_by(SurgerySchedule.Date).all()
    
    # Group surgeries by type for statistics
    surgery_types = {}
    for surgery in surgeries:
        surgery_type = surgery.surgery_type.Name
        if surgery_type in surgery_types:
            surgery_types[surgery_type] += 1
        else:
            surgery_types[surgery_type] = 1
    
    return render_template('surgeons/detail.html', 
                          surgeon=surgeon,
                          surgeries=surgeries,
                          surgery_types=surgery_types)

# Surgery routes
@main.route('/surgery-schedules')
def surgery_schedules():
    """List all surgery schedules"""
    surgeries = SurgerySchedule.query.order_by(SurgerySchedule.Date).all()
    return render_template('surgeries/index.html', surgeries=surgeries)

@main.route('/surgery-types')
def surgery_types():
    """List all surgery types"""
    types = SurgeryType.query.all()
    return render_template('surgeries/types.html', types=types)

@main.route('/surgery-types/<string:code>')
def surgery_type_detail(code):
    """Show surgery type details, required skills, and scheduled surgeries"""
    surgery_type = SurgeryType.query.get_or_404(code)
    skills = SurgerySkill.query.filter_by(SurgeryCode=code).all()
    surgeries = SurgerySchedule.query.filter_by(SurgeryCode=code).order_by(SurgerySchedule.Date).all()
    nurses = Nurse.query.filter_by(SurgeryTypeCode=code).all()
    
    return render_template('surgeries/type_detail.html', 
                          surgery_type=surgery_type,
                          skills=skills,
                          surgeries=surgeries,
                          nurses=nurses)

# Medication routes
@main.route('/medications')
def medications():
    """List all medications and inventory"""
    medications = Medication.query.all()
    return render_template('medications/index.html', medications=medications)

@main.route('/medications/<string:code>')
def medication_detail(code):
    """Show medication details, usage, and interactions"""
    medication = Medication.query.get_or_404(code)
    prescriptions = Prescription.query.filter_by(MedicationCode=code).all()
    
    # Get drug interactions
    interactions = DrugInteraction.query.filter(
        (DrugInteraction.Medication1 == code) | 
        (DrugInteraction.Medication2 == code)
    ).all()
    
    # Get related medications from interactions
    related_medications = []
    for interaction in interactions:
        if interaction.Medication1 == code:
            related_medications.append({
                'medication': Medication.query.get(interaction.Medication2),
                'severity': interaction.Severity
            })
        else:
            related_medications.append({
                'medication': Medication.query.get(interaction.Medication1),
                'severity': interaction.Severity
            })
    
    return render_template('medications/detail.html', 
                          medication=medication,
                          prescriptions=prescriptions,
                          interactions=interactions,
                          related_medications=related_medications)

# Consultation routes
@main.route('/consultations')
def consultations():
    """List all consultations"""
    consultations = Consultation.query.order_by(Consultation.ConsultationDate.desc()).all()
    return render_template('consultations/index.html', consultations=consultations)

@main.route('/consultations/<int:id>')
def consultation_detail(id):
    """Show consultation details and associated diagnoses"""
    consultation = Consultation.query.get_or_404(id)
    diagnoses = Diagnosis.query.filter_by(
        PatientID=consultation.PatientID,
        EmpID=consultation.EmpID,
        ConsultationDate=consultation.ConsultationDate
    ).all()
    
    # Get related prescriptions that might have been given during this consultation
    prescriptions = Prescription.query.filter_by(
        PatientID=consultation.PatientID,
        EmpID=consultation.EmpID
    ).all()
    
    return render_template('consultations/detail.html', 
                          consultation=consultation,
                          diagnoses=diagnoses,
                          prescriptions=prescriptions)

# Prescription routes
@main.route('/prescriptions')
def prescriptions():
    """List all prescriptions"""
    prescriptions = Prescription.query.all()
    return render_template('prescriptions/index.html', prescriptions=prescriptions)

@main.route('/prescriptions/<int:id>')
def prescription_detail(id):
    """Show prescription details"""
    prescription = Prescription.query.get_or_404(id)
    # Get drug interactions for the prescribed medication
    interactions = DrugInteraction.query.filter(
        (DrugInteraction.Medication1 == prescription.MedicationCode) | 
        (DrugInteraction.Medication2 == prescription.MedicationCode)
    ).all()
    
    # Get related medications from interactions
    related_medications = []
    for interaction in interactions:
        if interaction.Medication1 == prescription.MedicationCode:
            related_medications.append({
                'medication': Medication.query.get(interaction.Medication2),
                'severity': interaction.Severity
            })
        else:
            related_medications.append({
                'medication': Medication.query.get(interaction.Medication1),
                'severity': interaction.Severity
            })
    
    return render_template('prescriptions/detail.html', 
                          prescription=prescription,
                          interactions=interactions,
                          related_medications=related_medications)
