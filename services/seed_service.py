from typing import List, Tuple

from services.category_service import CategoryService

DEFAULT_CATEGORIES: List[Tuple[str, str, str]] = [
    ("Salário", "income", "#38A169"),
    ("Freelance", "income", "#3182CE"),
    ("Investimentos", "income", "#805AD5"),
    ("Presentes", "income", "#D69E2E"),
    ("Outras receitas", "income", "#718096"),
    ("Moradia", "expense", "#E53E3E"),
    ("Alimentação", "expense", "#DD6B20"),
    ("Transporte", "expense", "#3182CE"),
    ("Saúde", "expense", "#38A169"),
    ("Educação", "expense", "#805AD5"),
    ("Lazer", "expense", "#D53F8C"),
    ("Contas", "expense", "#DD6B20"),
    ("Compras", "expense", "#E53E3E"),
    ("Outras despesas", "expense", "#718096"),
]


class SeedService:
    def __init__(self, category_service: CategoryService) -> None:
        self._category_service = category_service

    def seed_user_defaults(self, user_id: int) -> None:
        for name, category_type, color in DEFAULT_CATEGORIES:
            self._category_service.get_or_create(
                user_id=user_id,
                name=name,
                type=category_type,
                color=color,
            )

    def seed_if_empty(self, user_id: int) -> None:
        existing = self._category_service.get_by_user(user_id, include_system=False)
        if not existing:
            self.seed_user_defaults(user_id)
