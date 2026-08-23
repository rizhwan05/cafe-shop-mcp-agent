from typing import Any, Dict, List
from mcp.server.fastmcp import FastMCP

from repositories.coffee_repository import CoffeeRepository
from utils.exceptions.custom_exceptions import (
    AppBaseException,
    MenuItemNotFoundException,
    OrderNotFoundException,
    InsufficientStockException,
    InvalidRequestException,
)
from utils.exceptions.error_codes import ErrorCode, ErrorCodeStatus
from utils.logging_utils import log_and_raise
from settings import settings

repo = CoffeeRepository()

# FastMCP instance — all tools registered here with @mcp.tool() decorators
mcp = FastMCP("bean-brew-tools-server")


@mcp.tool()
def check_menu() -> Dict:
    """
    Fetch all active menu items from Bean & Brew, including stock availability.
    Use this whenever the customer asks about drinks, prices, recommendations,
    or whether a specific item is available or in stock.

    Arguments: None

    Returns:
        {
            "items": [
                {
                    "name": str,             # Name of the drink
                    "description": str,      # Short description
                    "price": float,          # Price in rupees
                    "in_stock": bool,        # True if stock_quantity > 0
                    "stock_quantity": int    # Exact number of units available
                }
            ]
        }
    """
    try:
        items = repo.get_menu_items(active_only=True)
        return {
            "items": [
                {
                    "name": item.name,
                    "description": item.description,
                    "price": float(item.price),
                    "in_stock": item.stock_quantity > 0,
                    "stock_quantity": item.stock_quantity,
                }
                for item in items
            ]
        }
    except AppBaseException as exc:
        log_and_raise(exc, source="tools.check_menu")
    except Exception as exc:
        log_and_raise(
            AppBaseException(
                error_code=ErrorCodeStatus.get(ErrorCode.INTERNAL_SERVER_ERROR, "BB_SYS_001"),
                message=f"Failed to fetch menu: {str(exc)}",
                status_code=settings.http_internal_server_error,
            ),
            source="tools.check_menu",
        )


@mcp.tool()
def check_order_status(order_sequence_id: int) -> Dict:
    """
    Look up the current status of an order using its sequence ID.
    Use when the customer provides an order number and asks about their order status.
    Always use the integer order_sequence_id, never the UUID order_id.

    Arguments:
        order_sequence_id (int): The simple integer order reference number (e.g. 1, 2, 3).

    Returns:
        {
            "order_sequence_id": int,  # The integer reference number
            "order_id": str,           # Internal UUID of the order
            "status": str              # Current status e.g. PENDING, PROCESSED
        }
    """
    try:
        order = repo.get_order_by_sequence_id(order_sequence_id)
        if not order:
            raise OrderNotFoundException(str(order_sequence_id))
        return {
            "order_sequence_id": order.order_sequence_id,
            "order_id": str(order.order_id),
            "status": order.status,
        }
    except AppBaseException as exc:
        log_and_raise(exc, source="tools.check_order_status")
    except Exception as exc:
        log_and_raise(
            AppBaseException(
                error_code=ErrorCodeStatus.get(ErrorCode.INTERNAL_SERVER_ERROR, "BB_SYS_001"),
                message=f"Failed to check order status: {str(exc)}",
                status_code=settings.http_internal_server_error,
            ),
            source="tools.check_order_status",
        )


@mcp.tool()
def add_order(customer_name: str, items: List[Dict[str, Any]]) -> Dict:
    """
    Place a new order for a customer and reduce stock automatically.
    Only call this after confirming BOTH customer_name and at least one item with quantity.
    Only call this if ALL requested items exist in the menu returned by check_menu.
    If any item is not on the menu, do NOT call this tool. Inform the customer instead.
    Never substitute a different item without the customer's explicit confirmation.

    Arguments:
        customer_name (str): Full name of the customer placing the order.
        items (List[Dict]): List of items to order.
            Each item must have:
                - item_name (str): Exact menu item name (case-insensitive match).
                - quantity (int): Number of units, must be greater than 0.
            Example: [{"item_name": "Cappuccino", "quantity": 2}]

    Returns:
        {
            "order_id": str,           # Internal UUID of the created order
            "order_sequence_id": int,  # Integer reference number for the customer
            "status": str              # Order status after creation e.g. PROCESSED
        }
    """
    try:
        if not items:
            raise InvalidRequestException("Order items cannot be empty.")

        order_items = []
        for item in items:
            item_name = item.get("item_name")
            quantity = item.get("quantity")

            if not item_name or not isinstance(quantity, int) or quantity <= 0:
                raise InvalidRequestException("Each item must include item_name and quantity > 0.")

            menu_item = repo.get_menu_item_by_name(item_name)
            if not menu_item:
                raise MenuItemNotFoundException(item_name)
            if menu_item.stock_quantity < quantity:
                raise InsufficientStockException(menu_item.name, menu_item.stock_quantity)

            order_items.append({
                "menu_item_id": menu_item.menu_item_id,
                "quantity": quantity,
            })

        order = repo.create_order(customer_name=customer_name, status="PROCESSED")
        repo.create_order_items(order_id=str(order.order_id), items=order_items)
        for item in order_items:
            repo.reduce_stock(item["menu_item_id"], item["quantity"])

        return {
            "order_id": str(order.order_id),
            "order_sequence_id": order.order_sequence_id,
            "status": order.status,
        }
    except AppBaseException as exc:
        log_and_raise(exc, source="tools.add_order")
    except Exception as exc:
        log_and_raise(
            AppBaseException(
                error_code=ErrorCodeStatus.get(ErrorCode.INTERNAL_SERVER_ERROR, "BB_SYS_001"),
                message=f"Failed to place order: {str(exc)}",
                status_code=settings.http_internal_server_error,
            ),
            source="tools.add_order",
        )
