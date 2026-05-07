# task3_bank_account.py
"""
Модуль с классом BankAccount: приватное поле __balance, доступ через property,
валидация через декоратор, магические методы __repr__ и __str__.
"""

from functools import wraps


def check_positive(func):
    """
    Декоратор для методов, принимающих сумму: проверяет, что сумма > 0.
    """
    @wraps(func)
    def wrapper(self, amount):
        if amount <= 0:
            raise ValueError(f"Сумма должна быть положительной, получено: {amount}")
        return func(self, amount)
    return wrapper


class BankAccount:
    """Банковский счёт с контролем неотрицательного баланса."""

    def __init__(self, initial_balance: float = 0.0):
        self.__balance = 0.0  # приватное поле
        if initial_balance > 0:
            self.balance = initial_balance   # используем setter с проверкой

    @property
    def balance(self) -> float:
        """Геттер: возвращает текущий баланс."""
        return self.__balance

    @balance.setter
    @check_positive
    def balance(self, amount: float):
        """Сеттер: позволяет присвоить баланс только если amount > 0."""
        self.__balance = amount

    @check_positive
    def deposit(self, amount: float) -> None:
        """Пополнить счёт на положительную сумму."""
        self.__balance += amount

    @check_positive
    def withdraw(self, amount: float) -> bool:
        """
        Снять сумму со счёта, если достаточно средств.
        Возвращает True при успехе, False — если недостаточно денег.
        """
        if amount > self.__balance:
            return False
        self.__balance -= amount
        return True

    def __repr__(self) -> str:
        """Формальное представление для отладки."""
        return f"BankAccount(balance={self.__balance:.2f})"

    def __str__(self) -> str:
        """Дружелюбное представление для пользователя."""
        return f"Баланс счёта: {self.__balance:.2f} руб."


if __name__ == "__main__":
    print("=== Тестируем BankAccount ===\n")

    # Создание
    acc = BankAccount()
    print(f"Новый счёт: {acc}")
    print(f"repr: {repr(acc)}")

    # Пополнение и снятие
    acc.deposit(1000)
    print(f"После пополнения на 1000: {acc}")
    acc.withdraw(350)
    print(f"После снятия 350: {acc}")

    # Валидация
    print("\nПроверка валидации:")
    try:
        acc.deposit(-50)
    except ValueError as e:
        print(f"  Пополнение на -50: {e}")
    try:
        acc.balance = -100
    except ValueError as e:
        print(f"  Установка баланса -100: {e}")

    # Снятие при недостатке средств
    acc2 = BankAccount(200)
    print(f"\nСчёт с 200 руб.: {acc2}")
    success = acc2.withdraw(500)
    print(f"Попытка снять 500: {'успешно' if success else 'отказано'}, баланс: {acc2}")
    success = acc2.withdraw(150)
    print(f"Снятие 150: {'успешно' if success else 'отказано'}, баланс: {acc2}")

    print("\nВсе тесты пройдены!")
