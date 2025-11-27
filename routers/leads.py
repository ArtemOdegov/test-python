from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

from database import get_db
from models import Lead, Contact
from schemas import LeadResponse, LeadWithContacts


router = APIRouter(prefix="/leads", tags=["leads"])


@router.get("/", response_model=List[LeadResponse])
async def list_leads(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Lead).offset(skip).limit(limit).order_by(Lead.created_at.desc())
    )
    leads = result.scalars().all()
    return leads


@router.get("/{lead_id}", response_model=LeadWithContacts)
async def get_lead_with_contacts(
    lead_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Lead)
        .where(Lead.id == lead_id)
        .options(selectinload(Lead.contacts).selectinload(Contact.source))
        .options(selectinload(Lead.contacts).selectinload(Contact.operator))
    )
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Лид не найден")
    
    return LeadWithContacts(lead=lead, contacts=lead.contacts)

