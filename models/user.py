from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    id: Optional[int]
    username: str
    password_hash: str
    full_name: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None