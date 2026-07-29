from dataclasses import dataclass
from typing import Optional


@dataclass
class Transaction:
    id: Optional[int]
    user_id: int
    account_id: int
    category_id: int
    type: str
    amount: float
    description: Optional[str] = None
    date: str = ""
    is_recurring: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None