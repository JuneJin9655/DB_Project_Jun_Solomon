from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, validates
from sqlalchemy import CheckConstraint, event, func, Enum
import enum
from app import db

# Define enum types
class Gender(enum.Enum):
    MALE = 'male'
    FEMALE = 'female'

class SurgeryCategory(enum.Enum):
    HOSPITALIZATION = 'H'
    OUTPATIENT = 'O'

class InteractionSeverity(enum.Enum):
    SEVERE = 'S'
    MODERATE = 'M'
    LITTLE = 'L'
    NONE = 'N'

class HeartRisk(enum.Enum):
    NONE = 'N'
    LOW = 'L'
    MODERATE = 'M'
    HIGH = 'H'

class Wing(enum.Enum):
    BLUE = 'Blue'
    GREEN = 'Green'

class BedLabel(enum.Enum):
    A = 'A'
    B = 'B'

class MedicalCorporation(db.Model):
    __tablename__ = 'MedicalCorporation'
    CorpName = db.Column(db.String(100), primary_key=True)
    OwnerID = db.Column(db.Integer, db.ForeignKey('Owner.OwnerID'), primary_key=True)
    ClinicID = db.Column(db.Integer, db.ForeignKey('Clinic.ClinicID'), primary_key=True)
    Percentage = db.Column(db.Numeric(5, 2), nullable=False)
    CorpHeadquarters = db.Column(db.String(255), nullable=False)
    
    # Validate percentage between 0-100
    __table_args__ = (
        CheckConstraint('Percentage >= 0 AND Percentage <= 100', name='check_corp_percentage'),
    )
    
    # Relationships
    owner = relationship("Owner", back_populates="medical_corporations")
    clinic = relationship("Clinic", back_populates="medical_corporations")

class Owner(db.Model):
    __tablename__ = 'Owner'
    OwnerID = db.Column(db.Integer, primary_key=True)
    Percentage = db.Column(db.Numeric(5, 2), nullable=False)
    
    # Validate percentage between 0-100
    __table_args__ = (
        CheckConstraint('Percentage >= 0 AND Percentage <= 100', name='check_owner_percentage'),
    )
    
    # Relationships
    medical_corporations = relationship("MedicalCorporation", back_populates="owner")
    physicians = relationship("Physician", back_populates="owner")

class Clinic(db.Model):
    __tablename__ = 'Clinic'
    ClinicID = db.Column(db.Integer, primary_key=True)
    ClinicName = db.Column(db.String(100), nullable=False)
    Address = db.Column(db.Text, nullable=False)
    
    # Relationships
    personnel = relationship("ClinicPersonnel", back_populates="clinic")
    medical_corporations = relationship("MedicalCorporation", back_populates="clinic")

class ClinicPersonnel(db.Model):
    __tablename__ = 'ClinicPersonnel'
    EmpID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False)
    Address = db.Column(db.Text, nullable=False)
    Gender = db.Column(db.Enum(Gender), nullable=False)
    Phone = db.Column(db.String(20), nullable=False)
    Salary = db.Column(db.Numeric(10, 2), nullable=True)  # Can be null as some salaries may be missing
    SSN = db.Column(db.String(20), nullable=False, unique=True)
    ClinicID = db.Column(db.Integer, db.ForeignKey('Clinic.ClinicID'), nullable=False)
    
    # Salary range validation
    __table_args__ = (
        CheckConstraint('Salary IS NULL OR (Salary >= 25000 AND Salary <= 300000)', name='check_salary_range'),
    )
    
    # Relationships
    clinic = relationship("Clinic", back_populates="personnel")
    physician = relationship("Physician", uselist=False, back_populates="personnel")
    nurse = relationship("Nurse", uselist=False, back_populates="personnel")
    surgeon = relationship("Surgeon", uselist=False, back_populates="personnel")
    patient = relationship("Patient", back_populates="employee", foreign_keys="Patient.EmpID")

class Physician(db.Model):
    __tablename__ = 'Physician'
    EmpID = db.Column(db.Integer, db.ForeignKey('ClinicPersonnel.EmpID'), primary_key=True)
    Percentage = db.Column(db.Numeric(5, 2))
    Specialty = db.Column(db.String(100), nullable=False)
    IsActive = db.Column(db.Boolean, default=True)
    IsChief = db.Column(db.Boolean, default=False)
    OwnerID = db.Column(db.Integer, db.ForeignKey('Owner.OwnerID'))
    ClinicID = db.Column(db.Integer, db.ForeignKey('Clinic.ClinicID'), nullable=False)
    
    # Validate percentage between 0-100
    __table_args__ = (
        CheckConstraint('Percentage IS NULL OR (Percentage >= 0 AND Percentage <= 100)', name='check_physician_percentage'),
    )
    
    # Relationships
    personnel = relationship("ClinicPersonnel", back_populates="physician")
    owner = relationship("Owner", back_populates="physicians")
    consultations = relationship("Consultation", back_populates="physician")
    prescriptions = relationship("Prescription", back_populates="physician")
    diagnoses = relationship("Diagnosis", back_populates="physician")
    patients = relationship("Patient", back_populates="primary_physician", foreign_keys="Patient.PrimaryPhysicianID")
    
    @validates('patients')
    def validate_patients(self, key, patient):
        # Validate that a physician has no more than 20 patients
        if len(self.patients) >= 20:
            raise ValueError("A physician cannot have more than 20 patients")
        return patient

class Nurse(db.Model):
    __tablename__ = 'Nurse'
    EmpID = db.Column(db.Integer, db.ForeignKey('ClinicPersonnel.EmpID'), primary_key=True)
    YearsOfExperience = db.Column(db.Integer)
    Grade = db.Column(db.String(20))
    NursingUnits = db.Column(db.String(100))
    SurgeryTypeCode = db.Column(db.String(20), db.ForeignKey('SurgeryType.SurgeryCode'), nullable=True)
    
    # Relationships
    personnel = relationship("ClinicPersonnel", back_populates="nurse")
    inpatients = relationship("Inpatient", back_populates="nurse")
    surgery_type = relationship("SurgeryType", back_populates="assigned_nurses")
    skills = relationship("NurseSkill", back_populates="nurse")
    
    @validates('inpatients')
    def validate_inpatients(self, key, inpatient):
        # Skip validation if the _skip_inpatient_check flag is set
        if hasattr(self, '_skip_inpatient_check') and self._skip_inpatient_check:
            return inpatient
            
        # Validate that a nurse attends to at least 5 inpatients
        if len(self.inpatients) < 5:
            raise ValueError("A nurse must attend to at least 5 inpatients")
        return inpatient

# Association table for Nurse-SurgerySkill many-to-many relationship
class NurseSkill(db.Model):
    __tablename__ = 'NurseSkill'
    EmpID = db.Column(db.Integer, db.ForeignKey('Nurse.EmpID'), primary_key=True)
    SkillCode = db.Column(db.String(20), db.ForeignKey('SurgerySkill.SkillCode'), primary_key=True)
    
    # Relationships
    nurse = relationship("Nurse", back_populates="skills")
    skill = relationship("SurgerySkill", back_populates="nurses")

class Surgeon(db.Model):
    __tablename__ = 'Surgeon'
    EmpID = db.Column(db.Integer, db.ForeignKey('ClinicPersonnel.EmpID'), primary_key=True)
    ContractLength = db.Column(db.Integer, nullable=False)
    ContractType = db.Column(db.String(50), nullable=False)
    Specialty = db.Column(db.String(100), nullable=False)
    IsActive = db.Column(db.Boolean, default=True)
    
    # Relationships
    personnel = relationship("ClinicPersonnel", back_populates="surgeon")
    surgery_schedules = relationship("SurgerySchedule", back_populates="surgeon")

class SurgerySkill(db.Model):
    __tablename__ = 'SurgerySkill'
    SkillCode = db.Column(db.String(20), primary_key=True)
    Description = db.Column(db.Text)
    SurgeryCode = db.Column(db.String(20), db.ForeignKey('SurgeryType.SurgeryCode'))
    
    # Relationships
    surgery_type = relationship("SurgeryType", back_populates="skills")
    nurses = relationship("NurseSkill", back_populates="skill")

class SurgeryType(db.Model):
    __tablename__ = 'SurgeryType'
    SurgeryCode = db.Column(db.String(20), primary_key=True)
    Name = db.Column(db.String(100), nullable=False)
    Category = db.Column(db.Enum(SurgeryCategory), nullable=False)
    AnatomicalLocation = db.Column(db.String(100))
    SpecialNeeds = db.Column(db.Text)
    
    # Relationships
    skills = relationship("SurgerySkill", back_populates="surgery_type")
    surgery_schedules = relationship("SurgerySchedule", back_populates="surgery_type")
    assigned_nurses = relationship("Nurse", back_populates="surgery_type")
    
    @validates('assigned_nurses')
    def validate_nurses(self, key, nurse):
        # Validate that each surgery type has at least 2 nurses
        if len(self.assigned_nurses) < 2:
            raise ValueError("Each surgery type must have at least 2 nurses")
        return nurse

class Patient(db.Model):
    __tablename__ = 'Patient'
    PatientID = db.Column(db.Integer, primary_key=True)
    SSN = db.Column(db.String(20), nullable=False, unique=True)
    Name = db.Column(db.String(100), nullable=False)
    Gender = db.Column(db.Enum(Gender), nullable=False)
    Phone = db.Column(db.String(20), nullable=False)
    DOB = db.Column(db.Date, nullable=False)
    Address = db.Column(db.Text, nullable=False)
    BloodType = db.Column(db.String(5))
    HDL = db.Column(db.Float)
    LDL = db.Column(db.Float)
    Triglyceride = db.Column(db.Float)
    BloodSugar = db.Column(db.Float)
    AllergyCode = db.Column(db.String(20), db.ForeignKey('Allergy.AllergyCode'))
    IsInpatient = db.Column(db.Boolean, default=False)
    IsEmployee = db.Column(db.Boolean, default=False)
    EmpID = db.Column(db.Integer, db.ForeignKey('ClinicPersonnel.EmpID'))
    PrimaryPhysicianID = db.Column(db.Integer, db.ForeignKey('Physician.EmpID'), nullable=False)
    HeartRiskLevel = db.Column(db.Enum(HeartRisk))
    
    # Relationships
    employee = relationship("ClinicPersonnel", back_populates="patient", foreign_keys=[EmpID])
    primary_physician = relationship("Physician", back_populates="patients", foreign_keys=[PrimaryPhysicianID])
    allergy = relationship("Allergy", back_populates="patients")
    inpatient = relationship("Inpatient", back_populates="patient", uselist=False)
    consultations = relationship("Consultation", back_populates="patient")
    prescriptions = relationship("Prescription", back_populates="patient")
    diagnoses = relationship("Diagnosis", back_populates="patient")
    surgery_schedules = relationship("SurgerySchedule", back_populates="patient")
    
    # Calculate total cholesterol and heart risk
    def calculate_total_cholesterol(self):
        if self.HDL is None or self.LDL is None or self.Triglyceride is None:
            return None
        return self.HDL + self.LDL + (self.Triglyceride / 5)
    
    def calculate_heart_risk(self):
        if self.HDL is None or self.HDL == 0:
            return None
        
        total_cholesterol = self.calculate_total_cholesterol()
        if total_cholesterol is None:
            return None
        
        ratio = total_cholesterol / self.HDL
        
        if ratio < 4:
            return HeartRisk.NONE
        elif ratio <= 5:
            return HeartRisk.LOW
        else:
            return HeartRisk.MODERATE

class Bed(db.Model):
    __tablename__ = 'Bed'
    PatientRoomID = db.Column(db.Integer, primary_key=True)
    BedLabel = db.Column(db.Enum(BedLabel), primary_key=True)
    RoomNum = db.Column(db.String(10), nullable=False)
    Unit = db.Column(db.String(50), nullable=False)
    Wing = db.Column(db.Enum(Wing), nullable=False)
    
    # Create a unique index for the composite primary key
    __table_args__ = (
        db.UniqueConstraint('PatientRoomID', 'BedLabel', name='unique_bed_pk'),
    )
    
    # Relationships
    inpatient = relationship("Inpatient", back_populates="bed", uselist=False)

class Inpatient(db.Model):
    __tablename__ = 'Inpatient'
    PatientID = db.Column(db.Integer, db.ForeignKey('Patient.PatientID'), primary_key=True)
    NursingUnits = db.Column(db.String(100))
    PatientRoomID = db.Column(db.Integer, primary_key=True)
    BedLabel = db.Column(db.Enum(BedLabel), primary_key=True)
    EmpID = db.Column(db.Integer, db.ForeignKey('Nurse.EmpID'))
    AdmissionDate = db.Column(db.Date, nullable=False)
    
    # Validate nursing units between 1-7
    __table_args__ = (
        CheckConstraint('NursingUnits >= 1 AND NursingUnits <= 7', name='check_nursing_units'),
        db.ForeignKeyConstraint(
            ['PatientRoomID', 'BedLabel'],
            ['Bed.PatientRoomID', 'Bed.BedLabel'],
            name='fk_bed_inpatient'
        )
    )
    
    # Relationships
    patient = relationship("Patient", back_populates="inpatient")
    bed = relationship("Bed", back_populates="inpatient")
    nurse = relationship("Nurse", back_populates="inpatients")

class Consultation(db.Model):
    __tablename__ = 'Consultation'
    ConsultationID = db.Column(db.Integer, primary_key=True)
    PatientID = db.Column(db.Integer, db.ForeignKey('Patient.PatientID'), nullable=False)
    EmpID = db.Column(db.Integer, db.ForeignKey('Physician.EmpID'), nullable=False)
    ConsultationDate = db.Column(db.Date, nullable=False)
    Notes = db.Column(db.Text, nullable=True)
    
    # Relationships
    patient = relationship("Patient", back_populates="consultations", overlaps="diagnoses")
    physician = relationship("Physician", back_populates="consultations", overlaps="diagnoses")
    diagnoses = relationship("Diagnosis", 
                           back_populates="consultation",
                           overlaps="patient,physician",
                           foreign_keys="[Diagnosis.PatientID, Diagnosis.EmpID, Diagnosis.ConsultationDate]",
                           primaryjoin="and_(Consultation.PatientID==Diagnosis.PatientID, "
                                     "Consultation.EmpID==Diagnosis.EmpID, "
                                     "Consultation.ConsultationDate==Diagnosis.ConsultationDate)")

class Diagnosis(db.Model):
    __tablename__ = 'Diagnosis'
    PatientID = db.Column(db.Integer, db.ForeignKey('Patient.PatientID'), primary_key=True)
    EmpID = db.Column(db.Integer, db.ForeignKey('Physician.EmpID'), primary_key=True)
    ConsultationDate = db.Column(db.Date, primary_key=True)
    IllnessCode = db.Column(db.String(20), db.ForeignKey('Illness.IllnessCode'), nullable=False)
    AllergyCode = db.Column(db.String(20), db.ForeignKey('Allergy.AllergyCode'))
    
    # Relationships
    patient = relationship("Patient", back_populates="diagnoses", overlaps="consultations")
    physician = relationship("Physician", back_populates="diagnoses", overlaps="consultations")
    illness = relationship("Illness", back_populates="diagnoses")
    allergy = relationship("Allergy", back_populates="diagnoses")
    consultation = relationship("Consultation", 
                              back_populates="diagnoses",
                              overlaps="patient,physician",
                              foreign_keys="[Diagnosis.PatientID, Diagnosis.EmpID, Diagnosis.ConsultationDate]",
                              primaryjoin="and_(Diagnosis.PatientID==Consultation.PatientID, "
                                        "Diagnosis.EmpID==Consultation.EmpID, "
                                        "Diagnosis.ConsultationDate==Consultation.ConsultationDate)")

class SurgerySchedule(db.Model):
    __tablename__ = 'SurgerySchedule'
    ScheduleID = db.Column(db.Integer, primary_key=True)
    PatientID = db.Column(db.Integer, db.ForeignKey('Patient.PatientID'), nullable=False)
    EmpID = db.Column(db.Integer, db.ForeignKey('Surgeon.EmpID'), nullable=False)
    Date = db.Column(db.Date, nullable=False)
    SurgeryCode = db.Column(db.String(20), db.ForeignKey('SurgeryType.SurgeryCode'), nullable=False)
    OpRoomID = db.Column(db.Integer, db.ForeignKey('OperatingRoom.OpRoomID'), nullable=False)
    
    # Relationships
    patient = relationship("Patient", back_populates="surgery_schedules")
    surgeon = relationship("Surgeon", back_populates="surgery_schedules")
    surgery_type = relationship("SurgeryType", back_populates="surgery_schedules")
    operating_room = relationship("OperatingRoom", back_populates="surgery_schedules")

class Prescription(db.Model):
    __tablename__ = 'Prescription'
    PrescriptionID = db.Column(db.Integer, primary_key=True)
    Dosage = db.Column(db.String(100), nullable=False)
    Frequency = db.Column(db.String(100), nullable=False)
    PatientID = db.Column(db.Integer, db.ForeignKey('Patient.PatientID'), nullable=False)
    MedicationCode = db.Column(db.String(20), db.ForeignKey('Medication.MedicationCode'), nullable=False)
    EmpID = db.Column(db.Integer, db.ForeignKey('Physician.EmpID'), nullable=False)
    
    # Ensure the same patient cannot be prescribed the same medication by different physicians
    __table_args__ = (
        db.UniqueConstraint('PatientID', 'MedicationCode', name='unique_patient_medication'),
    )
    
    # Relationships
    patient = relationship("Patient", back_populates="prescriptions")
    medication = relationship("Medication", back_populates="prescriptions")
    physician = relationship("Physician", back_populates="prescriptions")

class Medication(db.Model):
    __tablename__ = 'Medication'
    MedicationCode = db.Column(db.String(20), primary_key=True)
    MedicationName = db.Column(db.String(100), nullable=False)
    QuantityOnOrder = db.Column(db.Integer, default=0)
    QuantityOnHand = db.Column(db.Integer, default=0)
    UnitCost = db.Column(db.Numeric(10, 2), nullable=False)
    YearToDateUsage = db.Column(db.Integer, default=0)
    
    # Relationships
    prescriptions = relationship("Prescription", back_populates="medication")
    interactions_as_med1 = relationship("DrugInteraction", 
                                      foreign_keys="DrugInteraction.Medication1",
                                      back_populates="medication1")
    interactions_as_med2 = relationship("DrugInteraction", 
                                      foreign_keys="DrugInteraction.Medication2",
                                      back_populates="medication2")

class OperatingRoom(db.Model):
    __tablename__ = 'OperatingRoom'
    OpRoomID = db.Column(db.Integer, primary_key=True)
    
    # Relationships
    surgery_schedules = relationship("SurgerySchedule", back_populates="operating_room")

class DrugInteraction(db.Model):
    __tablename__ = 'DrugInteraction'
    Medication1 = db.Column(db.String(20), db.ForeignKey('Medication.MedicationCode'), primary_key=True)
    Medication2 = db.Column(db.String(20), db.ForeignKey('Medication.MedicationCode'), primary_key=True)
    Severity = db.Column(db.Enum(InteractionSeverity), nullable=False)
    
    # Relationships
    medication1 = relationship("Medication", foreign_keys=[Medication1], back_populates="interactions_as_med1")
    medication2 = relationship("Medication", foreign_keys=[Medication2], back_populates="interactions_as_med2")

class Allergy(db.Model):
    __tablename__ = 'Allergy'
    AllergyCode = db.Column(db.String(20), primary_key=True)
    AllergyName = db.Column(db.String(100), nullable=False)
    
    # Relationships
    patients = relationship("Patient", back_populates="allergy")
    diagnoses = relationship("Diagnosis", back_populates="allergy")

class Illness(db.Model):
    __tablename__ = 'Illness'
    IllnessCode = db.Column(db.String(20), primary_key=True)
    Description = db.Column(db.Text, nullable=False)
    
    # Relationships
    diagnoses = relationship("Diagnosis", back_populates="illness")

# Event listeners
@event.listens_for(Physician, 'before_delete')
def physician_before_delete(mapper, connection, physician):
    """This event is no longer responsible for patient reassignment.
    Patient reassignment is now handled in the route directly before deletion.
    This ensures we can handle the UI feedback appropriately."""
    # Intentionally left empty to avoid conflicts with the routes.py implementation
    pass

@event.listens_for(Nurse, 'before_delete')
def nurse_before_delete(mapper, connection, nurse):
    # Temporarily remove the association of inpatients attended by the nurse
    for inpatient in nurse.inpatients:
        inpatient.EmpID = None

@event.listens_for(Patient, 'before_insert')
@event.listens_for(Patient, 'before_update')
def patient_before_save(mapper, connection, patient):
    # Update heart risk level
    patient.HeartRiskLevel = patient.calculate_heart_risk()

@event.listens_for(Surgeon, 'before_delete')
def check_surgeon_surgeries(mapper, connection, surgeon):
    # Prevent deletion of surgeon with surgery records
    if surgeon.surgery_schedules:
        raise ValueError("Cannot delete surgeon with surgery records")

@event.listens_for(Patient, 'before_insert')
def check_patient_illness(mapper, connection, patient):
    # Skip validation if this is a test data insertion
    # This can be detected by checking a special attribute we'll set during test data insertion
    if hasattr(patient, '_skip_illness_check') and patient._skip_illness_check:
        return
    
    # Skip validation for web form submissions - we'll handle this in the route
    if hasattr(patient, '_from_web_form') and patient._from_web_form:
        print("Skipping illness validation for web form submission")
        return
    
    # Validate that a patient has at least one illness
    if not patient.diagnoses:
        print("Patient validation failed: No illnesses detected")
        raise ValueError("A patient must have at least one illness")
