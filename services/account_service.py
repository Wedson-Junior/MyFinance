from typing import Optional, List

from database.database_manager import DatabaseManager
from models.bank_account import BankAccount


class AccountService:
    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def create(self, user_id: int, name: str, balance: float = 0.0, currency: str = "BRL") -> Optional[BankAccount]:
        self._db.execute(
            """
            INSERT INTO bank_accounts (user_id, name, balance, currency)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, name, balance, currency),
        )
        row = self._db.fetch_one(
            "SELECT * FROM bank_accounts WHERE user_id = ? AND name = ? ORDER BY id DESC LIMIT 1",
            (user_id, name),
        )
        return self._row_to_account(row) if row else None

    def get_by_id(self, account_id: int) -> Optional[BankAccount]:
        row = self._db.fetch_one(
            "SELECT * FROM bank_accounts WHERE id = ?",
            (account_id,),
        )
        return self._row_to_account(row) if row else None

    def get_by_user(self, user_id: int) -> List[BankAccount]:
        rows = self._db.fetch_all(
            "SELECT * FROM bank_accounts WHERE user_id = ? AND is_active = 1 ORDER BY name",
            (user_id,),
        )
        return [self._row_to_account(row) for row in rows]

    def update(self, account: BankAccount) -> bool:
        self._db.execute(
            """
            UPDATE bank_accounts
            SET name = ?, balance = ?, currency = ?, is_active = ?, updated_at = datetime('now')
            WHERE id = ?
            """,
            (account.name, account.balance, account.currency, int(account.is_active), account.id),
        )
        return True

    def delete(self, account_id: int) -> bool:
        self._db.execute(
            "UPDATE bank_accounts SET is_active = 0, updated_at = datetime('now') WHERE id = ?",
            (account_id,),
        )
        return True

    def update_balance(self, account_id: int, amount: float) -> bool:
        self._db.execute(
            """
            UPDATE bank_accounts
            SET balance = balance + ?, updated_at = datetime('now')
            WHERE id = ?
            """,
            (amount, account_id),
        )
        return True

    def _row_to_account(self, row) -> BankAccount:
        return BankAccount(
            id=row["id"],
            user_id=row["user_id"],
            name=row["name"],
            balance=row["balance"],
            currency=row["currency"],
            is_active=bool(row["is_active"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )