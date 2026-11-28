import hashlib
import hmac
import secrets

import db


def _hash_password(password: str, salt: str) -> str:
    return hashlib.sha256((password + salt).encode("utf-8")).hexdigest()


def register(login: str, password: str) -> None:
    # secrets вместо random — криптостойкая соль
    salt = secrets.token_hex(16)
    pwd_hash = _hash_password(password, salt)

    # стандартный метод создания строки из db.py
    if db.create_user(login, salt, pwd_hash):
        print(f"Успех: {login} зарегистрирован")
    else:
        print(f"Ошибка: Логин {login} уже занят")


def login_user(login: str, password: str) -> None:
    user = db.get_user(login)
    if user is None:
        print("Ошибка: Неверный логин или пароль")
        return

    new_hash = _hash_password(password, user["salt"])
    if hmac.compare_digest(new_hash, user["password_hash"]):
        print(f"Успех: Добро пожаловать, {login}!")
    else:
        print("Ошибка: Неверный логин или пароль")


if __name__ == "__main__":
    db.run_migrations()          # накатывает migrations/001_*.sql при первом запуске

    register("admin", "12345")
    register("user", "12345")    # тот же пароль — разные соли
    register("admin", "12345")   # занят

    login_user("admin", "12345") # Успех
    login_user("admin", "wrong") # Ошибка