from typing import Optional, List

from database.database_manager import DatabaseManager
from models.category import Category

SYSTEM_CATEGORY_NAMES = frozenset({"Saldo inicial"})


class CategoryService:
    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def create(
        self,
        user_id: int,
        name: str,
        type: str,
        color: Optional[str] = None,
        icon: Optional[str] = None,
    ) -> Optional[Category]:
        self._db.execute(
            """
            INSERT INTO categories (user_id, name, type, color, icon)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, name, type, color, icon),
        )
        row = self._db.fetch_one(
            "SELECT * FROM categories WHERE user_id = ? AND name = ? ORDER BY id DESC LIMIT 1",
            (user_id, name),
        )
        return self._row_to_category(row) if row else None

    def get_by_id(self, category_id: int) -> Optional[Category]:
        row = self._db.fetch_one(
            "SELECT * FROM categories WHERE id = ?",
            (category_id,),
        )
        return self._row_to_category(row) if row else None

    def get_by_user(
        self,
        user_id: int,
        type: Optional[str] = None,
        include_system: bool = False,
    ) -> List[Category]:
        if type:
            rows = self._db.fetch_all(
                "SELECT * FROM categories WHERE user_id = ? AND type = ? AND is_active = 1 ORDER BY name",
                (user_id, type),
            )
        else:
            rows = self._db.fetch_all(
                "SELECT * FROM categories WHERE user_id = ? AND is_active = 1 ORDER BY name",
                (user_id,),
            )
        categories = [self._row_to_category(row) for row in rows]
        if not include_system:
            categories = [c for c in categories if c.name not in SYSTEM_CATEGORY_NAMES]
        return categories

    def get_or_create(
        self,
        user_id: int,
        name: str,
        type: str,
        color: Optional[str] = None,
    ) -> Optional[Category]:
        row = self._db.fetch_one(
            """
            SELECT * FROM categories
            WHERE user_id = ? AND name = ? AND type = ? AND is_active = 1
            LIMIT 1
            """,
            (user_id, name, type),
        )
        if row:
            return self._row_to_category(row)
        return self.create(user_id=user_id, name=name, type=type, color=color)

    def is_system_category(self, category: Category) -> bool:
        return category.name in SYSTEM_CATEGORY_NAMES

    def update(self, category: Category) -> bool:
        if category.name in SYSTEM_CATEGORY_NAMES:
            return False
        self._db.execute(
            """
            UPDATE categories
            SET name = ?, type = ?, color = ?, icon = ?, is_active = ?, updated_at = datetime('now')
            WHERE id = ?
            """,
            (category.name, category.type, category.color, category.icon, int(category.is_active), category.id),
        )
        return True

    def delete(self, category_id: int) -> bool:
        existing = self.get_by_id(category_id)
        if existing is not None and existing.name in SYSTEM_CATEGORY_NAMES:
            return False
        self._db.execute(
            "UPDATE categories SET is_active = 0, updated_at = datetime('now') WHERE id = ?",
            (category_id,),
        )
        return True

    def _row_to_category(self, row) -> Category:
        return Category(
            id=row["id"],
            user_id=row["user_id"],
            name=row["name"],
            type=row["type"],
            color=row["color"],
            icon=row["icon"],
            is_active=bool(row["is_active"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
