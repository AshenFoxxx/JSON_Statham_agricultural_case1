"""Демонстрационные данные при первом запуске."""
from sqlalchemy.orm import Session
from app import crud, models

FARM = ("Хозяйство Обнинск", 36.6103, 55.0969)

PRODUCTS = [
    ("strawberry", "Клубника", 800, 6),
    ("lettuce", "Салат", 500, 10),
    ("cucumber", "Огурцы", 1000, 18),
    ("tomato", "Томаты", 1200, 24),
]

BUYERS = [
    ("buyer-belousovo", "Белоусово", 36.668, 55.095),
    ("buyer-obninsk", "Рынок Обнинск", 36.5855, 55.112),
    ("buyer-maloyaroslavets", "Малоярославец", 36.471, 55.014),
    ("buyer-naro-fominsk", "Наро-Фоминск", 36.734, 55.387),
    ("buyer-kaluga", "Сеть Калуга", 36.2613, 54.5138),
    ("buyer-moscow", "Рестораны Москва", 37.6173, 55.7558),
    ("buyer-tula", "Опт Тула", 37.6186, 54.193),
    ("buyer-voronezh", "Дальний опт Воронеж", 39.2003, 51.672),
]

# Короткий срок — ближним. Воронеж берёт клубнику дорого (скорее не успеет) и томаты.
ORDERS = [
    ("strawberry", "buyer-belousovo", 80, 150),
    ("lettuce", "buyer-belousovo", 40, 90),
    ("cucumber", "buyer-belousovo", 60, 45),
    ("strawberry", "buyer-obninsk", 120, 160),
    ("lettuce", "buyer-obninsk", 70, 95),
    ("cucumber", "buyer-obninsk", 100, 50),
    ("tomato", "buyer-obninsk", 150, 70),
    ("strawberry", "buyer-maloyaroslavets", 80, 175),
    ("lettuce", "buyer-maloyaroslavets", 40, 105),
    ("tomato", "buyer-maloyaroslavets", 100, 75),
    ("strawberry", "buyer-naro-fominsk", 100, 190),
    ("tomato", "buyer-naro-fominsk", 120, 80),
    ("strawberry", "buyer-kaluga", 150, 210),
    ("cucumber", "buyer-kaluga", 180, 60),
    ("tomato", "buyer-kaluga", 200, 85),
    ("strawberry", "buyer-moscow", 180, 280),
    ("lettuce", "buyer-moscow", 90, 150),
    ("tomato", "buyer-moscow", 250, 120),
    ("cucumber", "buyer-tula", 160, 55),
    ("tomato", "buyer-tula", 220, 75),
    ("strawberry", "buyer-voronezh", 120, 320),
    ("tomato", "buyer-voronezh", 300, 140),
]

VEHICLES = [
    ("vehicle-a", "Газель А", 900, 12, 60, 2, 4, True),
    ("vehicle-b", "Газель Б", 800, 15, 60, 2, 3, True),
    ("vehicle-c", "Рефрижератор", 600, 22, 70, 2, 2, True),
]


def seed_db(db: Session):
    """Заполняет пустую базу набором для демонстрации плана."""
    crud.create_farm(db, *FARM)
    for item in PRODUCTS:
        crud.create_product(db, *item)
    for item in BUYERS:
        crud.create_buyer(db, *item)
    for item in ORDERS:
        crud.create_order(db, *item)
    for item in VEHICLES:
        crud.create_vehicle(db, *item)
    db.commit()


if __name__ == "__main__":
    from app.database import SessionLocal

    db = SessionLocal()
    try:
        for table in [models.Vehicle, models.BuyerOrder, models.Buyer, models.Product, models.Farm]:
            db.query(table).delete()
        seed_db(db)
    finally:
        db.close()
