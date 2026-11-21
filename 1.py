import hashlib
import random

# Наша "База данных" (словарь)
db = {}

# 1. РЕГИСТРАЦИЯ
def register(login, password):
    if login in db:
        print(f"Ошибка: Логин {login} уже занят")
        return

    # Генерируем простую соль (случайное число от 1000 до 9999)
    salt = str(random.randint(1000, 9999))
    
    # СКЛЕИВАЕМ пароль и соль, затем хэшируем (строка -> байты -> хэш)
    # В Python пароль обязательно нужно перевести в байты (.encode)
    text_to_hash = password + salt
    pwd_hash = hashlib.sha256(text_to_hash.encode()).hexdigest()
    
    # Сохраняем логин, соль и хэш в БД
    db[login] = {
        "salt": salt,
        "hash": pwd_hash
    }
    print(f"Успех: {login} зарегистрирован")

# 2. АВТОРИЗАЦИЯ
def login_user(login, password):
    if login not in db:
        print("Ошибка: Неверный логин или пароль")
        return

    # Достаем соль и старый хэш из БД
    user_salt = db[login]["salt"]
    saved_hash = db[login]["hash"]

    # Берем введенный пароль, приклеиваем к нему СОЛЬ ИЗ БАЗЫ и хэшируем
    text_to_hash = password + user_salt
    new_hash = hashlib.sha256(text_to_hash.encode()).hexdigest()

    # Сравниваем хэши (обычное равенство ==)
    if new_hash == saved_hash:
        print(f"Успех: Добро пожаловать, {login}!")
    else:
        print("Ошибка: Неверный логин или пароль")

# --- ПРОВЕРКА ---
register("admin", "12345")
register("user", "12345") # Пароль такой же, но соль разная!
print("База данных:", db, "\n")

login_user("admin", "12345") # Успех
login_user("admin", "wrong") # Ошибка