# task4_sqlalchemy_core.py
"""
Модуль для работы с БД через SQLAlchemy Core (без ORM).
Таблицы: products (товары) и orders (заказы).
Реализована пакетная вставка данных и параметризованный запрос get_low_stock_products.
"""

from typing import List, Dict, Any
from sqlalchemy import (
    create_engine, MetaData, Table, Column, Integer, String, ForeignKey,
    UniqueConstraint, insert, select, bindparam
)

# -------------------------------------------------------------------
# 1. Описание таблиц с ForeignKey и ограничением уникальности
# -------------------------------------------------------------------
metadata = MetaData()

products = Table(
    'products', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(100), nullable=False),
    Column('article', String(50), nullable=False),          # артикул — уникален
    Column('stock_quantity', Integer, nullable=False),      # остаток на складе
    UniqueConstraint('article', name='uq_products_article') # ограничение уникальности
)

orders = Table(
    'orders', metadata,
    Column('id', Integer, primary_key=True),
    Column('product_id', Integer, ForeignKey('products.id'), nullable=False),
    Column('quantity', Integer, nullable=False),
    Column('customer_name', String(100), nullable=False)
)

# -------------------------------------------------------------------
# 2. Инициализация БД и пакетная вставка данных (executemany)
# -------------------------------------------------------------------
def init_db(db_url: str = "sqlite:///store.db", reset: bool = False):
    """
    Создаёт таблицы и заполняет их начальными данными.
    Пакетная вставка реализована через передачу списка словарей в execute(insert(...), data).
    """
    engine = create_engine(db_url)

    if reset:
        metadata.drop_all(engine)   # удаляем старые таблицы
    metadata.create_all(engine)     # создаём новые

    # Данные для товаров (пакетная вставка)
    products_data = [
        {"name": "Ноутбук", "article": "NB-001", "stock_quantity": 3},
        {"name": "Мышь", "article": "MS-002", "stock_quantity": 15},
        {"name": "Клавиатура", "article": "KB-003", "stock_quantity": 0},
        {"name": "Монитор", "article": "MN-004", "stock_quantity": 2},
    ]

    # Данные для заказов (пакетная вставка)
    orders_data = [
        {"product_id": 1, "quantity": 1, "customer_name": "Иванов И.И."},
        {"product_id": 2, "quantity": 2, "customer_name": "Петров П.П."},
        {"product_id": 1, "quantity": 1, "customer_name": "Сидоров С.С."},
        {"product_id": 3, "quantity": 1, "customer_name": "Кузнецова А.А."},
    ]

    with engine.connect() as conn:
        # Очищаем таблицы перед вставкой (чтобы при reset=True данные не дублировались)
        conn.execute(orders.delete())
        conn.execute(products.delete())

        # executemany внутри: передаём список словарей
        conn.execute(insert(products), products_data)
        conn.execute(insert(orders), orders_data)

        conn.commit()

    return engine

# -------------------------------------------------------------------
# 3. Функция get_low_stock_products (параметризованный запрос)
# -------------------------------------------------------------------
def get_low_stock_products(engine, threshold: int = 5) -> List[Dict[str, Any]]:
    """
    Возвращает список товаров, у которых stock_quantity < threshold.
    Запрос параметризован через bindparam.
    """
    # Используем bindparam для параметризации
    query = select(
        products.c.name,
        products.c.article,
        products.c.stock_quantity
    ).where(products.c.stock_quantity < bindparam('thr'))

    with engine.connect() as conn:
        result = conn.execute(query, {"thr": threshold})
        return [dict(row._mapping) for row in result]

# -------------------------------------------------------------------
# 4. Тесты (запускаются только при прямом исполнении)
# -------------------------------------------------------------------
if __name__ == "__main__":
    print("Инициализация БД (пересоздание таблиц)...")
    engine = init_db("sqlite:///store.db", reset=True)

    print("\nТовары с остатком меньше 5:")
    low_stock = get_low_stock_products(engine, threshold=5)
    for p in low_stock:
        print(f"  {p['name']} (арт. {p['article']}) — остаток: {p['stock_quantity']} шт.")

    print("\nТовары с остатком меньше 10:")
    very_low = get_low_stock_products(engine, threshold=10)
    for p in very_low:
        print(f"  {p['name']} (арт. {p['article']}) — остаток: {p['stock_quantity']} шт.")

    print("\n Все условия задания выполнены:")
    print("  - Таблицы через Table и MetaData")
    print("  - ForeignKey и UniqueConstraint присутствуют")
    print("  - Пакетная вставка (executemany)")
    print("  - Функция get_low_stock_products с параметризованным запросом (bindparam)")
