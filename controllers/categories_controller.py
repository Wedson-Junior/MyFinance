from PySide6.QtCore import QObject

from models.user import User
from services.category_service import CategoryService, SYSTEM_CATEGORY_NAMES
from views.categories_view import CategoriesView


class CategoriesController(QObject):
    def __init__(
        self,
        view: CategoriesView,
        category_service: CategoryService,
        current_user: User,
    ) -> None:
        super().__init__()
        self._view = view
        self._category_service = category_service
        self._current_user = current_user
        self._connect_signals()
        self.refresh()

    def _connect_signals(self) -> None:
        self._view.save_requested.connect(self._handle_save)
        self._view.update_requested.connect(self._handle_update)
        self._view.delete_requested.connect(self._handle_delete)
        self._view.clear_requested.connect(self._view.clear_form)

    def refresh(self) -> None:
        categories = self._category_service.get_by_user(
            self._current_user.id, include_system=False
        )
        self._view.load_categories(categories)

    def _handle_save(self, name: str, category_type: str, color: str) -> None:
        self._view.clear_error()

        if not name:
            self._view.show_error("Informe o nome da categoria.")
            return

        if category_type not in ("income", "expense"):
            self._view.show_error("Tipo inválido.")
            return

        if name in SYSTEM_CATEGORY_NAMES:
            self._view.show_error("Este nome é reservado para o sistema.")
            return

        category = self._category_service.create(
            user_id=self._current_user.id,
            name=name,
            type=category_type,
            color=color if color else None,
        )

        if category is None:
            self._view.show_error("Erro ao criar categoria.")
            return

        self._view.show_success()
        self.refresh()

    def _handle_update(self, category_id: int, name: str, category_type: str, color: str) -> None:
        self._view.clear_error()

        if not name:
            self._view.show_error("Informe o nome da categoria.")
            return

        if category_type not in ("income", "expense"):
            self._view.show_error("Tipo inválido.")
            return

        existing = self._category_service.get_by_id(category_id)
        if existing is None:
            self._view.show_error("Categoria não encontrada.")
            return

        if self._category_service.is_system_category(existing):
            self._view.show_error("Categoria de sistema não pode ser editada.")
            return

        if name in SYSTEM_CATEGORY_NAMES:
            self._view.show_error("Este nome é reservado para o sistema.")
            return

        existing.name = name
        existing.type = category_type
        existing.color = color if color else None
        self._category_service.update(existing)

        self._view.show_success()
        self.refresh()

    def _handle_delete(self, category_id: int) -> None:
        self._view.clear_error()
        existing = self._category_service.get_by_id(category_id)
        if existing is not None and self._category_service.is_system_category(existing):
            self._view.show_error("Categoria de sistema não pode ser excluída.")
            return
        self._category_service.delete(category_id)
        self._view.clear_form()
        self.refresh()
