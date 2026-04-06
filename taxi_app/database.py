import sqlite3
import os

DATABASE_PATH = os.getenv('DATABASE_PATH', 'taxi.db')


def get_db():
    return sqlite3.connect(DATABASE_PATH)


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS cars (
            car_id INTEGER PRIMARY KEY,
            model TEXT,
            driver TEXT,
            plate TEXT,
            on_line TEXT
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS passengers (
            id INTEGER PRIMARY KEY,
            name TEXT,
            phone TEXT,
            sms_code TEXT
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY,
            passenger_phone TEXT,
            car_plate TEXT,
            driver TEXT,
            destination TEXT,
            status TEXT,
            arrival_time INTEGER
        )
    ''')

    cur.execute("SELECT COUNT(*) FROM cars")
    if cur.fetchone()[0] == 0:
        cars_data = [
            (1, 'Kia Rio', 'Корунов Александр Владимирович', 'a712ee99', 'Да'),
            (2, 'Lada Vesta', 'Рунов Дмитрий Борисович', 'a171mp97', 'Нет'),
            (3, 'Kia Optima', 'Косачков Кирилл Павлович', 'm196oc50', 'Да'),
            (4, 'Hyundai Solaris', 'Михайлова Анна Сергеевна', 'x123aa77', 'Да'),
            (5, 'Toyota Camry', 'Волков Игорь Дмитриевич', 'o888oo199', 'Да')
        ]
        cur.executemany('INSERT INTO cars VALUES (?, ?, ?, ?, ?)', cars_data)

    cur.execute("SELECT COUNT(*) FROM passengers")
    if cur.fetchone()[0] == 0:
        passengers_data = [
            (1, 'Баранов Кирилл Олегович', '+79991234567', '124'),
            (2, 'Козин Олег Павлович', '+79997654321', '981'),
            (3, 'Смирнова Екатерина Андреевна', '+79998887777', '555')
        ]
        cur.executemany('INSERT INTO passengers VALUES (?, ?, ?, ?)', passengers_data)

    conn.commit()
    conn.close()


def get_free_cars():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT car_id, model, driver, plate FROM cars WHERE on_line = 'Да'")
    result = cur.fetchall()
    conn.close()
    return result


def authenticate(phone, sms_code):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT name, phone FROM passengers WHERE phone = ? AND sms_code = ?", (phone, sms_code))
    result = cur.fetchone()
    conn.close()
    return result


def create_order(passenger_phone, destination):
    import random
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT plate, driver, model FROM cars WHERE on_line = 'Да' LIMIT 1")
    car = cur.fetchone()

    if not car:
        conn.close()
        return None

    car_plate, driver, model = car
    arrival_time = random.randint(5, 20)

    cur.execute('''
        INSERT INTO orders (passenger_phone, car_plate, driver, destination, status, arrival_time)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (passenger_phone, car_plate, driver, destination, 'active', arrival_time))

    cur.execute("UPDATE cars SET on_line = 'Нет' WHERE plate = ?", (car_plate,))

    order_id = cur.lastrowid
    conn.commit()
    conn.close()

    return {
        'order_id': order_id,
        'driver': driver,
        'car_plate': car_plate,
        'model': model,
        'arrival_time': arrival_time,
        'destination': destination
    }


def get_active_order(phone):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        SELECT o.order_id, o.driver, o.car_plate, c.model, o.destination, o.arrival_time, o.status
        FROM orders o
        JOIN cars c ON o.car_plate = c.plate
        WHERE o.passenger_phone = ? AND o.status = 'active'
    ''', (phone,))
    order = cur.fetchone()
    conn.close()

    if order:
        return {
            'order_id': order[0],
            'driver': order[1],
            'car_plate': order[2],
            'model': order[3],
            'destination': order[4],
            'arrival_time': order[5],
            'status': order[6]
        }
    return None
