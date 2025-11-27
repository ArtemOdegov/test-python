from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class OperatorBase(BaseModel):
    name: str
    is_active: bool = True
    max_load: int = 10


class OperatorCreate(OperatorBase):
    pass


class OperatorUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    max_load: Optional[int] = None


class OperatorResponse(OperatorBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class SourceBase(BaseModel):
    name: str
    description: Optional[str] = None


class SourceCreate(SourceBase):
    pass


class SourceResponse(SourceBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class SourceOperatorWeightBase(BaseModel):
    operator_id: int
    weight: float = 1.0


class SourceOperatorWeightCreate(SourceOperatorWeightBase):
    pass


class SourceOperatorWeightResponse(SourceOperatorWeightBase):
    id: int
    source_id: int
    
    class Config:
        from_attributes = True


class SourceOperatorWeightUpdate(BaseModel):
    weight: float


class SourceConfigResponse(SourceResponse):
    operator_weights: List[SourceOperatorWeightResponse] = []
    
    class Config:
        from_attributes = True


class LeadBase(BaseModel):
    external_id: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    name: Optional[str] = None


class LeadCreate(LeadBase):
    pass


class LeadResponse(LeadBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ContactBase(BaseModel):
    source_id: int
    message: Optional[str] = None


class ContactCreate(ContactBase):
    lead_external_id: Optional[str] = None
    lead_phone: Optional[str] = None
    lead_email: Optional[EmailStr] = None
    lead_name: Optional[str] = None


class ContactResponse(BaseModel):
    id: int
    lead_id: int
    source_id: int
    operator_id: Optional[int] = None
    status: str
    message: Optional[str] = None
    created_at: datetime
    
    lead: LeadResponse
    source: SourceResponse
    operator: Optional[OperatorResponse] = None
    
    class Config:
        from_attributes = True


class OperatorStats(BaseModel):
    operator_id: int
    operator_name: str
    active_contacts_count: int
    max_load: int
    utilization_percent: float


class SourceStats(BaseModel):
    source_id: int
    source_name: str
    total_contacts: int
    operator_distribution: List[dict]


class LeadWithContacts(BaseModel):
    lead: LeadResponse
    contacts: List[ContactResponse]

