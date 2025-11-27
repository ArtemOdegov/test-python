from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import Optional, List
import random
from models import Operator, SourceOperatorWeight, Contact, Lead


async def get_operator_load(session: AsyncSession, operator_id: int) -> int:
    result = await session.execute(
        select(func.count(Contact.id))
        .where(Contact.operator_id == operator_id)
        .where(Contact.status == "active")
    )
    return result.scalar() or 0


async def select_operator(
    session: AsyncSession, 
    source_id: int
) -> Optional[Operator]:
    result = await session.execute(
        select(SourceOperatorWeight)
        .where(SourceOperatorWeight.source_id == source_id)
        .options(selectinload(SourceOperatorWeight.operator))
    )
    weights = result.scalars().all()
    
    if not weights:
        return None
    
    
    available_operators = []
    available_weights = []
    
    for weight_item in weights:
        operator = weight_item.operator
        if not operator.is_active:
            continue
        
        current_load = await get_operator_load(session, operator.id)
        if current_load >= operator.max_load:
            continue
        
        available_operators.append(operator)
        available_weights.append(weight_item.weight)
    
    if not available_operators:
        return None
    
  
    total_weight = sum(available_weights)
    if total_weight == 0:
        return random.choice(available_operators)
    
    random_value = random.uniform(0, total_weight)
    
    cumulative = 0
    for i, weight in enumerate(available_weights):
        cumulative += weight
        if random_value <= cumulative:
            return available_operators[i]
    
    return available_operators[-1]


async def find_or_create_lead(
    session: AsyncSession,
    external_id: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    name: Optional[str] = None
) -> Lead:
    if external_id:
        result = await session.execute(
            select(Lead).where(Lead.external_id == external_id)
        )
        lead = result.scalar_one_or_none()
        if lead:
            return lead
    
    if phone:
        result = await session.execute(
            select(Lead).where(Lead.phone == phone)
        )
        lead = result.scalar_one_or_none()
        if lead:
            return lead
    
    if email:
        result = await session.execute(
            select(Lead).where(Lead.email == email)
        )
        lead = result.scalar_one_or_none()
        if lead:
            return lead
    
    new_lead = Lead(
        external_id=external_id,
        phone=phone,
        email=email,
        name=name
    )
    session.add(new_lead)
    await session.commit()
    await session.refresh(new_lead)
    return new_lead

