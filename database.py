import os
import datetime
import random
import psycopg
from dotenv import load_dotenv
load_dotenv()


DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "bookstore")


def _conn_str(dbname: str) -> str:
    return f"dbname={dbname} user={DB_USER} password={DB_PASSWORD} host={DB_HOST} port={DB_PORT}"


def create_db_if_not_exists():
    with psycopg.connect(_conn_str("postgres")) as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname=%s;", (DB_NAME,))
            if cur.fetchone() is None:
                cur.execute(f"CREATE DATABASE {DB_NAME};")
                print(f"[DB] Створена база даних {DB_NAME}")
            else:
                print(f"[DB] База даних {DB_NAME} вже існує")


def get_conn():
    return psycopg.connect(_conn_str(DB_NAME))


def init_tables():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS employee (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                position TEXT,
                phone TEXT,
                email TEXT UNIQUE NOT NULL,
                is_deleted BOOLEAN NOT NULL DEFAULT FALSE
            );
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS book (
                id SERIAL PRIMARY KEY,
                isbn TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                genre TEXT,
                year INT,
                cost_price NUMERIC NOT NULL CHECK (cost_price > 0),
                sale_price NUMERIC NOT NULL CHECK (sale_price > 0),
                quantity INT NOT NULL CHECK (quantity >= 0),
                is_deleted BOOLEAN NOT NULL DEFAULT FALSE
            );
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS sale (
                id SERIAL PRIMARY KEY,
                employee_id INT NOT NULL REFERENCES employee(id),
                book_id INT NOT NULL REFERENCES book(id),
                sale_date DATE NOT NULL,
                real_price NUMERIC NOT NULL CHECK (real_price > 0),
                quantity_sold INT NOT NULL CHECK (quantity_sold > 0),
                is_deleted BOOLEAN NOT NULL DEFAULT FALSE
            );
            """)

    print("[DB] Таблиці готові")


def seed_data():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM employee;")
            emp_count = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM book;")
            book_count = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM sale;")
            sale_count = cur.fetchone()[0]

            if emp_count == 0:
                employees = [
                    ("Іван Петренко", "Продавець", "+380501112233", "ivan.petrenko@example.com"),
                    ("Олена Коваль", "Продавець", "+380631234567", "olena.koval@example.com"),
                    ("Андрій Мельник", "Старший продавець", "+380671110022", "andrii.melnyk@example.com"),
                    ("Марія Ткаченко", "Касир", "+380951234111", "maria.tkachenko@example.com"),
                ]
                cur.executemany(
                    "INSERT INTO employee (name, position, phone, email) VALUES (%s, %s, %s, %s);",
                    employees,
                )
                print("[DB] Додано demo співробітників (4)")

            if book_count == 0:
                books = [
                    ("978-617-12-0001-1", "Кобзар", "Тарас Шевченко", "Класика", 2015, 120.0, 220.0, 10),
                    ("978-617-12-0002-8", "Лісова пісня", "Леся Українка", "Драма", 2018, 90.0, 180.0, 8),
                    ("978-617-12-0003-5", "Тигролови", "Іван Багряний", "Роман", 2019, 110.0, 210.0, 6),
                    ("978-617-12-0004-2", "1984", "Джордж Орвелл", "Антиутопія", 2020, 140.0, 260.0, 7),
                    ("978-617-12-0005-9", "Маленький принц", "Антуан де Сент-Екзюпері", "Казка", 2017, 80.0, 150.0, 12),
                    ("978-617-12-0006-6", "Гаррі Поттер 1", "Дж. К. Ролінґ", "Фентезі", 2021, 200.0, 350.0, 9),
                    ("978-617-12-0007-3", "Місто", "Валер'ян Підмогильний", "Роман", 2016, 100.0, 190.0, 5),
                    ("978-617-12-0008-0", "Сад Гетсиманський", "Іван Багряний", "Роман", 2022, 130.0, 240.0, 4),
                    ("978-617-12-0009-7", "Алхімік", "Пауло Коельйо", "Роман", 2014, 95.0, 175.0, 11),
                    ("978-617-12-0010-3", "Дюна", "Френк Герберт", "Фантастика", 2023, 220.0, 390.0, 3),
                ]
                cur.executemany(
                    """
                    INSERT INTO book (isbn, title, author, genre, year, cost_price, sale_price, quantity)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                    """,
                    books,
                )
                print("[DB] Додано demo книги (10)")

            if sale_count == 0:
                cur.execute("SELECT id FROM employee WHERE is_deleted=FALSE ORDER BY id;")
                emp_ids = [r[0] for r in cur.fetchall()]
                cur.execute("SELECT id, sale_price FROM book WHERE is_deleted=FALSE ORDER BY id;")
                book_rows = cur.fetchall()

                if emp_ids and book_rows:
                    today = datetime.date.today()
                    sales_to_insert = []
                    for _ in range(10):
                        emp_id = random.choice(emp_ids)
                        book_id, sale_price = random.choice(book_rows)
                        qty = random.randint(1, 2)
                        total = float(sale_price) * qty
                        sale_date = today - datetime.timedelta(days=random.randint(0, 30))
                        sales_to_insert.append((emp_id, book_id, sale_date, total, qty))

                    for emp_id, book_id, sale_date, total, qty in sales_to_insert:
                        cur.execute("SELECT quantity FROM book WHERE id=%s;", (book_id,))
                        q = cur.fetchone()[0]
                        if q >= qty:
                            cur.execute("UPDATE book SET quantity = quantity - %s WHERE id=%s;", (qty, book_id))
                            cur.execute(
                                """
                                INSERT INTO sale (employee_id, book_id, sale_date, real_price, quantity_sold)
                                VALUES (%s, %s, %s, %s, %s);
                                """,
                                (emp_id, book_id, sale_date, total, qty),
                            )
                print("[DB] Додано demo продажі (до 10)")

    print("[DB] Seed готовий")


def init_db():
    create_db_if_not_exists()
    init_tables()
    seed_data()