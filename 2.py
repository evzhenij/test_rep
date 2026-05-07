# task2_decorators_chars.py
"""
Модуль с функцией поиска первого неповторяющегося символа и декораторами логирования/повторов.
"""

import time
from collections import Counter
from functools import wraps
from datetime import datetime
from typing import Any, Callable


def log_calls(log_file: str = "calls.log"):
    """
    Декоратор: записывает в файл имя функции, аргументы, результат, время выполнения и статус.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            # Формируем запись лога в виде строки (без json, чтобы не было лишних зависимостей)
            timestamp = datetime.now().isoformat()
            func_name = func.__name__
            args_str = f"args={args}, kwargs={kwargs}"
            status = "OK"
            result = None
            error_msg = ""

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                status = "ERROR"
                error_msg = str(e)
                raise
            finally:
                duration = round(time.time() - start, 4)
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(f"[{timestamp}] {func_name} | {args_str} | "
                            f"result={result} | {duration}s | {status}")
                    if error_msg:
                        f.write(f" | {error_msg}")
                    f.write("\n")
        return wrapper
    return decorator


def retry(attempts: int = 3, delay: float = 1.0):
    """
    Декоратор: повторяет вызов функции до attempts раз при возникновении исключения.
    Между попытками — задержка delay секунд.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < attempts:
                        time.sleep(delay)
                    else:
                        raise last_exception
            return None  # никогда не сработает, но для формальности
        return wrapper
    return decorator


def first_unique_char(s: str) -> int:
    """
    Возвращает индекс первого символа, который не повторяется в строке.
    Если такого нет — возвращает -1.
    Сложность: O(n) по времени, O(k) по памяти (k — размер алфавита).
    """
    if not s:
        return -1

    # Считаем частоты символов
    freq = Counter(s)

    # Ищем первый символ с частотой 1
    for i, ch in enumerate(s):
        if freq[ch] == 1:
            return i
    return -1


# Пример использования декораторов
@log_calls()
@retry(attempts=2, delay=0.5)
def find_unique_index(text: str) -> int:
    """Оборачивает first_unique_char с логированием и повторами."""
    return first_unique_char(text)


if __name__ == "__main__":
    print("Тестируем first_unique_char...")
    assert first_unique_char("leetcode") == 0
    assert first_unique_char("loveleetcode") == 2
    assert first_unique_char("aabb") == -1
    assert first_unique_char("") == -1
    print("OK")

    print("\nТестируем декораторы...")
    # Вызываем обёрнутую функцию — лог запишется в calls.log
    print(find_unique_index("swiss"))      # 's' повторяется, первый уникальный 'w' на индексе 1? Нет: s(0), w(1) -> 1
    print(find_unique_index("aabbcc"))     # -1
    print(find_unique_index("abcde"))      # 0

    # Покажем содержимое лога (последние записи)
    print("\nПоследние строки лога calls.log:")
    try:
        with open("calls.log", "r") as f:
            lines = f.readlines()
            for line in lines[-3:]:
                print("  " + line.strip())
    except FileNotFoundError:
        print("  Лог-файл не найден — он будет создан при первом вызове.")
