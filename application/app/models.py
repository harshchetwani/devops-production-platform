from sqlalchemy import Column, Float, Integer, String

from app.database import Base


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(
        String,
        primary_key=True,
        index=True,
    )

    customer_name = Column(
        String(100),
        nullable=False,
    )

    product_name = Column(
        String(100),
        nullable=False,
    )

    quantity = Column(
        Integer,
        nullable=False,
    )

    price = Column(
        Float,
        nullable=False,
    )

    status = Column(
        String(30),
        nullable=False,
        default="CREATED",
    )