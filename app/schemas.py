from pydantic import BaseModel, ConfigDict
from typing import List, Optional

# --- LICENSE ---
class LicenseResponse(BaseModel):
    id: int
    license_number: str
    issue_by: str
    doctor_id: int

    model_config = ConfigDict(from_attributes=True)


# --- CLINIC ---
class ClinicCreate(BaseModel):
    clinic_name: str
    specialty: str

class ClinicResponse(BaseModel):
    id: int
    clinic_name: str
    specialty: str

    model_config = ConfigDict(from_attributes=True)

class PaginatedClinicResponse(BaseModel):
    total_records: int
    total_pages: int
    current_page: int
    limit: int
    data: List[ClinicResponse]


# --- DOCTOR ---
class DoctorCreate(BaseModel):
    doctor_code: str
    salary: float
    clinic_id: int

class DoctorUpdate(BaseModel):
    doctor_code: Optional[str] = None
    salary: Optional[float] = None
    clinic_id: Optional[int] = None

class DoctorResponse(BaseModel):
    id: int
    doctor_code: str
    salary: float
    clinic: ClinicResponse
    license: Optional[LicenseResponse] = None

    model_config = ConfigDict(from_attributes=True)


# --- CLINIC DETAIL (Chứa danh sách bác sĩ) ---
class ClinicDetailResponse(ClinicResponse):
    doctors: List[DoctorResponse]

    model_config = ConfigDict(from_attributes=True)