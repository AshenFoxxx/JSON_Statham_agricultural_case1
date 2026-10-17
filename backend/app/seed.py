"""Seed данные для базы данных."""
from sqlalchemy.orm import Session
from app import crud, models


def seed_db(db: Session):
    """Заполняет базу начальными данными."""

    # Хозяйство
    crud.create_farm(db, "Хозяйство Обнинск", 36.6103, 55.0969)

    # Культуры
    crud.create_product(db, "strawberry", "Клубника", 600, 6)
    crud.create_product(db, "tomato", "Томаты", 900, 24)
    crud.create_product(db, "cucumber", "Огурцы", 700, 18)

    # Покупатели
    crud.create_buyer(db, "buyer-obninsk", "Рынок Обнинск", 36.5855, 55.112)
    crud.create_buyer(db, "buyer-kaluga", "Сеть Калуга", 36.2613, 54.5138)
    crud.create_buyer(db, "buyer-tula", "Опт Тула", 37.6182, 54.1931)
    crud.create_buyer(db, "buyer-moscow", "Рестораны Москва", 37.6173, 55.7558)

    # Заказы
    crud.create_order(db, "strawberry", "buyer-obninsk", 200, 160)
    crud.create_order(db, "tomato", "buyer-obninsk", 250, 70)
    crud.create_order(db, "cucumber", "buyer-obninsk", 200, 50)

    crud.create_order(db, "strawberry", "buyer-kaluga", 250, 210)
    crud.create_order(db, "tomato", "buyer-kaluga", 200, 85)
    crud.create_order(db, "cucumber", "buyer-kaluga", 180, 60)

    crud.create_order(db, "strawberry", "buyer-tula", 180, 190)
    crud.create_order(db, "tomato", "buyer-tula", 300, 75)
    crud.create_order(db, "cucumber", "buyer-tula", 220, 55)

    crud.create_order(db, "strawberry", "buyer-moscow", 300, 280)
    crud.create_order(db, "tomato", "buyer-moscow", 400, 120)
    crud.create_order(db, "cucumber", "buyer-moscow", 250, 90)

    # Машины
    crud.create_vehicle(db, "vehicle-a", "Газель А", 800, 10, 60, 1, 3, True)
    crud.create_vehicle(db, "vehicle-b", "Газель Б", 800, 11, 60, 1, 3, True)
    crud.create_vehicle(db, "vehicle-c", "Рефрижератор", 700, 15, 60, 1, 2, True)

    db.commit()


if __name__ == "__main__":
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        # Очистить и заполнить
        for table in [models.Vehicle, models.BuyerOrder, models.Buyer, models.Product, models.Farm]:
            db.query(table).delete()
        seed_db(db)
    finally:
        db.close()
