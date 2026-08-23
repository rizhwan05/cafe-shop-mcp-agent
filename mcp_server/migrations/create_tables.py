from repositories.database import Base, engine, get_db
from repositories.schema.schema import MenuItemSchema, OrderSchema, OrderItemSchema, ErrorLogSchema


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)
    seed_data()


def seed_data() -> None:
    with get_db() as session:
        if session.query(MenuItemSchema).first():
            return

        menu_items = [
            MenuItemSchema(name="Espresso", description="Strong and bold espresso shot", price=180.00, stock_quantity=50, is_active=True, created_by="system", updated_by="system"),
            MenuItemSchema(name="Cappuccino", description="Espresso with steamed milk and foam", price=250.00, stock_quantity=40, is_active=True, created_by="system", updated_by="system"),
            MenuItemSchema(name="Latte", description="Smooth espresso with steamed milk", price=260.00, stock_quantity=35, is_active=True, created_by="system", updated_by="system"),
            MenuItemSchema(name="Iced Mocha", description="Chilled espresso with chocolate and milk", price=290.00, stock_quantity=25, is_active=True, created_by="system", updated_by="system"),
            MenuItemSchema(name="Cold Brew", description="Slow brewed coffee served cold", price=240.00, stock_quantity=30, is_active=True, created_by="system", updated_by="system"),
            MenuItemSchema(name="Matcha Latte", description="Green tea latte with milk", price=270.00, stock_quantity=20, is_active=True, created_by="system", updated_by="system"),
        ]
        session.add_all(menu_items)
        session.commit()
