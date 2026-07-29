import hashlib
from typing import Optional

from PySide6.QtCore import QObject, Signal

from models.user import User
from services.user_service import UserService
from views.login_view import LoginView


class LoginController(QObject):
    login_success = Signal(object)

    def __init__(self, view: LoginView, user_service: UserService) -> None:
        super().__init__()
        self._view = view
        self._user_service = user_service
        self._connect_signals()

    def _connect_signals(self) -> None:
        self._view.login_requested.connect(self._handle_login)
        self._view.register_requested.connect(self._handle_register)

    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def _handle_login(self, username: str, password: str) -> None:
        self._view.clear_error()

        if not username or not password:
            self._view.show_error("Preencha usuário e senha.")
            return

        password_hash = self._hash_password(password)
        user = self._user_service.authenticate(username, password_hash)

        if user is None:
            self._view.show_error("Usuário ou senha inválidos.")
            return

        self.login_success.emit(user)

    def _handle_register(self, username: str, password: str) -> None:
        self._view.clear_error()

        if not username or not password:
            self._view.show_error("Preencha usuário e senha.")
            return

        if len(password) < 4:
            self._view.show_error("A senha deve ter no mínimo 4 caracteres.")
            return

        existing = self._user_service.get_by_username(username)
        if existing is not None:
            self._view.show_error("Este usuário já existe.")
            return

        password_hash = self._hash_password(password)
        user = self._user_service.create(username, password_hash)

        if user is None:
            self._view.show_error("Erro ao criar conta.")
            return

        self.login_success.emit(user)