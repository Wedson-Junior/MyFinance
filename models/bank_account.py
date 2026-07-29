from dataclasses import dataclass
from typing import Optional


@dataclass
class BankAccount:
    id: Optional[int]
    user_id: int
    name: str
    balance: float = 0.0
    currency: str = "BRL"
    is_active: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None