import json
from collections import Counter
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from .db import engine, AsyncSessionLocal, get_session
from .models import Base, Purchase


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/stats/unique_customers")
async def unique_customers(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(func.count(func.distinct(Purchase.user_id))))
    count = result.scalar_one()
    return {"unique_customers": count}


@app.get("/stats/loyal_customers")
async def loyal_customers(session: AsyncSession = Depends(get_session)):
    stmt = (
        select(Purchase.user_id)
        .group_by(Purchase.user_id)
        .having(func.count(Purchase.id) >= 3)
    )
    result = await session.execute(stmt)
    users = [row[0] for row in result.all()]
    return {"loyal_customers": users}


@app.get("/stats/top_products")
async def top_products(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Purchase.items_list))
    rows = result.scalars().all()

    items = []
    for text_list in rows:
        try:
            data = json.loads(text_list)
        except json.JSONDecodeError:
            inner = text_list.strip().strip("[]{}")
            parts = [p.strip().strip('"') for p in inner.split(",") if p.strip()]
            data = parts
        items.extend(data)

    if not items:
        return {"top_products": []}

    counts = Counter(items)
    max_count = max(counts.values())
    top = [item for item, cnt in counts.items() if cnt == max_count]
    return {"top_products": top}
