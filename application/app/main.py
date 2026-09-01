import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

logger = logging.getLogger("order-api")


from typing import List
from uuid import uuid4
from prometheus_fastapi_instrumentator import Instrumentator

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.config import APP_ENV, APP_NAME, APP_VERSION
from app.database import get_db
from app.models import Order as OrderModel

from app.config import APP_NAME, APP_VERSION, APP_ENV


app = FastAPI(
    title=APP_NAME,
    description="Production-style DevOps demonstration application",
    version=APP_VERSION,
)
Instrumentator().instrument(app).expose(app)

# -------------------------
# Data Models
# -------------------------

from pydantic import BaseModel, Field


class OrderCreate(BaseModel):
    customer_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )

    product_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )

    quantity: int = Field(
        ...,
        gt=0,
        le=100,
    )

    price: float = Field(
        ...,
        gt=0,
        le=1000000,
    )


class Order(OrderCreate):
    order_id: str
    status: str


# -------------------------
# Temporary Data Store
# -------------------------




# -------------------------
# Health Endpoints
# -------------------------

@app.get("/")
def root():
    return {
        "application": "Order Management API",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/ready")
def readiness():
    return {
        "status": "ready"
    }

@app.get("/version")
def version():
    return {
        "application": APP_NAME,
        "version": "3.1.0",
        "environment": APP_ENV,
    }


# -------------------------
# Order Endpoints
# -------------------------

@app.post("/orders", response_model=Order, status_code=201)
def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
):
    order_id = str(uuid4())

    new_order = OrderModel(
        order_id=order_id,
        customer_name=order.customer_name,
        product_name=order.product_name,
        quantity=order.quantity,
        price=order.price,
        status="CREATED",
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    logger.info(
        "Order created: order_id=%s customer=%s product=%s",
        order_id,
        order.customer_name,
        order.product_name,
    )

    return new_order


@app.get("/orders", response_model=List[Order])
def get_orders(
    db: Session = Depends(get_db),
):
    return db.query(OrderModel).all()


@app.get("/test-error")
def test_error():
    raise HTTPException(
        status_code=500,
        detail="Intentional test error",
    )


@app.get("/orders/{order_id}", response_model=Order)
def get_order(
    order_id: str,
    db: Session = Depends(get_db),
):
    order = (
        db.query(OrderModel)
        .filter(OrderModel.order_id == order_id)
        .first()
    )

    if order is None:
        logger.warning(
            "Order not found: order_id=%s",
            order_id,
        )

        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    return order
