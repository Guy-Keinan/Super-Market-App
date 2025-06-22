from sqlalchemy import Column, String, Numeric, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Supermarket(Base):
    __tablename__ = "supermarkets"
    id = Column(String(20), primary_key=True)
    name = Column(String, nullable=False)

class User(Base):
    __tablename__ = "users"
    id = Column(PG_UUID(as_uuid=True), primary_key=True)
    first_purchase = Column(DateTime)
    purchase_count = Column(Integer, default=0)

class Product(Base):
    __tablename__ = "products"
    name = Column(String, primary_key=True)
    unit_price = Column(Numeric(10,2), nullable=False)

class Purchase(Base):
    __tablename__ = "purchases"
    id = Column(Integer, primary_key=True, autoincrement=True)
    supermarket_id = Column(String(20), ForeignKey("supermarkets.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    items_list = Column(String, nullable=False)
    total_amount = Column(Numeric(10,2), nullable=False)
