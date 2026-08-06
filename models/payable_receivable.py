from dataclasses import dataclass
from typing import Optional


@dataclass
class PayableReceivable:
    id: Optional[int]
    user_id: int
    type: str
    description: str
    original_amount: float
    paid_amount: float = 0.0
    remaining_amount: float = 0.0
    due_date: str = ""
    status: str = "pending"
    account_id: Optional[int] = None
    category_id: Optional[int] = None
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
