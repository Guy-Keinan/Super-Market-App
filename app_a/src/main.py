from fastapi import FastAPI, HTTPException, Depends
from uuid import uuid4
from datetime import datetime
import os

from contextlib import asynccontextmanager
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from .db import AsyncSessionLocal
from .models import Supermarket, User, Product, Purchase


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncSessionLocal() as session:
        yield


app = FastAPI(lifespan=lifespan)


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


@app.post("/purchase")
async def create_purchase(purchase: dict, session: AsyncSession = Depends(get_session)):
    supermarket_id = purchase.get("supermarket_id")
    user_id = purchase.get("user_id") or str(uuid4())
    items = purchase.get("items", [])

    if len(items) != len(set(items)):
        raise HTTPException(
            status_code=400,
            detail="Each product can only be purchased once per transaction",
        )

    timestamp = datetime.utcnow()

    result = await session.execute(select(Product).where(Product.name.in_(items)))
    products = result.scalars().all()
    prices = {p.name: float(p.unit_price) for p in products}

    for item in items:
        if item not in prices:
            raise HTTPException(status_code=404, detail=f"Product '{item}' not found")

    total_amount = sum(prices[item] for item in items)

    stmt_user = (
        insert(User)
        .values(id=user_id, first_purchase=timestamp, purchase_count=1)
        .on_conflict_do_update(
            index_elements=[User.id], set_={"purchase_count": User.purchase_count + 1}
        )
    )
    await session.execute(stmt_user)

    new_purchase = Purchase(
        supermarket_id=str(supermarket_id),
        timestamp=timestamp,
        user_id=user_id,
        items_list=str(items),
        total_amount=total_amount,
    )
    session.add(new_purchase)

    await session.commit()

    return {"user_id": user_id, "total_amount": total_amount}
