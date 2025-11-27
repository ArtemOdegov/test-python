from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List, Optional

from database import get_db
from models import Contact, Lead, Source, Operator
from schemas import ContactCreate, ContactResponse, LeadWithContacts
from distribution import find_or_create_lead, select_operator


router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.post("/", response_model=ContactResponse, status_code=201)
async def create_contact(
    contact: ContactCreate,
    db: AsyncSession = Depends(get_db)
):
    source_result = await db.execute(
        select(Source).where(Source.id == contact.source_id)
    )
    source = source_result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Источник не найден")
    
    
    lead = await find_or_create_lead(
        db,
        external_id=contact.lead_external_id,
        phone=contact.lead_phone,
        email=contact.lead_email,
        name=contact.lead_name
    )
    
    
    operator = await select_operator(db, contact.source_id)
    
    
    new_contact = Contact(
        lead_id=lead.id,
        source_id=contact.source_id,
        operator_id=operator.id if operator else None,
        message=contact.message,
        status="active"
    )
    db.add(new_contact)
    await db.commit()
    await db.refresh(new_contact)
    
    
    result = await db.execute(
        select(Contact)
        .where(Contact.id == new_contact.id)
        .options(
            selectinload(Contact.lead),
            selectinload(Contact.source),
            selectinload(Contact.operator)
        )
    )
    contact_with_relations = result.scalar_one()
    
    return contact_with_relations


@router.get("/", response_model=List[ContactResponse])
async def list_contacts(
    skip: int = 0,
    limit: int = 100,
    lead_id: Optional[int] = None,
    source_id: Optional[int] = None,
    operator_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Contact)
    
    if lead_id:
        query = query.where(Contact.lead_id == lead_id)
    if source_id:
        query = query.where(Contact.source_id == source_id)
    if operator_id:
        query = query.where(Contact.operator_id == operator_id)
    
    query = query.offset(skip).limit(limit).order_by(Contact.created_at.desc())
    
    result = await db.execute(
        query.options(
            selectinload(Contact.lead),
            selectinload(Contact.source),
            selectinload(Contact.operator)
        )
    )
    contacts = result.scalars().all()
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Contact)
        .where(Contact.id == contact_id)
        .options(
            selectinload(Contact.lead),
            selectinload(Contact.source),
            selectinload(Contact.operator)
        )
    )
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Обращение не найдено")
    return contact


@router.patch("/{contact_id}/status", response_model=ContactResponse)
async def update_contact_status(
    contact_id: int,
    status: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id)
    )
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Обращение не найдено")
    
    contact.status = status
    await db.commit()
    
    
    result = await db.execute(
        select(Contact)
        .where(Contact.id == contact_id)
        .options(
            selectinload(Contact.lead),
            selectinload(Contact.source),
            selectinload(Contact.operator)
        )
    )
    updated_contact = result.scalar_one()
    return updated_contact

