from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    Date,
    ForeignKey,
)
from sqlalchemy.orm import declarative_base, relationship

from app.database.connection import engine


# Base class for all database models
Base = declarative_base()


# ---------------------------------------------------------
# REGIONS
# ---------------------------------------------------------

class Region(Base):
    __tablename__ = "regions"

    region_id = Column(Integer, primary_key=True)
    region_name = Column(
        String(100),
        nullable=False,
        unique=True
    )

    customers = relationship(
        "Customer",
        back_populates="region"
    )

    orders = relationship(
        "Order",
        back_populates="region"
    )


# ---------------------------------------------------------
# SALES CHANNELS
# ---------------------------------------------------------

class SalesChannel(Base):
    __tablename__ = "sales_channels"

    channel_id = Column(Integer, primary_key=True)

    channel_name = Column(
        String(100),
        nullable=False,
        unique=True
    )

    orders = relationship(
        "Order",
        back_populates="channel"
    )


# ---------------------------------------------------------
# CUSTOMERS
# ---------------------------------------------------------

class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(
        Integer,
        primary_key=True
    )

    customer_name = Column(
        String(150),
        nullable=False
    )

    email = Column(
        String(200)
    )

    region_id = Column(
        Integer,
        ForeignKey("regions.region_id")
    )

    region = relationship(
        "Region",
        back_populates="customers"
    )

    orders = relationship(
        "Order",
        back_populates="customer"
    )


# ---------------------------------------------------------
# PRODUCTS
# ---------------------------------------------------------

class Product(Base):
    __tablename__ = "products"

    product_id = Column(
        Integer,
        primary_key=True
    )

    product_name = Column(
        String(150),
        nullable=False
    )

    category = Column(
        String(100),
        nullable=False
    )

    price = Column(
        Numeric(12, 2),
        nullable=False
    )

    cost = Column(
        Numeric(12, 2),
        nullable=False
    )

    order_items = relationship(
        "OrderItem",
        back_populates="product"
    )


# ---------------------------------------------------------
# ORDERS
# ---------------------------------------------------------

class Order(Base):
    __tablename__ = "orders"

    order_id = Column(
        Integer,
        primary_key=True
    )

    customer_id = Column(
        Integer,
        ForeignKey("customers.customer_id")
    )

    region_id = Column(
        Integer,
        ForeignKey("regions.region_id")
    )

    channel_id = Column(
        Integer,
        ForeignKey("sales_channels.channel_id")
    )

    order_date = Column(
        Date,
        nullable=False
    )

    customer = relationship(
        "Customer",
        back_populates="orders"
    )

    region = relationship(
        "Region",
        back_populates="orders"
    )

    channel = relationship(
        "SalesChannel",
        back_populates="orders"
    )

    items = relationship(
        "OrderItem",
        back_populates="order"
    )


# ---------------------------------------------------------
# ORDER ITEMS
# ---------------------------------------------------------

class OrderItem(Base):
    __tablename__ = "order_items"

    order_item_id = Column(
        Integer,
        primary_key=True
    )

    order_id = Column(
        Integer,
        ForeignKey("orders.order_id")
    )

    product_id = Column(
        Integer,
        ForeignKey("products.product_id")
    )

    quantity = Column(
        Integer,
        nullable=False
    )

    unit_price = Column(
        Numeric(12, 2),
        nullable=False
    )

    revenue = Column(
        Numeric(14, 2),
        nullable=False
    )

    cost = Column(
        Numeric(14, 2),
        nullable=False
    )

    profit = Column(
        Numeric(14, 2),
        nullable=False
    )

    order = relationship(
        "Order",
        back_populates="items"
    )

    product = relationship(
        "Product",
        back_populates="order_items"
    )


# ---------------------------------------------------------
# CREATE TABLES
# ---------------------------------------------------------

if __name__ == "__main__":

    Base.metadata.create_all(engine)

    print("Database tables created successfully!")