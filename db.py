import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "app.db"
MIGRATIONS_DIR = BASE_DIR / "migrations"


def get_connection() -> sqlite3.Connection:
    """Открывает соединение с SQLite (словари вместо кортежей)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def run_migrations() -> None:
    """Применяет все *.sql из migrations/ по порядку, один раз каждый."""
    conn = get_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                name       TEXT PRIMARY KEY,
                applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        applied = {r["name"] for r in conn.execute("SELECT name FROM schema_migrations")}

        for sql_file in sorted(MIGRATIONS_DIR.glob("*.sql")):
            if sql_file.name in applied:
                continue
            conn.executescript(sql_file.read_text(encoding="utf-8"))
            conn.execute("INSERT INTO schema_migrations(name) VALUES (?)", (sql_file.name,))
            conn.commit()
            print(f"[db] применена миграция: {sql_file.name}")
    finally:
        conn.close()


# === СТАНДАРТНЫЙ МЕТОД СОЗДАНИЯ СТРОКИ ПОЛЬЗОВАТЕЛЯ ===
def create_user(login: str, salt: str, password_hash: str) -> bool:
    """
    Создаёт строку пользователя.
    Возвращает True — если создана, False — если логин уже занят.
    Все значения передаются через параметры (?) — защита от SQL-инъекций.
    """
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (login, salt, password_hash) VALUES (?, ?, ?)",
            (login, salt, password_hash),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Нарушено UNIQUE(login)
        return False
    finally:
        conn.close()


# === СТАНДАРТНЫЙ МЕТОД ЧТЕНИЯ СТРОКИ ===
def get_user(login: str) -> dict | None:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT login, salt, password_hash FROM users WHERE login = ?",
            (login,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()