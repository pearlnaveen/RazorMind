from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base


class Transaction(Base):

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    transaction_id = Column(String, unique=True, index=True)

    customer_id = Column(String, index=True)

    amount = Column(Float)

    payment_method = Column(String)

    status = Column(String)

    failure_reason = Column(String, nullable=True)

    created_at = Column(DateTime)