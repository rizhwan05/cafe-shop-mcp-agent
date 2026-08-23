import uuid
from sqlalchemy import Column, String, Numeric, Boolean, Integer, BigInteger, Text, TIMESTAMP, ForeignKey, Sequence
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from repositories.database import Base


class MenuItemSchema(Base):
    __tablename__ = "menu_items"

    menu_item_id = Column(BigInteger, primary_key=True, autoincrement=True)
    menu_item_uuid = Column(UUID(as_uuid=True), nullable=False, unique=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    stock_quantity = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    created_by = Column(String(100), nullable=True)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    updated_by = Column(String(100), nullable=True)

    order_items = relationship("OrderItemSchema", back_populates="menu_item")


class OrderSchema(Base):
    __tablename__ = "orders"

    order_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_sequence_id = Column(BigInteger, Sequence("orders_order_sequence_id_seq"), unique=True, nullable=False)
    customer_name = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False, default="PENDING")
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    created_by = Column(String(100), nullable=True)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    updated_by = Column(String(100), nullable=True)

    items = relationship("OrderItemSchema", back_populates="order")


class OrderItemSchema(Base):
    __tablename__ = "order_items"

    order_item_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.order_id"), nullable=False)
    menu_item_id = Column(BigInteger, ForeignKey("menu_items.menu_item_id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    created_by = Column(String(100), nullable=True)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    updated_by = Column(String(100), nullable=True)

    order = relationship("OrderSchema", back_populates="items")
    menu_item = relationship("MenuItemSchema", back_populates="order_items")


class ErrorLogSchema(Base):
    __tablename__ = "error_logs"

    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    error_code = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    source = Column(String(200), nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    created_by = Column(String(100), nullable=True)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    updated_by = Column(String(100), nullable=True)
