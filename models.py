from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Operator(Base):
    __tablename__ = "operators"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    max_load = Column(Integer, default=10, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    source_weights = relationship("SourceOperatorWeight", back_populates="operator", cascade="all, delete-orphan")
    contacts = relationship("Contact", back_populates="operator")


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    operator_weights = relationship("SourceOperatorWeight", back_populates="source", cascade="all, delete-orphan")
    contacts = relationship("Contact", back_populates="source")


class SourceOperatorWeight(Base):
    __tablename__ = "source_operator_weights"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    operator_id = Column(Integer, ForeignKey("operators.id"), nullable=False)
    weight = Column(Float, default=1.0, nullable=False)
    
    __table_args__ = (
        UniqueConstraint('source_id', 'operator_id', name='uq_source_operator'),
    )
    
    source = relationship("Source", back_populates="operator_weights")
    operator = relationship("Operator", back_populates="source_weights")


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, nullable=True, index=True)
    phone = Column(String, nullable=True, index=True)
    email = Column(String, nullable=True, index=True)
    name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    contacts = relationship("Contact", back_populates="lead")


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    operator_id = Column(Integer, ForeignKey("operators.id"), nullable=True)
    status = Column(String, default="active", nullable=False)
    message = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    lead = relationship("Lead", back_populates="contacts")
    source = relationship("Source", back_populates="contacts")
    operator = relationship("Operator", back_populates="contacts")

