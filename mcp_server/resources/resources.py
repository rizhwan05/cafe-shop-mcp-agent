from mcp.server.fastmcp import FastMCP

from repositories.coffee_repository import CoffeeRepository
from utils.exceptions.custom_exceptions import AppBaseException
from utils.exceptions.error_codes import ErrorCode, ErrorCodeStatus
from utils.logging_utils import log_and_raise
from settings import settings

repo = CoffeeRepository()


def register_resources(mcp: FastMCP) -> None:

    @mcp.resource("menu://items")
    def get_menu_resource() -> str:
        """
        Returns all active menu items from Bean & Brew as a formatted string.
        Includes name, description, price in rupees, and stock availability.
        Provides menu context for the agent alongside the check_menu tool.
        """
        try:
            items = repo.get_menu_items(active_only=True)
            lines = []
            for item in items:
                status = "In Stock" if item.stock_quantity > 0 else "Out of Stock"
                lines.append(
                    f"- {item.name}: {item.description} | Rs. {float(item.price)} | {status}"
                )
            return "Bean & Brew Menu:\n" + "\n".join(lines)
        except AppBaseException as exc:
            log_and_raise(exc, source="resources.get_menu_resource")
        except Exception as exc:
            log_and_raise(
                AppBaseException(
                    error_code=ErrorCodeStatus.get(ErrorCode.INTERNAL_SERVER_ERROR, "BB_SYS_001"),
                    message=f"Failed to fetch menu resource: {str(exc)}",
                    status_code=settings.http_internal_server_error,
                ),
                source="resources.get_menu_resource",
            )

    @mcp.resource("store://info")
    def get_store_info() -> str:
        """
        Returns static Bean & Brew store information.
        Includes opening hours, location, contact details, and policies.
        Read this resource when the customer asks about store details.
        """
        return """Bean & Brew - Store Information

Location: 42 Coffee Lane, Brew District, Chennai - 600001

Opening Hours:
- Monday to Friday: 7:00 AM - 10:00 PM
- Saturday: 8:00 AM - 11:00 PM
- Sunday: 9:00 AM - 9:00 PM

Contact:
- Phone: +91 98765 43210
- Email: hello@beanandbrew.in
- Instagram: @beanandbrew_cafe

Policies:
- Orders are prepared fresh and cannot be cancelled once placed
- We accept UPI, cards, and cash
- Loyalty points are awarded on every order
- Allergen information available on request
"""
