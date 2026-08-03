from typing import Optional, List

from database.database_manager import DatabaseManager
from models.transaction import Transaction
from services.account_service import AccountService


class TransactionService:
    def __init__(self, db: DatabaseManager) -> None:
        self._db = db
        self._account_service = AccountService(db)

    def create(
        self,
        user_id: int,
        account_id: int,
        category_id: int,
        type: str,
        amount: float,
        description: Optional[str] = None,
        date: str = "",
        is_recurring: bool = False,
    ) -> Optional[Transaction]:
        self._db.execute(
            """
            INSERT INTO transactions
            (user_id, account_id, category_id, type, amount, description, date, is_recurring)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, account_id, category_id, type, amount, description, date, int(is_recurring)),
        )

        if type == "income":
            self._account_service.update_balance(account_id, amount)
        else:
            self._account_service.update_balance(account_id, -amount)

        row = self._db.fetch_one(
            "SELECT * FROM transactions WHERE user_id = ? ORDER BY id DESC LIMIT 1",
            (user_id,),
        )
        return self._row_to_transaction(row) if row else None

    def get_by_id(self, transaction_id: int) -> Optional[Transaction]:
        row = self._db.fetch_one(
            "SELECT * FROM transactions WHERE id = ?",
            (transaction_id,),
        )
        return self._row_to_transaction(row) if row else None

    def get_by_user(self, user_id: int) -> List[Transaction]:
        rows = self._db.fetch_all(
            "SELECT * FROM transactions WHERE user_id = ? ORDER BY date DESC, id DESC",
            (user_id,),
        )
        return [self._row_to_transaction(row) for row in rows]

    def get_by_account(self, account_id: int) -> List[Transaction]:
        rows = self._db.fetch_all(
            "SELECT * FROM transactions WHERE account_id = ? ORDER BY date DESC, id DESC",
            (account_id,),
        )
        return [self._row_to_transaction(row) for row in rows]

    def update(self, transaction: Transaction) -> bool:
        old = self.get_by_id(transaction.id)
        if not old:
            return False

        if old.type == "income":
            self._account_service.update_balance(old.account_id, -old.amount)
        else:
            self._account_service.update_balance(old.account_id, old.amount)

        self._db.execute(
            """
            UPDATE transactions
            SET account_id = ?, category_id = ?, type = ?, amount = ?,
                description = ?, date = ?, is_recurring = ?, updated_at = datetime('now')
            WHERE id = ?
            """,
            (
                transaction.account_id,
                transaction.category_id,
                transaction.type,
                transaction.amount,
                transaction.description,
                transaction.date,
                int(transaction.is_recurring),
                transaction.id,
            ),
        )

        if transaction.type == "income":
            self._account_service.update_balance(transaction.account_id, transaction.amount)
        else:
            self._account_service.update_balance(transaction.account_id, -transaction.amount)

        return True

    def delete(self, transaction_id: int) -> bool:
        transaction = self.get_by_id(transaction_id)
        if not transaction:
            return False

        if transaction.type == "income":
            self._account_service.update_balance(transaction.account_id, -transaction.amount)
        else:
            self._account_service.update_balance(transaction.account_id, transaction.amount)

        self._db.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
        return True

    def delete_by_account(self, account_id: int) -> int:
        rows = self._db.fetch_all(
            "SELECT id FROM transactions WHERE account_id = ?",
            (account_id,),
        )
        self._db.execute(
            "DELETE FROM transactions WHERE account_id = ?",
            (account_id,),
        )
        return len(rows)

    def _row_to_transaction(self, row) -> Transaction:
        return Transaction(
            id=row["id"],
            user_id=row["user_id"],
            account_id=row["account_id"],
            category_id=row["category_id"],
            type=row["type"],
            amount=row["amount"],
            description=row["description"],
            date=row["date"],
            is_recurring=bool(row["is_recurring"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )