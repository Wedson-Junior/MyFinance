from typing import Optional, List

from database.database_manager import DatabaseManager
from models.user import User


class UserService:
    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def create(self, username: str, password_hash: str, full_name: Optional[str] = None) -> Optional[User]:
        self._db.execute(
            """
            INSERT INTO users (username, password_hash, full_name)
            VALUES (?, ?, ?)
            """,
            (username, password_hash, full_name),
        )
        row = self._db.fetch_one(
            "SELECT * FROM users WHERE username = ?",
            (username,),
        )
        return self._row_to_user(row) if row else None

    def get_by_id(self, user_id: int) -> Optional[User]:
        row = self._db.fetch_one(
            "SELECT * FROM users WHERE id = ?",
            (user_id,),
        )
        return self._row_to_user(row) if row else None

    def get_by_username(self, username: str) -> Optional[User]:
        row = self._db.fetch_one(
            "SELECT * FROM users WHERE username = ?",
            (username,),
        )
        return self._row_to_user(row) if row else None

    def authenticate(self, username: str, password_hash: str) -> Optional[User]:
        row = self._db.fetch_one(
            "SELECT * FROM users WHERE username = ? AND password_hash = ?",
            (username, password_hash),
        )
        return self._row_to_user(row) if row else None

    def update(self, user: User) -> bool:
        self._db.execute(
            """
            UPDATE users
            SET username = ?, password_hash = ?, full_name = ?, updated_at = datetime('now')
            WHERE id = ?
            """,
            (user.username, user.password_hash, user.full_name, user.id),
        )
        return True

    def delete(self, user_id: int) -> bool:
        self._db.execute("DELETE FROM users WHERE id = ?", (user_id,))
        return True

    def _row_to_user(self, row) -> User:
        return User(
            id=row["id"],
            username=row["username"],
            password_hash=row["password_hash"],
            full_name=row["full_name"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )