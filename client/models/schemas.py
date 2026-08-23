from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str
    mode: str = "normal"
    stream: bool = False
    thread_id: str = "default"


class OrderItem(BaseModel):
    item: str = Field(description="Exact name of the menu item as returned by check_menu tool")
    quantity: int = Field(description="Number of units ordered, must be greater than 0", gt=0)
    price: Optional[float] = Field(
        default=None,
        description="Price per unit in rupees as returned by check_menu tool"
    )


class OrderDetails(BaseModel):
    customer_name: Optional[str] = Field(
        description="Name of the customer placing the order"
    )
    items: List[OrderItem] = Field(description="List of ordered items with name, quantity and unit price")


class PendingApproval(BaseModel):
    tool: str = Field(description="Name of the tool awaiting approval")
    args: Dict[str, Any] = Field(description="Arguments the agent wants to call the tool with")
    description: str = Field(description="Human-readable description of the pending action")


class ChatResponse(BaseModel):
    message: str
    structured_output: Optional[OrderDetails] = None
    stream_chunks: Optional[List[str]] = None
    pending_approval: Optional[PendingApproval] = None
