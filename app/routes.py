# app/routes.py
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from app import db
from app.models import MedicalCorporation, Owner, Clinic, ClinicPersonnel, Physician, Nurse, Surgeon
from app.models import Patient, Inpatient, Consultation, Diagnosis, SurgerySchedule, Prescription, Medication
from app.models import Illness, Allergy, HeartRisk, SurgerySkill, NurseSkill, SurgeryType, OperatingRoom
from app.models import DrugInteraction, InteractionSeverity, Gender
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

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

#CRUD Routes for Physicians
@main.route('/physicians')
def physicians():
    """List all physicians"""
    # Removed search functionality in favor of global search
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

@main.route('/physicians/add', methods=['GET', 'POST'])
def add_physician():
    """Add a new physician"""
    if request.method == 'POST':
        try:
            # Create a new ClinicPersonnel record first
            new_personnel = ClinicPersonnel(
                Name=request.form['name'],
                Address=request.form['address'],
                Gender=Gender(request.form['gender']),
                Phone=request.form['phone'],
                SSN=request.form['ssn'],
                ClinicID=request.form['clinic_id']
            )
            
            # Add salary if provided
            if request.form.get('salary'):
                new_personnel.Salary = request.form['salary']
            
            db.session.add(new_personnel)
            db.session.flush()  # Get the EmpID for the new personnel
            
            # Create the Physician record
            new_physician = Physician(
                EmpID=new_personnel.EmpID,
                Specialty=request.form['specialty'],
                IsActive=True if request.form.get('is_active') else False,
                IsChief=True if request.form.get('is_chief') else False,
                ClinicID=request.form['clinic_id']
            )
            
            # Add percentage if provided
            if request.form.get('percentage'):
                new_physician.Percentage = request.form['percentage']
                
            # Add owner if provided
            if request.form.get('owner_id'):
                new_physician.OwnerID = request.form['owner_id']
            
            db.session.add(new_physician)
            db.session.commit()
            
            flash('Physician added successfully!', 'success')
            return redirect(url_for('main.physician_detail', id=new_physician.EmpID))
            
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Error adding physician: {str(e)}', 'danger')
    
    # GET request - render form
    clinics = Clinic.query.all()
    owners = Owner.query.all()
    return render_template('physicians/form.html', clinics=clinics, owners=owners)

@main.route('/physicians/<int:id>/edit', methods=['GET', 'POST'])
def edit_physician(id):
    """Edit an existing physician"""
    physician = Physician.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Check if status is changing from active to inactive
            status_changing = physician.IsActive and not request.form.get('is_active')
            
            # Check if chief status is changing
            chief_status_changing = physician.IsChief != bool(request.form.get('is_chief'))
            becoming_chief = not physician.IsChief and request.form.get('is_chief')
            losing_chief = physician.IsChief and not request.form.get('is_chief')
            
            # Update the physician record
            physician.Specialty = request.form['specialty']
            physician.IsActive = True if request.form.get('is_active') else False
            
            # Handle chief status change - we now allow multiple chiefs
            if becoming_chief:
                flash('Physician has been promoted to Chief Physician.', 'info')
            elif losing_chief:
                # Check if there's at least one other chief physician if this one is losing chief status
                other_chiefs = Physician.query.filter(Physician.IsChief == True, 
                                                    Physician.IsActive == True, 
                                                    Physician.EmpID != physician.EmpID).count()
                if other_chiefs == 0 and status_changing == False:  # Only validate if still active
                    flash('Warning: This is the last chief physician. Consider appointing another chief physician.', 'warning')
            
            physician.IsChief = True if request.form.get('is_chief') else False
            
            # Update percentage if provided
            if request.form.get('percentage'):
                physician.Percentage = request.form['percentage']
            else:
                physician.Percentage = None
                
            # Update owner if provided
            if request.form.get('owner_id'):
                physician.OwnerID = request.form['owner_id']
            else:
                physician.OwnerID = None
            
            # Handle status change from active to inactive
            if status_changing:
                # Find an active chief physician to reassign patients
                chief_physician = Physician.query.filter(Physician.IsChief == True, 
                                                       Physician.IsActive == True,
                                                       Physician.EmpID != physician.EmpID).first()
                
                if not chief_physician:
                    raise ValueError("Cannot deactivate physician: No other active chief physician found to reassign patients.")
                
                # Get patients for this physician
                patients = Patient.query.filter_by(PrimaryPhysicianID=physician.EmpID).all()
                
                # Reassign patients to chief physician
                for patient in patients:
                    patient.PrimaryPhysicianID = chief_physician.EmpID
                
                flash(f'{len(patients)} patients reassigned to chief physician (ID: {chief_physician.EmpID}).', 'info')
            
            db.session.commit()
            
            flash('Physician updated successfully!', 'success')
            return redirect(url_for('main.physician_detail', id=physician.EmpID))
            
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Error updating physician: {str(e)}', 'danger')
        except ValueError as e:
            db.session.rollback()
            flash(str(e), 'danger')
    
    # GET request - render form with existing data
    clinics = Clinic.query.all()
    owners = Owner.query.all()
    return render_template('physicians/form.html', physician=physician, clinics=clinics, owners=owners)

@main.route('/physicians/<int:id>/delete', methods=['POST'])
def delete_physician(id):
    """Delete a physician"""
    try:
        physician = Physician.query.get_or_404(id)
        
        # First check if this is a chief physician
        if physician.IsChief:
            flash('Cannot delete a chief physician. Please assign patients first', 'danger')
            return redirect(url_for('main.physicians'))
        
        # Get all patients first (before any reassignment attempts)
        patients = Patient.query.filter_by(PrimaryPhysicianID=id).all()
        
        # Check if the physician has patients
        if patients:
            # Try to find another physician to take over patients
            replacement = None
            
            # Try an active chief physician first
            replacement = Physician.query.filter(
                Physician.IsChief == True,
                Physician.IsActive == True,
                Physician.EmpID != physician.EmpID
            ).first()
            
            # If no chief found, try any active physician
            if not replacement:
                replacement = Physician.query.filter(
                    Physician.IsActive == True,
                    Physician.EmpID != physician.EmpID
                ).first()
            
            # Verify we have a replacement physician for patients
            if replacement:
                try:
                    # Display which physician will take over
                    flash(f'Patients will be reassigned to physician {replacement.personnel.Name} (ID: {replacement.EmpID})', 'info')
                    
                    # Explicitly reassign each patient and keep count
                    reassigned_count = 0
                    for patient in patients:
                        patient.PrimaryPhysicianID = replacement.EmpID
                        reassigned_count += 1
                    
                    # Commit the changes to ensure they're saved
                    db.session.commit()
                    
                    # Double-check after commit that patients were actually reassigned
                    remaining = Patient.query.filter_by(PrimaryPhysicianID=id).count()
                    if remaining > 0:
                        db.session.rollback()
                        flash(f'Error: Failed to reassign all patients. {remaining} patients still assigned to this physician. Please transfer all patients to another physician before deleting.', 'danger')
                        return redirect(url_for('main.physicians'))
                    
                    flash(f'Successfully reassigned {reassigned_count} patients to {replacement.personnel.Name}', 'success')
                    
                except Exception as e:
                    db.session.rollback()
                    flash(f'Error reassigning patients: {str(e)}. Please transfer all patients manually before deleting.', 'danger')
                    return redirect(url_for('main.physicians'))
            else:
                # If no replacement found, we cannot delete
                flash('Cannot delete physician: No other active physicians available to reassign patients. Please add or activate another physician first.', 'danger')
                return redirect(url_for('main.physicians'))
        
        # At this point, we should have no patients assigned to this physician
        # Handle related records that would prevent deletion
        try:
            # 1. Delete physician's consultations
            consultations = Consultation.query.filter_by(EmpID=id).all()
            for consultation in consultations:
                # Delete associated diagnoses
                diagnoses = Diagnosis.query.filter_by(
                    EmpID=id, 
                    PatientID=consultation.PatientID,
                    ConsultationDate=consultation.ConsultationDate
                ).all()
                for diagnosis in diagnoses:
                    db.session.delete(diagnosis)
                db.session.delete(consultation)
            
            # 2. Delete physician's prescriptions
            prescriptions = Prescription.query.filter_by(EmpID=id).all()
            for prescription in prescriptions:
                db.session.delete(prescription)
            
            # Final check that patients have been properly reassigned
            patients_check = Patient.query.filter_by(PrimaryPhysicianID=id).all()
            if patients_check:
                db.session.rollback()
                flash('Error: Patients still assigned to this physician. Please transfer all patients to another physician before deleting.', 'danger')
                return redirect(url_for('main.physicians'))
            
            # Now we can safely delete the physician and personnel records
            db.session.delete(physician)
            
            # Delete related personnel record
            personnel = ClinicPersonnel.query.get(id)
            if personnel:
                db.session.delete(personnel)
            
            # Commit all changes at once
            db.session.commit()
            flash('Physician deleted successfully!', 'success')
            
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Database error when deleting physician records: {str(e)}', 'danger')
            return redirect(url_for('main.physicians'))
        
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Database error deleting physician: {str(e)}', 'danger')
    except ValueError as e:
        db.session.rollback()
        flash(f'Cannot delete physician: {str(e)}', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'Unexpected error: {str(e)}', 'danger')
    
    return redirect(url_for('main.physicians'))

# API routes for AJAX calls
@main.route('/api/physicians', methods=['GET'])
def api_physicians():
    """API to get all physicians"""
    physicians = Physician.query.join(ClinicPersonnel).all()
    result = []
    
    for physician in physicians:
        result.append({
            'id': physician.EmpID,
            'name': physician.personnel.Name,
            'specialty': physician.Specialty,
            'is_active': physician.IsActive,
            'is_chief': physician.IsChief,
            'owner_id': physician.OwnerID,
            'clinic_id': physician.ClinicID
        })
    
    return jsonify(result)

@main.route('/api/physicians/<int:id>', methods=['GET'])
def api_physician_detail(id):
    """API to get a specific physician"""
    physician = Physician.query.get_or_404(id)
    
    result = {
        'id': physician.EmpID,
        'name': physician.personnel.Name,
        'specialty': physician.Specialty,
        'is_active': physician.IsActive,
        'is_chief': physician.IsChief,
        'owner_id': physician.OwnerID,
        'clinic_id': physician.ClinicID,
        'address': physician.personnel.Address,
        'gender': physician.personnel.Gender.value,
        'phone': physician.personnel.Phone,
        'ssn': physician.personnel.SSN,
        'salary': float(physician.personnel.Salary) if physician.personnel.Salary else None,
        'percentage': float(physician.Percentage) if physician.Percentage else None
    }
    
    return jsonify(result)


# Patient routes
@main.route('/patients')
def patients():
    """List all patients"""
    # Removed search functionality in favor of global search
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

@main.route('/patients/add', methods=['GET', 'POST'])
def add_patient():
    """Add a new patient"""
    if request.method == 'POST':
        try:
            # Create the new patient record
            new_patient = Patient(
                Name=request.form['name'],
                SSN=request.form['ssn'],
                Gender=Gender(request.form['gender']),
                DOB=datetime.strptime(request.form['dob'], '%Y-%m-%d').date(),
                Phone=request.form['phone'],
                Address=request.form['address'],
                PrimaryPhysicianID=request.form['primary_physician_id'],
                IsInpatient=True if request.form.get('is_inpatient') else False,
                IsEmployee=True if request.form.get('is_employee') else False
            )
            
            # Add optional fields if provided
            if request.form.get('blood_type'):
                new_patient.BloodType = request.form['blood_type']
            
            if request.form.get('allergy_code'):
                new_patient.AllergyCode = request.form['allergy_code']
                
            if request.form.get('hdl') and request.form['hdl'].strip():
                new_patient.HDL = float(request.form['hdl'])
                
            if request.form.get('ldl') and request.form['ldl'].strip():
                new_patient.LDL = float(request.form['ldl'])
                
            if request.form.get('triglyceride') and request.form['triglyceride'].strip():
                new_patient.Triglyceride = float(request.form['triglyceride'])
                
            if request.form.get('blood_sugar') and request.form['blood_sugar'].strip():
                new_patient.BloodSugar = float(request.form['blood_sugar'])
                
            # If employee is checked, assign EmpID
            if new_patient.IsEmployee and request.form.get('emp_id'):
                new_patient.EmpID = request.form['emp_id']
            
            # Calculate heart risk if values are provided
            if new_patient.HDL and new_patient.LDL and new_patient.Triglyceride:
                new_patient.HeartRiskLevel = new_patient.calculate_heart_risk()
            
            db.session.add(new_patient)
            db.session.commit()
            
            flash('Patient added successfully!', 'success')
            return redirect(url_for('main.patient_detail', id=new_patient.PatientID))
            
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Database error adding patient: {str(e)}', 'danger')
        except ValueError as e:
            db.session.rollback()
            flash(f'Error adding patient: {str(e)}', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Unexpected error: {str(e)}', 'danger')
    
    # GET request - render form with needed data
    physicians = Physician.query.filter_by(IsActive=True).all()
    allergies = Allergy.query.all()
    
    return render_template('patients/form.html', 
                          physicians=physicians,
                          allergies=allergies)

@main.route('/patients/<int:id>/edit', methods=['GET', 'POST'])
def edit_patient(id):
    """Edit an existing patient"""
    patient = Patient.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Update patient information
            patient.Name = request.form['name']
            patient.SSN = request.form['ssn']
            patient.Gender = Gender(request.form['gender'])
            patient.DOB = datetime.strptime(request.form['dob'], '%Y-%m-%d').date()
            patient.Phone = request.form['phone']
            patient.Address = request.form['address']
            patient.PrimaryPhysicianID = request.form['primary_physician_id']
            patient.IsInpatient = True if request.form.get('is_inpatient') else False
            patient.IsEmployee = True if request.form.get('is_employee') else False
            
            # Update optional fields
            patient.BloodType = request.form['blood_type'] if request.form.get('blood_type') else None
            patient.AllergyCode = request.form['allergy_code'] if request.form.get('allergy_code') else None
            
            # Update cholesterol values
            if request.form.get('hdl') and request.form['hdl'].strip():
                patient.HDL = float(request.form['hdl'])
            else:
                patient.HDL = None
                
            if request.form.get('ldl') and request.form['ldl'].strip():
                patient.LDL = float(request.form['ldl'])
            else:
                patient.LDL = None
                
            if request.form.get('triglyceride') and request.form['triglyceride'].strip():
                patient.Triglyceride = float(request.form['triglyceride'])
            else:
                patient.Triglyceride = None
                
            if request.form.get('blood_sugar') and request.form['blood_sugar'].strip():
                patient.BloodSugar = float(request.form['blood_sugar'])
            else:
                patient.BloodSugar = None
                
            # Update employee ID if applicable
            if patient.IsEmployee and request.form.get('emp_id'):
                patient.EmpID = request.form['emp_id']
            else:
                patient.EmpID = None
            
            # Handle inpatient status change - would need additional logic for bed assignment
            if patient.IsInpatient and not patient.inpatient:
                flash('Note: Patient marked as inpatient. Please assign a bed in the inpatient management section.', 'warning')
            
            # Calculate heart risk based on cholesterol values
            if patient.HDL and patient.LDL and patient.Triglyceride:
                patient.HeartRiskLevel = patient.calculate_heart_risk()
            else:
                patient.HeartRiskLevel = None
            
            db.session.commit()
            
            flash('Patient updated successfully!', 'success')
            return redirect(url_for('main.patient_detail', id=patient.PatientID))
            
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Database error updating patient: {str(e)}', 'danger')
        except ValueError as e:
            db.session.rollback()
            flash(f'Error updating patient: {str(e)}', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Unexpected error: {str(e)}', 'danger')
    
    # GET request - render form with existing data
    physicians = Physician.query.filter_by(IsActive=True).all()
    allergies = Allergy.query.all()
    
    return render_template('patients/form.html', 
                          patient=patient,
                          physicians=physicians,
                          allergies=allergies)

@main.route('/inpatients')
def inpatients():
    """List all inpatients"""
    inpatients = Inpatient.query.join(Patient).all()
    return render_template('patients/inpatients.html', inpatients=inpatients)

# Nurse routes
@main.route('/nurses')
def nurses():
    """List all nurses"""
    # Removed search functionality in favor of global search
    nurses = Nurse.query.join(ClinicPersonnel).all()
    return render_template('nurses/index.html', nurses=nurses)

@main.route('/nurses/<int:id>')
def nurse_detail(id):
    """Show nurse details, skills, and assigned patients"""
    nurse = Nurse.query.get_or_404(id)
    
    skills = NurseSkill.query.filter_by(EmpID=id).all()
    inpatients = Inpatient.query.filter_by(EmpID=id).all()
    
    return render_template('nurses/detail.html',
                          nurse=nurse,
                          skills=skills,
                          inpatients=inpatients)

@main.route('/nurses/add', methods=['GET', 'POST'])
def add_nurse():
    """Add a new nurse"""
    if request.method == 'POST':
        try:
            # Create a new ClinicPersonnel record first
            new_personnel = ClinicPersonnel(
                Name=request.form['name'],
                Address=request.form['address'],
                Gender=Gender[request.form['gender'].upper()],
                Phone=request.form['phone'],
                SSN=request.form['ssn'],
                ClinicID=request.form['clinic_id']
            )
            
            # Add salary if provided
            if request.form.get('salary'):
                new_personnel.Salary = request.form['salary']
            
            db.session.add(new_personnel)
            db.session.flush()  # This assigns the ID without committing
            
            # Create a new Nurse record
            new_nurse = Nurse(
                EmpID=new_personnel.EmpID,
                YearsOfExperience=request.form['years_of_experience'],
                Grade=request.form['grade'],
                NursingUnits=request.form['nursing_units']
            )
            
            # Add surgery type if provided
            if request.form.get('surgery_type_code'):
                new_nurse.SurgeryTypeCode = request.form['surgery_type_code']
            
            # We need to temporarily disable the inpatient validation since a new nurse
            # won't have any inpatients assigned yet
            # Set a flag to bypass validation in the event listener
            setattr(new_nurse, '_skip_inpatient_check', True)
            
            db.session.add(new_nurse)
            db.session.commit()
            
            flash('Nurse added successfully! Please assign at least 5 inpatients to this nurse.', 'success')
            return redirect(url_for('main.nurse_detail', id=new_nurse.EmpID))
            
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Error adding nurse: {str(e)}', 'danger')
            
    # GET request - render form
    clinics = Clinic.query.all()
    surgery_types = SurgeryType.query.all()
    return render_template('nurses/form.html', clinics=clinics, surgery_types=surgery_types)

@main.route('/nurses/<int:id>/edit', methods=['GET', 'POST'])
def edit_nurse(id):
    """Edit an existing nurse"""
    nurse = Nurse.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Update nurse record
            nurse.YearsOfExperience = request.form['years_of_experience']
            nurse.Grade = request.form['grade']
            nurse.NursingUnits = request.form['nursing_units']
            
            # Update surgery type if provided
            if request.form.get('surgery_type_code'):
                nurse.SurgeryTypeCode = request.form['surgery_type_code']
            else:
                nurse.SurgeryTypeCode = None
                
            db.session.commit()
            
            flash('Nurse updated successfully!', 'success')
            return redirect(url_for('main.nurse_detail', id=nurse.EmpID))
            
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Error updating nurse: {str(e)}', 'danger')
        except ValueError as e:
            db.session.rollback()
            flash(str(e), 'danger')
    
    # GET request - render form with existing data
    surgery_types = SurgeryType.query.all()
    return render_template('nurses/form.html', nurse=nurse, surgery_types=surgery_types)

@main.route('/nurses/<int:id>/delete', methods=['POST'])
def delete_nurse(id):
    """Delete a nurse"""
    try:
        nurse = Nurse.query.get_or_404(id)
        
        # Check if the nurse has inpatients
        inpatients = Inpatient.query.filter_by(EmpID=id).all()
        
        if inpatients:
            # Find another nurse to take over inpatients
            replacement = Nurse.query.filter(Nurse.EmpID != nurse.EmpID).first()
            
            if replacement:
                try:
                    # Display which nurse will take over
                    flash(f'Inpatients will be reassigned to nurse {replacement.personnel.Name} (ID: {replacement.EmpID})', 'info')
                    
                    # Reassign each inpatient
                    for inpatient in inpatients:
                        inpatient.EmpID = replacement.EmpID
                    
                    # Commit the changes to ensure they're saved
                    db.session.commit()
                    
                    # Double-check after commit that inpatients were actually reassigned
                    remaining = Inpatient.query.filter_by(EmpID=id).count()
                    if remaining > 0:
                        db.session.rollback()
                        flash(f'Error: Failed to reassign all inpatients. {remaining} inpatients still assigned to this nurse.', 'danger')
                        return redirect(url_for('main.nurses'))
                    
                    flash(f'Successfully reassigned {len(inpatients)} inpatients to {replacement.personnel.Name}', 'success')
                    
                except Exception as e:
                    db.session.rollback()
                    flash(f'Error reassigning inpatients: {str(e)}.', 'danger')
                    return redirect(url_for('main.nurses'))
            else:
                # If no replacement found, we cannot delete
                flash('Cannot delete nurse: No other nurses available to reassign inpatients. Please add another nurse first.', 'danger')
                return redirect(url_for('main.nurses'))
        
        # Delete related NurseSkill records
        NurseSkill.query.filter_by(EmpID=id).delete()
        
        # Now delete the nurse record
        db.session.delete(nurse)
        
        # Delete the ClinicPersonnel record
        personnel = ClinicPersonnel.query.get(id)
        if personnel:
            db.session.delete(personnel)
        
        db.session.commit()
        flash('Nurse deleted successfully!', 'success')
        
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Error deleting nurse: {str(e)}', 'danger')
        
    return redirect(url_for('main.nurses'))

# Surgeon routes
@main.route('/surgeons')
def surgeons():
    """List all surgeons"""
    # Removed search functionality in favor of global search
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

@main.route('/surgeons/add', methods=['GET', 'POST'])
def add_surgeon():
    """Add a new surgeon"""
    if request.method == 'POST':
        try:
            # Create a new ClinicPersonnel record first
            new_personnel = ClinicPersonnel(
                Name=request.form['name'],
                Address=request.form['address'],
                Gender=Gender[request.form['gender'].upper()],
                Phone=request.form['phone'],
                SSN=request.form['ssn'],
                ClinicID=request.form['clinic_id']
            )
            
            # Add salary if provided
            if request.form.get('salary'):
                new_personnel.Salary = request.form['salary']
            
            db.session.add(new_personnel)
            db.session.flush()  # This assigns the ID without committing
            
            # Create a new Surgeon record
            new_surgeon = Surgeon(
                EmpID=new_personnel.EmpID,
                Specialty=request.form['specialty'],
                ContractType=request.form['contract_type'],
                ContractLength=request.form['contract_length'],
                IsActive=True if request.form.get('is_active') else False
            )
            
            db.session.add(new_surgeon)
            db.session.commit()
            
            flash('Surgeon added successfully!', 'success')
            return redirect(url_for('main.surgeon_detail', id=new_surgeon.EmpID))
            
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Error adding surgeon: {str(e)}', 'danger')
            
    # GET request - render form
    clinics = Clinic.query.all()
    return render_template('surgeons/form.html', clinics=clinics)

@main.route('/surgeons/<int:id>/edit', methods=['GET', 'POST'])
def edit_surgeon(id):
    """Edit an existing surgeon"""
    surgeon = Surgeon.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Update surgeon record
            surgeon.Specialty = request.form['specialty']
            surgeon.ContractType = request.form['contract_type']
            surgeon.ContractLength = request.form['contract_length']
            surgeon.IsActive = True if request.form.get('is_active') else False
            
            db.session.commit()
            
            flash('Surgeon updated successfully!', 'success')
            return redirect(url_for('main.surgeon_detail', id=surgeon.EmpID))
            
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Error updating surgeon: {str(e)}', 'danger')
        except ValueError as e:
            db.session.rollback()
            flash(str(e), 'danger')
    
    # GET request - render form with existing data
    return render_template('surgeons/form.html', surgeon=surgeon)

@main.route('/surgeons/<int:id>/toggle-status', methods=['POST'])
def toggle_surgeon_status(id):
    """Toggle the active status of a surgeon"""
    try:
        surgeon = Surgeon.query.get_or_404(id)
        
        # Toggle the active status
        surgeon.IsActive = not surgeon.IsActive
        
        # If deactivating, check for scheduled surgeries to warn the user
        if not surgeon.IsActive and surgeon.surgery_schedules:
            warning_message = f'Surgeon deactivated, but has {len(surgeon.surgery_schedules)} scheduled surgeries that may need attention.'
            flash(warning_message, 'warning')
        else:
            status_message = 'activated' if surgeon.IsActive else 'deactivated'
            flash(f'Surgeon {status_message} successfully!', 'success')
        
        db.session.commit()
        
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Error changing surgeon status: {str(e)}', 'danger')
        
    return redirect(url_for('main.surgeon_detail', id=id))

@main.route('/surgeons/<int:id>/delete', methods=['POST'])
def delete_surgeon(id):
    """
    This function is kept for historical records but is no longer in use.
    The system now uses the toggle_surgeon_status function instead of deleting surgeons,
    to maintain data integrity and preserve historical surgery records.
    
    Surgeons can be marked as inactive rather than being deleted.
    """
    # The legacy code is kept for reference but not used
    try:
        surgeon = Surgeon.query.get_or_404(id)
        
        # Check if the surgeon has scheduled surgeries
        surgeries = SurgerySchedule.query.filter_by(EmpID=id).all()
        
        if surgeries:
            flash('Cannot delete surgeon with scheduled surgeries. Please reassign or complete all surgeries first.', 'danger')
            return redirect(url_for('main.surgeon_detail', id=id))
        
        # Now we can safely delete the surgeon record
        db.session.delete(surgeon)
        
        # Delete the ClinicPersonnel record
        personnel = ClinicPersonnel.query.get(id)
        if personnel:
            db.session.delete(personnel)
        
        db.session.commit()
        flash('Surgeon deleted successfully!', 'success')
        
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Error deleting surgeon: {str(e)}', 'danger')
        
    return redirect(url_for('main.surgeons'))

# Surgery routes
@main.route('/surgery-schedules')
def surgery_schedules():
    """List all surgery schedules"""
    surgeries = SurgerySchedule.query.order_by(SurgerySchedule.Date).all()
    return render_template('surgeries/index.html', surgeries=surgeries)

@main.route('/surgery-schedules/add', methods=['GET', 'POST'])
def add_surgery_schedule():
    """Add a new surgery schedule"""
    # Get data needed for the form
    patients = Patient.query.order_by(Patient.Name).all()
    surgeons = Surgeon.query.filter_by(IsActive=True).join(ClinicPersonnel).order_by(ClinicPersonnel.Name).all()
    surgery_types = SurgeryType.query.order_by(SurgeryType.Name).all()
    operating_rooms = OperatingRoom.query.all()
    
    if request.method == 'POST':
        try:
            # Create new surgery schedule
            new_surgery = SurgerySchedule(
                PatientID=request.form['patient_id'],
                EmpID=request.form['surgeon_id'],
                Date=datetime.strptime(request.form['date'], '%Y-%m-%d').date(),
                SurgeryCode=request.form['surgery_code'],
                OpRoomID=request.form['op_room_id']
            )
            
            db.session.add(new_surgery)
            db.session.commit()
            
            flash('Surgery scheduled successfully!', 'success')
            return redirect(url_for('main.surgery_schedules'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error scheduling surgery: {str(e)}', 'danger')
    
    return render_template('surgeries/form.html', 
                          patients=patients,
                          surgeons=surgeons,
                          surgery_types=surgery_types,
                          operating_rooms=operating_rooms)

@main.route('/surgery-schedules/<int:id>/edit', methods=['GET', 'POST'])
def edit_surgery_schedule(id):
    """Edit an existing surgery schedule"""
    surgery = SurgerySchedule.query.get_or_404(id)
    
    # Get data needed for the form
    patients = Patient.query.order_by(Patient.Name).all()
    surgeons = Surgeon.query.join(ClinicPersonnel).order_by(ClinicPersonnel.Name).all()
    surgery_types = SurgeryType.query.order_by(SurgeryType.Name).all()
    operating_rooms = OperatingRoom.query.all()
    
    if request.method == 'POST':
        try:
            # Update surgery schedule
            surgery.PatientID = request.form['patient_id']
            surgery.EmpID = request.form['surgeon_id']
            surgery.Date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
            surgery.SurgeryCode = request.form['surgery_code']
            surgery.OpRoomID = request.form['op_room_id']
            
            db.session.commit()
            
            flash('Surgery schedule updated successfully!', 'success')
            return redirect(url_for('main.surgery_schedules'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating surgery schedule: {str(e)}', 'danger')
    
    return render_template('surgeries/form.html', 
                          surgery=surgery,
                          patients=patients,
                          surgeons=surgeons,
                          surgery_types=surgery_types,
                          operating_rooms=operating_rooms)

@main.route('/surgery-schedules/<int:id>/delete', methods=['POST'])
def delete_surgery_schedule(id):
    """Delete a surgery schedule"""
    surgery = SurgerySchedule.query.get_or_404(id)
    
    try:
        db.session.delete(surgery)
        db.session.commit()
        
        flash('Surgery schedule deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting surgery schedule: {str(e)}', 'danger')
    
    return redirect(url_for('main.surgery_schedules'))

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

@main.route('/surgery-types/<string:code>/schedule', methods=['GET', 'POST'])
def add_surgery_schedule_for_type(code):
    """Add a new surgery schedule for a specific surgery type"""
    surgery_type = SurgeryType.query.get_or_404(code)
    
    # Get data needed for the form
    patients = Patient.query.order_by(Patient.Name).all()
    surgeons = Surgeon.query.filter_by(IsActive=True).join(ClinicPersonnel).order_by(ClinicPersonnel.Name).all()
    surgery_types = SurgeryType.query.order_by(SurgeryType.Name).all()
    operating_rooms = OperatingRoom.query.all()
    
    if request.method == 'POST':
        try:
            # Create new surgery schedule
            new_surgery = SurgerySchedule(
                PatientID=request.form['patient_id'],
                EmpID=request.form['surgeon_id'],
                Date=datetime.strptime(request.form['date'], '%Y-%m-%d').date(),
                SurgeryCode=request.form['surgery_code'],
                OpRoomID=request.form['op_room_id']
            )
            
            db.session.add(new_surgery)
            db.session.commit()
            
            flash('Surgery scheduled successfully!', 'success')
            return redirect(url_for('main.surgery_type_detail', code=code))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error scheduling surgery: {str(e)}', 'danger')
    
    return render_template('surgeries/form.html', 
                          patients=patients,
                          surgeons=surgeons,
                          surgery_types=surgery_types,
                          operating_rooms=operating_rooms,
                          selected_surgery_type=code)

@main.route('/surgeons/<int:id>/schedule', methods=['GET', 'POST'])
def add_surgery_schedule_for_surgeon(id):
    """Add a new surgery schedule for a specific surgeon"""
    surgeon = Surgeon.query.get_or_404(id)
    
    # Verify that surgeon is active
    if not surgeon.IsActive:
        flash('Cannot schedule surgery for inactive surgeon.', 'danger')
        return redirect(url_for('main.surgeon_detail', id=id))
    
    # Get data needed for the form
    patients = Patient.query.order_by(Patient.Name).all()
    surgeons = Surgeon.query.filter_by(IsActive=True).join(ClinicPersonnel).order_by(ClinicPersonnel.Name).all()
    surgery_types = SurgeryType.query.order_by(SurgeryType.Name).all()
    operating_rooms = OperatingRoom.query.all()
    
    if request.method == 'POST':
        try:
            # Create new surgery schedule
            new_surgery = SurgerySchedule(
                PatientID=request.form['patient_id'],
                EmpID=request.form['surgeon_id'],
                Date=datetime.strptime(request.form['date'], '%Y-%m-%d').date(),
                SurgeryCode=request.form['surgery_code'],
                OpRoomID=request.form['op_room_id']
            )
            
            db.session.add(new_surgery)
            db.session.commit()
            
            flash('Surgery scheduled successfully!', 'success')
            return redirect(url_for('main.surgeon_detail', id=id))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error scheduling surgery: {str(e)}', 'danger')
    
    return render_template('surgeries/form.html', 
                          patients=patients,
                          surgeons=surgeons,
                          surgery_types=surgery_types,
                          operating_rooms=operating_rooms,
                          selected_surgeon_id=id)

# Medication routes
@main.route('/medications')
def medications():
    """List all medications and inventory"""
    # Removed search functionality in favor of global search
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

@main.route('/medications/add', methods=['GET', 'POST'])
def add_medication():
    """Add a new medication"""
    if request.method == 'POST':
        try:
            # Get form data
            medication_code = request.form['medication_code'].strip()
            medication_name = request.form['medication_name'].strip()
            quantity_on_hand = int(request.form['quantity_on_hand'])
            quantity_on_order = int(request.form['quantity_on_order'])
            unit_cost = float(request.form['unit_cost'])
            ytd_usage = int(request.form['ytd_usage'])
            
            # Validate input
            if not medication_code:
                raise ValueError("Medication code is required")
            
            if not medication_name:
                raise ValueError("Medication name is required")
            
            # Check if medication code already exists
            existing_medication = Medication.query.filter_by(MedicationCode=medication_code).first()
            if existing_medication:
                raise ValueError(f"Medication with code {medication_code} already exists")
            
            # Create new medication
            new_medication = Medication(
                MedicationCode=medication_code,
                MedicationName=medication_name,
                QuantityOnHand=quantity_on_hand,
                QuantityOnOrder=quantity_on_order,
                UnitCost=unit_cost,
                YearToDateUsage=ytd_usage
            )
            
            db.session.add(new_medication)
            db.session.commit()
            
            flash('Medication added successfully!', 'success')
            return redirect(url_for('main.medication_detail', code=new_medication.MedicationCode))
            
        except ValueError as e:
            db.session.rollback()
            flash(str(e), 'danger')
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Database error: {str(e)}', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Unexpected error: {str(e)}', 'danger')
    
    # GET request - render the form
    return render_template('medications/form.html')

@main.route('/medications/<string:code>/edit', methods=['GET', 'POST'])
def edit_medication(code):
    """Edit an existing medication"""
    medication = Medication.query.get_or_404(code)
    
    if request.method == 'POST':
        try:
            # Get form data
            medication_name = request.form['medication_name'].strip()
            quantity_on_hand = int(request.form['quantity_on_hand'])
            quantity_on_order = int(request.form['quantity_on_order'])
            unit_cost = float(request.form['unit_cost'])
            ytd_usage = int(request.form['ytd_usage'])
            
            # Validate input
            if not medication_name:
                raise ValueError("Medication name is required")
            
            # Update medication
            medication.MedicationName = medication_name
            medication.QuantityOnHand = quantity_on_hand
            medication.QuantityOnOrder = quantity_on_order
            medication.UnitCost = unit_cost
            medication.YearToDateUsage = ytd_usage
            
            db.session.commit()
            
            flash('Medication updated successfully!', 'success')
            return redirect(url_for('main.medication_detail', code=medication.MedicationCode))
            
        except ValueError as e:
            db.session.rollback()
            flash(str(e), 'danger')
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Database error: {str(e)}', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Unexpected error: {str(e)}', 'danger')
    
    # GET request - render form with existing data
    return render_template('medications/form.html', medication=medication)

@main.route('/medications/<string:code>/delete', methods=['POST'])
def delete_medication(code):
    """Delete a medication"""
    medication = Medication.query.get_or_404(code)
    
    try:
        # Check for related prescriptions
        prescriptions = Prescription.query.filter_by(MedicationCode=code).all()
        
        # Check for drug interactions
        interactions = DrugInteraction.query.filter(
            (DrugInteraction.Medication1 == code) | 
            (DrugInteraction.Medication2 == code)
        ).all()
        
        # Delete related records first (if cascading is not set up in model)
        for prescription in prescriptions:
            db.session.delete(prescription)
        
        for interaction in interactions:
            db.session.delete(interaction)
        
        # Delete the medication
        db.session.delete(medication)
        db.session.commit()
        
        flash('Medication deleted successfully!', 'success')
        return redirect(url_for('main.medications'))
        
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Database error: {str(e)}', 'danger')
        return redirect(url_for('main.medication_detail', code=code))
    except Exception as e:
        db.session.rollback()
        flash(f'Unexpected error: {str(e)}', 'danger')
        return redirect(url_for('main.medication_detail', code=code))

# Consultation routes
@main.route('/consultations')
def consultations():
    """List all consultations"""
    # Removed search functionality in favor of global search
    consultations = Consultation.query.order_by(Consultation.ConsultationDate.desc()).all()
    return render_template('consultations/index.html', consultations=consultations)

@main.route('/consultations/add', methods=['GET', 'POST'])
def add_consultation():
    """Add a new consultation with diagnoses"""
    if request.method == 'POST':
        try:
            # Get form data
            patient_id = int(request.form['patient_id'])
            physician_id = int(request.form['physician_id'])
            consultation_date = datetime.strptime(request.form['consultation_date'], '%Y-%m-%d').date()
            notes = request.form.get('notes', '')
            
            # Get selected illnesses
            illness_codes = request.form.getlist('illnesses[]')
            
            # Validate that the patient exists
            patient = Patient.query.get(patient_id)
            if not patient:
                raise ValueError("Selected patient does not exist")
            
            # Validate that the physician exists and is active
            physician = Physician.query.filter_by(EmpID=physician_id, IsActive=True).first()
            if not physician:
                raise ValueError("Selected physician does not exist or is inactive")
            
            # Validate that at least one illness is selected
            if not illness_codes:
                raise ValueError("At least one diagnosis (illness) must be selected")
            
            # Create a new consultation
            new_consultation = Consultation(
                PatientID=patient_id,
                EmpID=physician_id,
                ConsultationDate=consultation_date
            )
            
            # Add a Notes field if your model has one
            if hasattr(Consultation, 'Notes'):
                new_consultation.Notes = notes
            
            db.session.add(new_consultation)
            db.session.flush()  # Get the ConsultationID
            
            # Create diagnoses records for each selected illness
            for illness_code in illness_codes:
                new_diagnosis = Diagnosis(
                    PatientID=patient_id,
                    EmpID=physician_id,
                    ConsultationDate=consultation_date,
                    IllnessCode=illness_code
                )
                db.session.add(new_diagnosis)
            
            db.session.commit()
            
            flash('Consultation added successfully!', 'success')
            return redirect(url_for('main.consultation_detail', id=new_consultation.ConsultationID))
            
        except ValueError as e:
            db.session.rollback()
            flash(str(e), 'danger')
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Database error: {str(e)}', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Unexpected error: {str(e)}', 'danger')
    
    # GET request - render the form
    patients = Patient.query.all()
    physicians = Physician.query.filter_by(IsActive=True).all()
    illnesses = Illness.query.all()
    
    return render_template(
        'consultations/form.html',
        patients=patients,
        physicians=physicians,
        illnesses=illnesses,
        can_change_patient=True,
        can_change_physician=True,
        can_change_date=True
    )

@main.route('/consultations/<int:id>/edit', methods=['GET', 'POST'])
def edit_consultation(id):
    """Edit an existing consultation and its diagnoses"""
    consultation = Consultation.query.get_or_404(id)
    
    # Get existing diagnoses for this consultation
    existing_diagnoses = Diagnosis.query.filter_by(
        PatientID=consultation.PatientID,
        EmpID=consultation.EmpID,
        ConsultationDate=consultation.ConsultationDate
    ).all()
    
    # Get list of illness codes for existing diagnoses
    diagnosed_illnesses = [diagnosis.IllnessCode for diagnosis in existing_diagnoses]
    
    if request.method == 'POST':
        try:
            # For existing consultations, we don't change the patient, physician, or date
            # These form key identifying relationships in the diagnosis records
            
            # Update notes if the model has this field
            if hasattr(Consultation, 'Notes'):
                consultation.Notes = request.form.get('notes', '')
            
            # Get selected illnesses from the form
            new_illness_codes = request.form.getlist('illnesses[]')
            
            # Validate that at least one illness is selected
            if not new_illness_codes:
                raise ValueError("At least one diagnosis (illness) must be selected")
            
            # Remove diagnoses that are no longer selected
            for diagnosis in existing_diagnoses:
                if diagnosis.IllnessCode not in new_illness_codes:
                    db.session.delete(diagnosis)
            
            # Add new diagnoses that weren't previously selected
            for illness_code in new_illness_codes:
                if illness_code not in diagnosed_illnesses:
                    new_diagnosis = Diagnosis(
                        PatientID=consultation.PatientID,
                        EmpID=consultation.EmpID,
                        ConsultationDate=consultation.ConsultationDate,
                        IllnessCode=illness_code
                    )
                    db.session.add(new_diagnosis)
            
            db.session.commit()
            
            flash('Consultation updated successfully!', 'success')
            return redirect(url_for('main.consultation_detail', id=consultation.ConsultationID))
            
        except ValueError as e:
            db.session.rollback()
            flash(str(e), 'danger')
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Database error: {str(e)}', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Unexpected error: {str(e)}', 'danger')
    
    # GET request - render form with existing data
    patients = Patient.query.all()
    physicians = Physician.query.all()
    illnesses = Illness.query.all()
    
    return render_template(
        'consultations/form.html',
        consultation=consultation,
        patients=patients,
        physicians=physicians,
        illnesses=illnesses,
        diagnosed_illnesses=diagnosed_illnesses,
        can_change_patient=False,  # Cannot change patient for existing consultation
        can_change_physician=False,  # Cannot change physician for existing consultation
        can_change_date=False  # Cannot change date for existing consultation
    )

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

@main.route('/prescriptions/add', methods=['GET', 'POST'])
def add_prescription():
    """Add a new prescription"""
    if request.method == 'POST':
        try:
            # Get form data
            patient_id = int(request.form['patient_id'])
            physician_id = int(request.form['physician_id'])
            medication_code = request.form['medication_code'].strip()
            dosage = request.form['dosage'].strip()
            frequency = request.form['frequency'].strip()
            
            # Validate that required fields are not empty
            if not dosage:
                raise ValueError("Dosage is required")
            
            if not frequency:
                raise ValueError("Frequency is required")
            
            # Verify that patient, physician and medication exist
            patient = Patient.query.get(patient_id)
            if not patient:
                raise ValueError("Selected patient does not exist")
                
            physician = Physician.query.get(physician_id)
            if not physician:
                raise ValueError("Selected physician does not exist")
                
            medication = Medication.query.get(medication_code)
            if not medication:
                raise ValueError("Selected medication does not exist")
            
            # Check if this patient already has a prescription for this medication
            existing_prescription = Prescription.query.filter_by(
                PatientID=patient_id,
                MedicationCode=medication_code
            ).first()
            
            if existing_prescription:
                raise ValueError(f"Patient already has a prescription for {medication.MedicationName}. Please edit the existing prescription instead.")
            
            # Create new prescription
            new_prescription = Prescription(
                PatientID=patient_id,
                EmpID=physician_id,
                MedicationCode=medication_code,
                Dosage=dosage,
                Frequency=frequency
            )
            
            # Increment the medication's YearToDateUsage
            medication.YearToDateUsage += 1
            
            # If medication is getting low in stock, show a warning
            if medication.QuantityOnHand <= 20:
                flash(f"Warning: {medication.MedicationName} is running low on stock ({medication.QuantityOnHand} remaining).", 'warning')
            
            db.session.add(new_prescription)
            db.session.commit()
            
            # Check for potential drug interactions
            interactions = DrugInteraction.query.filter(
                ((DrugInteraction.Medication1 == medication_code) | 
                (DrugInteraction.Medication2 == medication_code)) &
                (DrugInteraction.Severity.in_(['S', 'M']))  # Severe or Moderate
            ).all()
            
            # Get other medications this patient is taking
            patient_medications = Prescription.query.filter(
                Prescription.PatientID == patient_id,
                Prescription.MedicationCode != medication_code
            ).all()
            
            # Check for interactions with patient's other medications
            potential_interactions = []
            for interaction in interactions:
                other_med_code = interaction.Medication2 if interaction.Medication1 == medication_code else interaction.Medication1
                for patient_med in patient_medications:
                    if patient_med.MedicationCode == other_med_code:
                        other_med = Medication.query.get(other_med_code)
                        potential_interactions.append({
                            'medication': other_med.MedicationName,
                            'severity': "Severe" if interaction.Severity == 'S' else "Moderate"
                        })
            
            # Show warning if there are potential interactions
            if potential_interactions:
                interaction_message = "Potential drug interactions detected: "
                for interaction in potential_interactions:
                    interaction_message += f"{interaction['medication']} ({interaction['severity']}), "
                flash(interaction_message[:-2], 'warning')
            
            flash('Prescription added successfully!', 'success')
            return redirect(url_for('main.prescription_detail', id=new_prescription.PrescriptionID))
            
        except ValueError as e:
            db.session.rollback()
            flash(str(e), 'danger')
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Database error: {str(e)}', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Unexpected error: {str(e)}', 'danger')
    
    # GET request - render the form
    patients = Patient.query.order_by(Patient.Name).all()
    physicians = Physician.query.filter_by(IsActive=True).join(ClinicPersonnel).order_by(ClinicPersonnel.Name).all()
    medications = Medication.query.order_by(Medication.MedicationName).all()
    
    # Check for pre-selected values (when coming from patient or physician page)
    selected_patient_id = request.args.get('patient_id', type=int)
    selected_physician_id = request.args.get('physician_id', type=int)
    selected_medication_code = request.args.get('medication_code')
    
    return render_template('prescriptions/form.html',
                          patients=patients,
                          physicians=physicians,
                          medications=medications,
                          selected_patient_id=selected_patient_id,
                          selected_physician_id=selected_physician_id,
                          selected_medication_code=selected_medication_code)

@main.route('/prescriptions/<int:id>/edit', methods=['GET', 'POST'])
def edit_prescription(id):
    """Edit an existing prescription"""
    prescription = Prescription.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Get form data
            # For security, get IDs from hidden inputs if the selects are disabled
            patient_id = int(request.form['patient_id'])
            physician_id = int(request.form['physician_id'])
            medication_code = request.form['medication_code']
            dosage = request.form['dosage'].strip()
            frequency = request.form['frequency'].strip()
            
            # Validate that required fields are not empty
            if not dosage:
                raise ValueError("Dosage is required")
            
            if not frequency:
                raise ValueError("Frequency is required")
            
            # Verify the patient, physician, and medication haven't changed
            if patient_id != prescription.PatientID:
                raise ValueError("Patient cannot be changed for an existing prescription")
                
            if physician_id != prescription.EmpID:
                raise ValueError("Physician cannot be changed for an existing prescription")
                
            if medication_code != prescription.MedicationCode:
                raise ValueError("Medication cannot be changed for an existing prescription")
            
            # Update prescription
            prescription.Dosage = dosage
            prescription.Frequency = frequency
            
            db.session.commit()
            
            flash('Prescription updated successfully!', 'success')
            return redirect(url_for('main.prescription_detail', id=prescription.PrescriptionID))
            
        except ValueError as e:
            db.session.rollback()
            flash(str(e), 'danger')
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Database error: {str(e)}', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Unexpected error: {str(e)}', 'danger')
    
    # GET request - render form with existing data
    patients = Patient.query.order_by(Patient.Name).all()
    physicians = Physician.query.join(ClinicPersonnel).order_by(ClinicPersonnel.Name).all()
    medications = Medication.query.order_by(Medication.MedicationName).all()
    
    return render_template('prescriptions/form.html',
                          prescription=prescription,
                          patients=patients,
                          physicians=physicians,
                          medications=medications)

@main.route('/prescriptions/<int:id>/delete', methods=['POST'])
def delete_prescription(id):
    """Delete a prescription"""
    prescription = Prescription.query.get_or_404(id)
    
    try:
        # Get medication details for confirmation message
        medication_name = prescription.medication.MedicationName
        patient_name = prescription.patient.Name
        
        # Delete the prescription
        db.session.delete(prescription)
        db.session.commit()
        
        flash(f'Prescription for {medication_name} for patient {patient_name} deleted successfully!', 'success')
        return redirect(url_for('main.prescriptions'))
        
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Database error: {str(e)}', 'danger')
        return redirect(url_for('main.prescription_detail', id=id))
    except Exception as e:
        db.session.rollback()
        flash(f'Unexpected error: {str(e)}', 'danger')
        return redirect(url_for('main.prescription_detail', id=id))

# Add a patient-specific route to create prescriptions directly from patient detail page
@main.route('/patients/<int:id>/prescribe', methods=['GET', 'POST'])
def add_prescription_for_patient(id):
    """Add a new prescription for a specific patient"""
    patient = Patient.query.get_or_404(id)
    
    if request.method == 'POST':
        # Process the form submission similar to add_prescription
        # but with patient_id already set
        try:
            # Get form data
            physician_id = int(request.form['physician_id'])
            medication_code = request.form['medication_code'].strip()
            dosage = request.form['dosage'].strip()
            frequency = request.form['frequency'].strip()
            
            # Validate and create prescription (similar to add_prescription)
            # ...
            
            # Create new prescription
            new_prescription = Prescription(
                PatientID=id,  # Use the patient ID from the route parameter
                EmpID=physician_id,
                MedicationCode=medication_code,
                Dosage=dosage,
                Frequency=frequency
            )
            
            # Increment the medication's YearToDateUsage
            medication = Medication.query.get(medication_code)
            medication.YearToDateUsage += 1
            
            db.session.add(new_prescription)
            db.session.commit()
            
            flash('Prescription added successfully!', 'success')
            return redirect(url_for('main.patient_detail', id=id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    # Redirect to the main add_prescription form with patient_id pre-selected
    return redirect(url_for('main.add_prescription', patient_id=id))

# Add a physician-specific route to create prescriptions directly from physician detail page
@main.route('/physicians/<int:id>/prescribe', methods=['GET'])
def add_prescription_by_physician(id):
    """Add a new prescription by a specific physician"""
    physician = Physician.query.get_or_404(id)
    
    # Redirect to the main add_prescription form with physician_id pre-selected
    return redirect(url_for('main.add_prescription', physician_id=id))

# Add a medication-specific route to create prescriptions for a specific medication
@main.route('/medications/<string:code>/prescribe', methods=['GET'])
def add_prescription_for_medication(code):
    """Add a new prescription for a specific medication"""
    medication = Medication.query.get_or_404(code)
    
    # Redirect to the main add_prescription form with medication_code pre-selected
    return redirect(url_for('main.add_prescription', medication_code=code))

# Add a global search function
@main.route('/search')
def global_search():
    """Global search across all major entities"""
    search_query = request.args.get('search', '')
    search_type = request.args.get('type', 'all')  # Default to searching all
    
    # If empty search, just show the search form
    if not search_query:
        return render_template('search_results.html', 
                            search_query='',
                            search_type=search_type,
                            results={})
    
    # Prepare search terms - original query and a version with wildcards
    search_term = f"%{search_query}%"
    
    # Direct ID search takes priority - for exact numeric matches
    if search_query.isdigit():
        query_id = int(search_query)
        
        # Check for direct ID matches in different entity types
        if search_type in ['all', 'physicians']:
            physician = Physician.query.get(query_id)
            if physician:
                return redirect(url_for('main.physician_detail', id=query_id))
        
        if search_type in ['all', 'patients']:
            patient = Patient.query.get(query_id)
            if patient:
                return redirect(url_for('main.patient_detail', id=query_id))
        
        if search_type in ['all', 'consultations']:
            consultation = Consultation.query.get(query_id)
            if consultation:
                return redirect(url_for('main.consultation_detail', id=query_id))
                
        if search_type in ['all', 'nurses']:
            nurse = Nurse.query.get(query_id)
            if nurse:
                return redirect(url_for('main.nurse_detail', id=query_id))
        
        if search_type in ['all', 'surgeons']:
            surgeon = Surgeon.query.get(query_id)
            if surgeon:
                return redirect(url_for('main.surgeon_detail', id=query_id))
                
        if search_type in ['all', 'prescriptions']:
            prescription = Prescription.query.get(query_id)
            if prescription:
                return redirect(url_for('main.prescription_detail', id=query_id))
    
    # String-based searches for codes/exact matches in non-numeric IDs            
    if search_type in ['all', 'medications']:
        # Try exact code match for medications
        medication = Medication.query.filter(
            (Medication.MedicationCode == search_query) | 
            (Medication.MedicationName.ilike(search_query))
        ).first()
        if medication:
            return redirect(url_for('main.medication_detail', code=medication.MedicationCode))
    
    if search_type in ['all', 'surgery-types']:
        surgery_type = SurgeryType.query.filter(
            (SurgeryType.SurgeryCode == search_query) |
            (SurgeryType.Name.ilike(search_query))
        ).first()
        if surgery_type:
            return redirect(url_for('main.surgery_type_detail', code=surgery_type.SurgeryCode))
    
    # Collect search results for display
    results = {}
    
    # Search physicians
    if search_type in ['all', 'physicians']:
        physicians = Physician.query.join(ClinicPersonnel).filter(
            (ClinicPersonnel.Name.ilike(search_term)) |
            (Physician.Specialty.ilike(search_term)) |
            (ClinicPersonnel.Phone.ilike(search_term)) |
            (ClinicPersonnel.Address.ilike(search_term)) |
            (Physician.EmpID == search_query if search_query.isdigit() else False)
        ).all()
        
        if physicians:
            # If exact name match and only one result, redirect
            for physician in physicians:
                if physician.personnel.Name.lower() == search_query.lower():
                    if len(physicians) == 1:
                        return redirect(url_for('main.physician_detail', id=physician.EmpID))
            
            results['physicians'] = physicians
    
    # Search patients with expanded criteria
    if search_type in ['all', 'patients']:
        patients = Patient.query.filter(
            (Patient.Name.ilike(search_term)) |
            (Patient.PatientID == search_query if search_query.isdigit() else False) |
            (Patient.SSN.ilike(search_term)) |
            (Patient.Phone.ilike(search_term)) |
            (Patient.Address.ilike(search_term)) |
            (Patient.DOB.ilike(search_term) if not search_query.isdigit() else False)
        ).all()
        
        if patients:
            # If exact name match and only one result, redirect
            for patient in patients:
                if patient.Name.lower() == search_query.lower():
                    if len(patients) == 1:
                        return redirect(url_for('main.patient_detail', id=patient.PatientID))
            
            results['patients'] = patients
    
    # Search nurses with expanded criteria
    if search_type in ['all', 'nurses']:
        nurses = Nurse.query.join(ClinicPersonnel).filter(
            (ClinicPersonnel.Name.ilike(search_term)) |
            (ClinicPersonnel.Phone.ilike(search_term)) |
            (ClinicPersonnel.Address.ilike(search_term)) |
            (Nurse.Grade.ilike(search_term)) |
            (Nurse.NursingUnits.ilike(search_term)) |
            (Nurse.EmpID == search_query if search_query.isdigit() else False)
        ).all()
        
        if nurses:
            # If exact name match and only one result, redirect
            for nurse in nurses:
                if nurse.personnel.Name.lower() == search_query.lower():
                    if len(nurses) == 1:
                        return redirect(url_for('main.nurse_detail', id=nurse.EmpID))
            
            results['nurses'] = nurses
    
    # Search surgeons with expanded criteria
    if search_type in ['all', 'surgeons']:
        surgeons = Surgeon.query.join(ClinicPersonnel).filter(
            (ClinicPersonnel.Name.ilike(search_term)) |
            (ClinicPersonnel.Phone.ilike(search_term)) |
            (ClinicPersonnel.Address.ilike(search_term)) |
            (Surgeon.Specialty.ilike(search_term)) |
            (Surgeon.ContractType.ilike(search_term)) |
            (Surgeon.EmpID == search_query if search_query.isdigit() else False)
        ).all()
        
        if surgeons:
            # If exact name match and only one result, redirect
            for surgeon in surgeons:
                if surgeon.personnel.Name.lower() == search_query.lower():
                    if len(surgeons) == 1:
                        return redirect(url_for('main.surgeon_detail', id=surgeon.EmpID))
                        
            results['surgeons'] = surgeons
    
    # Search consultations (including by notes if available)
    if search_type in ['all', 'consultations']:
        consultations = []
        
        # Always try to get consultations by ID fields
        id_matches = []
        if search_query.isdigit():
            id_matches = Consultation.query.filter(
                (Consultation.ConsultationID == search_query) |
                (Consultation.PatientID == search_query) |
                (Consultation.EmpID == search_query)
            ).all()
        
        # Additionally, let's join with related tables to search by patient or physician name
        name_matches = Consultation.query\
            .join(Patient, Consultation.PatientID == Patient.PatientID)\
            .join(Physician, Consultation.EmpID == Physician.EmpID)\
            .join(ClinicPersonnel, Physician.EmpID == ClinicPersonnel.EmpID)\
            .filter(
                (Patient.Name.ilike(search_term)) |
                (ClinicPersonnel.Name.ilike(search_term))
            ).all()
        
        # Also try to search by date if the search query looks like a date
        date_matches = []
        try:
            # Try to parse the date in common formats
            search_date = datetime.strptime(search_query, '%Y-%m-%d').date()
            date_matches = Consultation.query.filter(Consultation.ConsultationDate == search_date).all()
        except ValueError:
            # Not a valid date format, try other formats
            try:
                search_date = datetime.strptime(search_query, '%m/%d/%Y').date()
                date_matches = Consultation.query.filter(Consultation.ConsultationDate == search_date).all()
            except ValueError:
                # Not a valid date format in second format either, just continue
                pass
        
        # Add all matches to the consultations list
        if id_matches:
            consultations.extend(id_matches)
        if name_matches:
            for consultation in name_matches:
                if consultation not in consultations:
                    consultations.append(consultation)
        if date_matches:
            for consultation in date_matches:
                if consultation not in consultations:
                    consultations.append(consultation)
            
        # Add any with matching notes if the model has a Notes field
        try:
            notes_matches = Consultation.query.filter(
                Consultation.Notes.ilike(search_term)
            ).all()
            
            if notes_matches:
                for consultation in notes_matches:
                    if consultation not in consultations:
                        consultations.append(consultation)
        except:
            # If Notes column doesn't exist, just continue
            pass
        
        if consultations:
            # If only one consultation found, redirect to its details page
            if len(consultations) == 1:
                return redirect(url_for('main.consultation_detail', id=consultations[0].ConsultationID))
                
            results['consultations'] = consultations
    
    # Search medications with expanded criteria
    if search_type in ['all', 'medications']:
        medications = Medication.query.filter(
            (Medication.MedicationCode.ilike(search_term)) |
            (Medication.MedicationName.ilike(search_term)) |
            (Medication.UnitCost == float(search_query) if search_query.replace('.', '', 1).isdigit() else False)
        ).all()
        
        if medications:
            # If exact name match and only one result, redirect
            for medication in medications:
                if medication.MedicationName.lower() == search_query.lower():
                    if len(medications) == 1:
                        return redirect(url_for('main.medication_detail', code=medication.MedicationCode))
            
            results['medications'] = medications
    
    # Search prescriptions
    if search_type in ['all', 'prescriptions']:
        # Try to join with related tables to get more comprehensive results
        prescriptions = Prescription.query\
            .join(Patient, Prescription.PatientID == Patient.PatientID)\
            .join(Physician, Prescription.EmpID == Physician.EmpID)\
            .join(Medication, Prescription.MedicationCode == Medication.MedicationCode)\
            .join(ClinicPersonnel, Physician.EmpID == ClinicPersonnel.EmpID)\
            .filter(
                (Prescription.PrescriptionID == search_query if search_query.isdigit() else False) |
                (Patient.Name.ilike(search_term)) |
                (ClinicPersonnel.Name.ilike(search_term)) |
                (Medication.MedicationName.ilike(search_term)) |
                (Prescription.Dosage.ilike(search_term)) |
                (Prescription.Frequency.ilike(search_term))
            ).all()
        
        if prescriptions:
            # If only one prescription, redirect directly
            if len(prescriptions) == 1:
                return redirect(url_for('main.prescription_detail', id=prescriptions[0].PrescriptionID))
                
            results['prescriptions'] = prescriptions
    
    # If we have no results at all 
    if not results:
        flash(f'No results found for "{search_query}". Try a different search term or category.', 'info')
    
    # Render the search results page with all collected results
    return render_template('search_results.html', 
                          search_query=search_query,
                          search_type=search_type,
                          results=results)
