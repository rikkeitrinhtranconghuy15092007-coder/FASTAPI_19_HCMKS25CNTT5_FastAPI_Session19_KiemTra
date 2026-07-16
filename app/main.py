from fastapi import FastAPI, Depends, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi.responses import JSONResponse
from typing import Optional, List

from database import engine, Base, get_db
import schemas
import crud

app = FastAPI(title="Clinic Management API")

# Cấu hình Middleware CORS tương tự ứng dụng mẫu
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    try:
        Base.metadata.create_all(bind=engine)
        print("--- ĐÃ KHỞI TẠO HỆ THỐNG DB CLINIC THÀNH CÔNG! ---")
    except Exception as e:
        print(f"Lỗi khởi tạo bảng: {e}")

@app.exception_handler(IntegrityError)
async def global_integrity_error_handler(request, exc: IntegrityError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "status": "error",
            "message": "Vi phạm ràng buộc dữ liệu hoặc trùng mã khóa (Unique/Foreign Key)!",
            "detail": str(exc.orig)
        }
    )

@app.get("/")
def root():
    return {"status": "Success", "message": "Hệ thống Quản lý Y tế đang hoạt động!"}


@app.post("/clinics", response_model=schemas.ClinicResponse, status_code=status.HTTP_201_CREATED, tags=["Clinic"])
def create_clinic(clinic_data: schemas.ClinicCreate, db: Session = Depends(get_db)):
    return crud.create_clinic(db, clinic_data)

@app.get("/clinics", response_model=schemas.PaginatedClinicResponse, tags=["Clinic"])
def get_clinics(
    page: int = 1, 
    limit: int = 10, 
    search: Optional[str] = None, 
    db: Session = Depends(get_db)
):
    return crud.get_all_clinics_paginated(db, page, limit, search) # type: ignore

@app.get("/clinics/{clinic_id}", response_model=schemas.ClinicDetailResponse, tags=["Clinic"])
def get_clinic_detail(clinic_id: int, db: Session = Depends(get_db)):
    return crud.get_clinic_by_id(db, clinic_id)



@app.post("/doctors", response_model=schemas.DoctorResponse, status_code=status.HTTP_201_CREATED, tags=["Doctor"])
def create_doctor(doctor_data: schemas.DoctorCreate, db: Session = Depends(get_db)):
    return crud.create_doctor(db, doctor_data)

@app.get("/doctors", response_model=List[schemas.DoctorResponse], tags=["Doctor"])
def get_doctors(clinic_id: Optional[int] = None, db: Session = Depends(get_db)):
    if clinic_id is not None:
        return crud.get_doctors_by_clinic(db, clinic_id)
    import models
    return db.query(models.Doctor).all()

@app.get("/doctors/{doctor_id}", response_model=schemas.DoctorResponse, tags=["Doctor"])
def get_doctor_detail(doctor_id: int, db: Session = Depends(get_db)):
    return crud.get_doctor_by_id(db, doctor_id)

@app.patch("/doctors/{doctor_id}", response_model=schemas.DoctorResponse, tags=["Doctor"])
def update_doctor(doctor_id: int, doctor_update: schemas.DoctorUpdate, db: Session = Depends(get_db)):
    return crud.update_doctor(db, doctor_id, doctor_update)


# --- LICENSE ENDPOINTS ---

@app.delete("/licenses/{license_id}", tags=["License"])
def delete_license(license_id: int, db: Session = Depends(get_db)):
    return crud.delete_license(db, license_id)