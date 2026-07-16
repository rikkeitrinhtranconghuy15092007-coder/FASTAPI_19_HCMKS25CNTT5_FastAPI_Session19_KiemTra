import math
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from app.models import Clinic, Doctor, License
from app.schemas import ClinicCreate, DoctorCreate, DoctorUpdate


def create_clinic(db: Session, clinic_data: ClinicCreate) -> Clinic:
    db_clinic = Clinic(
        clinic_name=clinic_data.clinic_name,
        specialty=clinic_data.specialty
    )
    try:
        db.add(db_clinic)
        db.commit()
        db.refresh(db_clinic)
        return db_clinic
    except Exception as e:
        db.rollback()
        raise e

def get_clinic_by_id(db: Session, clinic_id: int) -> Optional[Clinic]:
    return db.query(Clinic).filter(Clinic.id == clinic_id).first()

def get_all_clinics_paginated(db: Session, page: int, limit: int, search: Optional[str] = None) -> Dict[str, Any]:
    query = db.query(Clinic)
    if search:
        query = query.filter(Clinic.clinic_name.ilike(f"%{search}%"))
        
    total_records = query.count()
    total_pages = math.ceil(total_records / limit) if total_records > 0 else 1
    offset = (page - 1) * limit
    
    data = query.offset(offset).limit(limit).all()
    return {
        "total_records": total_records,
        "total_pages": total_pages,
        "current_page": page,
        "limit": limit,
        "data": data
    }



def create_doctor(db: Session, doctor_data: DoctorCreate) -> Doctor:
    clinic_exists = db.query(Clinic).filter(Clinic.id == doctor_data.clinic_id).first()
    if not clinic_exists:
        raise HTTPException(status_code=400, detail="Clinic ID does not exist")

    code_exists = db.query(Doctor).filter(Doctor.doctor_code == doctor_data.doctor_code).first()
    if code_exists:
        raise HTTPException(status_code=409, detail="Doctor code already exists")

    db_doctor = Doctor(
        doctor_code=doctor_data.doctor_code,
        salary=doctor_data.salary,
        clinic_id=doctor_data.clinic_id
    )
    try:
        db.add(db_doctor)
        db.commit()
        db.refresh(db_doctor)
        return db_doctor
    except Exception as e:
        db.rollback()
        raise e

def get_doctor_by_id(db: Session, doctor_id: int) -> Optional[Doctor]:
    return db.query(Doctor).filter(Doctor.id == doctor_id).first()

def get_doctors_by_clinic_id(db: Session, clinic_id: int) -> List[Doctor]:
    return db.query(Doctor).filter(Doctor.clinic_id == clinic_id).all()

def update_doctor(db: Session, doctor_id: int, doctor_update: DoctorUpdate) -> Optional[Doctor]:
    db_doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not db_doctor:
        return None
        
    update_data = doctor_update.model_dump(exclude_unset=True)
    
    if "clinic_id" in update_data:
        clinic_exists = db.query(Clinic).filter(Clinic.id == update_data["clinic_id"]).first()
        if not clinic_exists:
            raise HTTPException(status_code=400, detail="Target Clinic ID does not exist")

    try:
        for key, value in update_data.items():
            setattr(db_doctor, key, value)
        db.commit()
        db.refresh(db_doctor)
        return db_doctor
    except Exception as e:
        db.rollback()
        raise e



def delete_license(db: Session, license_id: int) -> bool:
    db_license = db.query(License).filter(License.id == license_id).first()
    if not db_license:
        return False
    try:
        db.delete(db_license)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e