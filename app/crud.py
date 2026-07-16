import math
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import models
import schemas


def create_clinic(db: Session, clinic: schemas.ClinicCreate):
    db_clinic = models.Clinic(**clinic.model_dump())
    try:
        db.add(db_clinic)
        db.commit()
        db.refresh(db_clinic)
        return db_clinic
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Lỗi tạo phòng khám: {str(e)}")

def get_clinic_by_id(db: Session, clinic_id: int):
    clinic = db.query(models.Clinic).filter(models.Clinic.id == clinic_id).first()
    if not clinic:
        raise HTTPException(status_code=404, detail="Không tìm thấy phòng khám!")
    return clinic

def get_all_clinics_paginated(db: Session, page: int, limit: int, search: str = None): # type: ignore
    query = db.query(models.Clinic)
    if search:
        query = query.filter(models.Clinic.clinic_name.ilike(f"%{search}%"))
        
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



def create_doctor(db: Session, doctor: schemas.DoctorCreate):
    clinic = db.query(models.Clinic).filter(models.Clinic.id == doctor.clinic_id).first()
    if not clinic:
        raise HTTPException(status_code=400, detail="Không tìm thấy phòng khám tương ứng (clinic_id)!")

    existing_code = db.query(models.Doctor).filter(models.Doctor.doctor_code == doctor.doctor_code).first()
    if existing_code:
        raise HTTPException(status_code=409, detail="Mã số bác sĩ đã tồn tại trên hệ thống!")

    db_doctor = models.Doctor(**doctor.model_dump())
    try:
        db.add(db_doctor)
        db.commit()
        db.refresh(db_doctor)
        return db_doctor
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Lỗi thêm bác sĩ: {str(e)}")

def get_doctor_by_id(db: Session, doctor_id: int):
    doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông tin bác sĩ!")
    return doctor

def get_doctors_by_clinic(db: Session, clinic_id: int):
    clinic = db.query(models.Clinic).filter(models.Clinic.id == clinic_id).first()
    if not clinic:
        raise HTTPException(status_code=404, detail="Phòng khám không tồn tại!")
    return db.query(models.Doctor).filter(models.Doctor.clinic_id == clinic_id).all()

def update_doctor(db: Session, doctor_id: int, doctor_update: schemas.DoctorUpdate):
    db_doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if not db_doctor:
        raise HTTPException(status_code=404, detail="Không tìm thấy bác sĩ cần chỉnh sửa!")

    update_data = doctor_update.model_dump(exclude_unset=True)

    if "clinic_id" in update_data:
        clinic = db.query(models.Clinic).filter(models.Clinic.id == update_data["clinic_id"]).first()
        if not clinic:
            raise HTTPException(status_code=400, detail="Phòng khám (clinic_id) cập nhật không tồn tại!")

    try:
        for key, value in update_data.items():
            setattr(db_doctor, key, value)
        db.commit()
        db.refresh(db_doctor)
        return db_doctor
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Lỗi cập nhật bác sĩ: {str(e)}")

def get_all_doctors(db: Session):
    return db.query(models.Doctor).all()



def delete_license(db: Session, license_id: int):
    db_license = db.query(models.License).filter(models.License.id == license_id).first()
    if not db_license:
        raise HTTPException(status_code=404, detail="Không tìm thấy chứng chỉ để xóa!")
    try:
        db.delete(db_license)
        db.commit()
        return {"message": "Deleted"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Lỗi khi xóa chứng chỉ: {str(e)}")