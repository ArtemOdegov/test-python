from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

from database import get_db
from models import Source, SourceOperatorWeight, Operator
from schemas import (
    SourceCreate,
    SourceResponse,
    SourceConfigResponse,
    SourceOperatorWeightCreate,
    SourceOperatorWeightUpdate,
    SourceOperatorWeightResponse
)


router = APIRouter(prefix="/sources", tags=["sources"])


@router.post("/", response_model=SourceResponse, status_code=201)
async def create_source(
    source: SourceCreate,
    db: AsyncSession = Depends(get_db)
):
    new_source = Source(**source.dict())
    db.add(new_source)
    await db.commit()
    await db.refresh(new_source)
    return new_source


@router.get("/", response_model=List[SourceResponse])
async def list_sources(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Source))
    sources = result.scalars().all()
    return sources


@router.get("/{source_id}", response_model=SourceConfigResponse)
async def get_source(
    source_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Source)
        .where(Source.id == source_id)
        .options(selectinload(Source.operator_weights).selectinload(SourceOperatorWeight.operator))
    )
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Источник не найден")
    return source


@router.post("/{source_id}/operators", response_model=SourceOperatorWeightResponse, status_code=201)
async def add_operator_to_source(
    source_id: int,
    weight_data: SourceOperatorWeightCreate,
    db: AsyncSession = Depends(get_db)
):
    source_result = await db.execute(
        select(Source).where(Source.id == source_id)
    )
    source = source_result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Источник не найден")
    
    operator_result = await db.execute(
        select(Operator).where(Operator.id == weight_data.operator_id)
    )
    operator = operator_result.scalar_one_or_none()
    if not operator:
        raise HTTPException(status_code=404, detail="Оператор не найден")
    
    existing_result = await db.execute(
        select(SourceOperatorWeight)
        .where(SourceOperatorWeight.source_id == source_id)
        .where(SourceOperatorWeight.operator_id == weight_data.operator_id)
    )
    existing = existing_result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Оператор уже назначен на этот источник")
    
    new_weight = SourceOperatorWeight(
        source_id=source_id,
        operator_id=weight_data.operator_id,
        weight=weight_data.weight
    )
    db.add(new_weight)
    await db.commit()
    await db.refresh(new_weight)
    return new_weight


@router.patch("/{source_id}/operators/{operator_id}", response_model=SourceOperatorWeightResponse)
async def update_operator_weight(
    source_id: int,
    operator_id: int,
    weight_update: SourceOperatorWeightUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(SourceOperatorWeight)
        .where(SourceOperatorWeight.source_id == source_id)
        .where(SourceOperatorWeight.operator_id == operator_id)
    )
    weight = result.scalar_one_or_none()
    if not weight:
        raise HTTPException(status_code=404, detail="Связь источник-оператор не найдена")
    
    weight.weight = weight_update.weight
    await db.commit()
    await db.refresh(weight)
    return weight


@router.delete("/{source_id}/operators/{operator_id}", status_code=204)
async def remove_operator_from_source(
    source_id: int,
    operator_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(SourceOperatorWeight)
        .where(SourceOperatorWeight.source_id == source_id)
        .where(SourceOperatorWeight.operator_id == operator_id)
    )
    weight = result.scalar_one_or_none()
    if not weight:
        raise HTTPException(status_code=404, detail="Связь источник-оператор не найдена")
    
    await db.delete(weight)
    await db.commit()
    return None

