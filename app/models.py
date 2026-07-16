from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Clinic(Base):
    __tablename__ = "clinics"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    clinic_name = Column(String(100), nullable=False)
    specialty = Column(String(100), nullable=False)

    doctors = relationship("Doctor", back_populates="clinic")


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    doctor_code = Column(String(20), nullable=False, unique=True, index=True)
    salary = Column(Float, nullable=False)
    clinic_id = Column(Integer, ForeignKey("clinics.id"), nullable=False)

    clinic = relationship("Clinic", back_populates="doctors")
    
    license = relationship("License", uselist=False, back_populates="doctor")


class License(Base):
    __tablename__ = "licenses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    license_number = Column(String(30), nullable=False, unique=True, index=True)
    issue_by = Column(String(100), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False, unique=True)

    doctor = relationship("Doctor", back_populates="license")