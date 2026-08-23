from typing import List, Optional
from repositories.database import get_db
from repositories.schema.schema import MenuItemSchema, OrderSchema, OrderItemSchema
from utils.exceptions.custom_exceptions import DatabaseConnectionException


class CoffeeRepository:

    def get_menu_items(self, active_only: bool = True) -> List[MenuItemSchema]:
        try:
            with get_db() as session:
                query = session.query(MenuItemSchema)
                if active_only:
                    query = query.filter(MenuItemSchema.is_active.is_(True))
                items = query.order_by(MenuItemSchema.name.asc()).all()
                for item in items:
                    session.expunge(item)
                return items
        except DatabaseConnectionException:
            raise
        except Exception as e:
            raise DatabaseConnectionException(detail=f"Failed to fetch menu items: {str(e)}")

    def get_menu_item_by_name(self, name: str) -> Optional[MenuItemSchema]:
        try:
            with get_db() as session:
                item = session.query(MenuItemSchema).filter(
                    MenuItemSchema.name.ilike(name)
                ).first()
                if item:
                    session.expunge(item)
                return item
        except DatabaseConnectionException:
            raise
        except Exception as e:
            raise DatabaseConnectionException(detail=f"Failed to fetch menu item: {str(e)}")

    def get_order_by_sequence_id(self, order_sequence_id: int) -> Optional[OrderSchema]:
        try:
            with get_db() as session:
                order = session.query(OrderSchema).filter(
                    OrderSchema.order_sequence_id == order_sequence_id
                ).first()
                if order:
                    session.expunge(order)
                return order
        except DatabaseConnectionException:
            raise
        except Exception as e:
            raise DatabaseConnectionException(detail=f"Failed to fetch order: {str(e)}")

    def create_order(self, customer_name: str, status: str = "PENDING") -> OrderSchema:
        try:
            with get_db() as session:
                order = OrderSchema(
                    customer_name=customer_name,
                    status=status,
                    created_by="system",
                    updated_by="system"
                )
                session.add(order)
                session.commit()
                session.refresh(order)
                session.expunge(order)
                return order
        except DatabaseConnectionException:
            raise
        except Exception as e:
            raise DatabaseConnectionException(detail=f"Failed to create order: {str(e)}")

    def create_order_items(self, order_id: str, items: list) -> None:
        try:
            with get_db() as session:
                for item in items:
                    record = OrderItemSchema(
                        order_id=order_id,
                        menu_item_id=item["menu_item_id"],
                        quantity=item["quantity"],
                        created_by="system",
                        updated_by="system"
                    )
                    session.add(record)
                session.commit()
        except DatabaseConnectionException:
            raise
        except Exception as e:
            raise DatabaseConnectionException(detail=f"Failed to create order items: {str(e)}")

    def reduce_stock(self, menu_item_id: int, quantity: int) -> None:
        try:
            with get_db() as session:
                item = session.query(MenuItemSchema).filter(
                    MenuItemSchema.menu_item_id == menu_item_id
                ).first()
                if not item:
                    return
                item.stock_quantity = max(item.stock_quantity - quantity, 0)
                session.commit()
        except DatabaseConnectionException:
            raise
        except Exception as e:
            raise DatabaseConnectionException(detail=f"Failed to update stock: {str(e)}")
