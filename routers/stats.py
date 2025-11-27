from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List, Dict

from database import get_db
from models import Source, Contact, Operator
from schemas import SourceStats


router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/sources/{source_id}", response_model=SourceStats)
async def get_source_stats(
    source_id: int,
    db: AsyncSession = Depends(get_db)
):
    source_result = await db.execute(
        select(Source).where(Source.id == source_id)
    )
    source = source_result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Источник не найден")
    
    total_result = await db.execute(
        select(func.count(Contact.id))
        .where(Contact.source_id == source_id)
    )
    total_contacts = total_result.scalar() or 0
    
    distribution_result = await db.execute(
        select(
            Contact.operator_id,
            Operator.name,
            func.count(Contact.id).label("count")
        )
        .join(Operator, Contact.operator_id == Operator.id, isouter=True)
        .where(Contact.source_id == source_id)
        .group_by(Contact.operator_id, Operator.name)
    )
    
    distribution = []
    for row in distribution_result.all():
        distribution.append({
            "operator_id": row.operator_id,
            "operator_name": row.name or "Не назначен",
            "count": row.count
        })
    
    return SourceStats(
        source_id=source.id,
        source_name=source.name,
        total_contacts=total_contacts,
        operator_distribution=distribution
    )

