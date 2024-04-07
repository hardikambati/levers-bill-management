from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
)
from sqlalchemy.orm import relationship

# custom imports
from app.database import Base


class SubBill(Base):
    
    __tablename__ = "sub_bills"
    
    id        = Column(Integer, primary_key=True, index=True)
    amount    = Column(Float, nullable=False)
    reference = Column(String(255), nullable=True, unique=True)
    bill_id   = Column(Integer, ForeignKey('bills.id'))
    bill      = relationship("Bill", back_populates="sub_bills")


class Bill(Base):

    __tablename__ = "bills"

    id        = Column(Integer, primary_key=True, index=True)
    total     = Column(Float, nullable=False)
    sub_bills = relationship("SubBill", back_populates="bill", cascade="all, delete")
