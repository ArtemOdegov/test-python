from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

from database import get_db
from models import Operator
from schemas import (
    OperatorCreate,
    OperatorUpdate,
    OperatorResponse,
    OperatorStats
)


router = APIRouter(prefix="/operators", tags=["operators"])


@router.post("/", response_model=OperatorResponse, status_code=201)
async def create_operator(
    operator: OperatorCreate,
    db: AsyncSession = Depends(get_db)
):
    new_operator = Operator(**operator.dict())
    db.add(new_operator)
    await db.commit()
    await db.refresh(new_operator)
    return new_operator


@router.get("/", response_model=List[OperatorResponse])
async def list_operators(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Operator))
    operators = result.scalars().all()
    return operators


@router.get("/{operator_id}", response_model=OperatorResponse)
async def get_operator(
    operator_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Operator).where(Operator.id == operator_id)
    )
    operator = result.scalar_one_or_none()
    if not operator:
        raise HTTPException(status_code=404, detail="Оператор не найден")
    return operator


@router.patch("/{operator_id}", response_model=OperatorResponse)
async def update_operator(
    operator_id: int,
    operator_update: OperatorUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Operator).where(Operator.id == operator_id)
    )
    operator = result.scalar_one_or_none()
    if not operator:
        raise HTTPException(status_code=404, detail="Оператор не найден")
    
    update_data = operator_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(operator, field, value)
    
    await db.commit()
    await db.refresh(operator)
    return operator


@router.delete("/{operator_id}", status_code=204)
async def delete_operator(
    operator_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Operator).where(Operator.id == operator_id)
    )
    operator = result.scalar_one_or_none()
    if not operator:
        raise HTTPException(status_code=404, detail="Оператор не найден")
    
    await db.delete(operator)
    await db.commit()
    return None


@router.get("/{operator_id}/stats", response_model=OperatorStats)
async def get_operator_stats(
    operator_id: int,
    db: AsyncSession = Depends(get_db)
):
    from distribution import get_operator_load
    
    result = await db.execute(
        select(Operator).where(Operator.id == operator_id)
    )
    operator = result.scalar_one_or_none()
    if not operator:
        raise HTTPException(status_code=404, detail="Оператор не найден")
    
    active_load = await get_operator_load(db, operator_id)
    utilization = (active_load / operator.max_load * 100) if operator.max_load > 0 else 0
    
    return OperatorStats(
        operator_id=operator.id,
        operator_name=operator.name,
        active_contacts_count=active_load,
        max_load=operator.max_load,
        utilization_percent=round(utilization, 2)
    )

