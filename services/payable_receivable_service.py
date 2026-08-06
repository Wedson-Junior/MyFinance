from datetime import date
from typing import Optional, List

from database.database_manager import DatabaseManager
from models.payable_receivable import PayableReceivable
from services.account_service import AccountService


class PayableReceivableService:
    def __init__(self, db: DatabaseManager) -> None:
        self._db = db
        self._account_service = AccountService(db)

    def create(
        self,
        user_id: int,
        type: str,
        description: str,
        original_amount: float,
        due_date: str,
        account_id: Optional[int] = None,
        category_id: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> Optional[PayableReceivable]:
        self._db.execute(
            """
            INSERT INTO payables_receivables
            (user_id, type, description, original_amount, paid_amount, remaining_amount,
             due_date, status, account_id, category_id, notes)
            VALUES (?, ?, ?, ?, 0, ?, ?, 'pending', ?, ?, ?)
            """,
            (
                user_id,
                type,
                description,
                original_amount,
                original_amount,
                due_date,
                account_id,
                category_id,
                notes,
            ),
        )
        row = self._db.fetch_one(
            """
            SELECT * FROM payables_receivables
            WHERE user_id = ? ORDER BY id DESC LIMIT 1
            """,
            (user_id,),
        )
        return self._row_to_item(row) if row else None

    def get_by_id(self, item_id: int) -> Optional[PayableReceivable]:
        row = self._db.fetch_one(
            "SELECT * FROM payables_receivables WHERE id = ?",
            (item_id,),
        )
        return self._row_to_item(row) if row else None

    def get_by_user(self, user_id: int, type: Optional[str] = None) -> List[PayableReceivable]:
        if type:
            rows = self._db.fetch_all(
                """
                SELECT * FROM payables_receivables
                WHERE user_id = ? AND type = ?
                ORDER BY due_date ASC, id DESC
                """,
                (user_id, type),
            )
        else:
            rows = self._db.fetch_all(
                """
                SELECT * FROM payables_receivables
                WHERE user_id = ?
                ORDER BY due_date ASC, id DESC
                """,
                (user_id,),
            )
        return [self._apply_overdue(self._row_to_item(row)) for row in rows]

    def update(self, item: PayableReceivable) -> bool:
        self._db.execute(
            """
            UPDATE payables_receivables
            SET type = ?, description = ?, original_amount = ?, paid_amount = ?,
                remaining_amount = ?, due_date = ?, status = ?, account_id = ?,
                category_id = ?, notes = ?, updated_at = datetime('now')
            WHERE id = ?
            """,
            (
                item.type,
                item.description,
                item.original_amount,
                item.paid_amount,
                item.remaining_amount,
                item.due_date,
                item.status,
                item.account_id,
                item.category_id,
                item.notes,
                item.id,
            ),
        )
        return True

    def delete(self, item_id: int) -> bool:
        item = self.get_by_id(item_id)
        if item is None:
            return False

        rows = self._db.fetch_all(
            "SELECT * FROM transactions WHERE payable_receivable_id = ?",
            (item_id,),
        )
        for row in rows:
            amount = row["amount"]
            account_id = row["account_id"]
            tx_type = row["type"]
            if tx_type == "income":
                self._account_service.update_balance(account_id, -amount)
            else:
                self._account_service.update_balance(account_id, amount)

        self._db.execute(
            "DELETE FROM transactions WHERE payable_receivable_id = ?",
            (item_id,),
        )
        self._db.execute(
            "DELETE FROM payables_receivables WHERE id = ?",
            (item_id,),
        )
        return True

    def add_haver(
        self,
        item_id: int,
        user_id: int,
        account_id: int,
        category_id: int,
        amount: float,
        payment_date: str,
        description: Optional[str] = None,
    ) -> bool:
        item = self.get_by_id(item_id)
        if item is None or item.status == "cancelled":
            return False
        if amount <= 0:
            return False
        if amount > item.remaining_amount + 0.0001:
            return False

        tx_type = "expense" if item.type == "payable" else "income"
        note = description or f"Haver: {item.description}"

        self._db.execute(
            """
            INSERT INTO transactions
            (user_id, account_id, category_id, type, amount, description, date,
             is_recurring, payable_receivable_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?)
            """,
            (user_id, account_id, category_id, tx_type, amount, note, payment_date, item_id),
        )

        if tx_type == "income":
            self._account_service.update_balance(account_id, amount)
        else:
            self._account_service.update_balance(account_id, -amount)

        self.refresh_amounts(item_id)
        return True

    def refresh_amounts(self, item_id: int) -> None:
        item = self.get_by_id(item_id)
        if item is None:
            return

        row = self._db.fetch_one(
            """
            SELECT COALESCE(SUM(amount), 0) AS total
            FROM transactions
            WHERE payable_receivable_id = ?
            """,
            (item_id,),
        )
        paid = float(row["total"]) if row else 0.0
        remaining = max(item.original_amount - paid, 0.0)

        if item.status == "cancelled":
            status = "cancelled"
        elif paid <= 0:
            status = "pending"
        elif remaining <= 0.0001:
            status = "settled"
            remaining = 0.0
        else:
            status = "partial"

        if status not in ("settled", "cancelled") and item.due_date:
            try:
                if date.fromisoformat(item.due_date) < date.today() and remaining > 0:
                    status = "overdue"
            except ValueError:
                pass

        self._db.execute(
            """
            UPDATE payables_receivables
            SET paid_amount = ?, remaining_amount = ?, status = ?,
                updated_at = datetime('now')
            WHERE id = ?
            """,
            (paid, remaining, status, item_id),
        )

    def recalculate_all(self, user_id: int) -> None:
        items = self.get_by_user(user_id)
        for item in items:
            if item.id is not None:
                self.refresh_amounts(item.id)

    def _apply_overdue(self, item: PayableReceivable) -> PayableReceivable:
        if item.status in ("settled", "cancelled"):
            return item
        if not item.due_date:
            return item
        try:
            if date.fromisoformat(item.due_date) < date.today() and item.remaining_amount > 0:
                item.status = "overdue"
        except ValueError:
            pass
        return item

    def _row_to_item(self, row) -> PayableReceivable:
        return PayableReceivable(
            id=row["id"],
            user_id=row["user_id"],
            type=row["type"],
            description=row["description"],
            original_amount=row["original_amount"],
            paid_amount=row["paid_amount"],
            remaining_amount=row["remaining_amount"],
            due_date=row["due_date"],
            status=row["status"],
            account_id=row["account_id"],
            category_id=row["category_id"],
            notes=row["notes"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
