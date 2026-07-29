from dataclasses import dataclass
from typing import Optional


@dataclass
class Category:
    id: Optional[int]
    user_id: int
    name: str
    type: str
    color: Optional[str] = None
    icon: Optional[str] = None
    is_active: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None