import psycopg

USER = "postgres"
PASSWORD = "*****"   # потрібно ввести свій пароль
HOST = "localhost"
DB_NAME = "bookstore"


def create_db_if_not_exists():
    with psycopg.connect(
        f"dbname=postgres user={USER} password={PASSWORD} host={HOST}"
    ) as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname=%s;", (DB_NAME,))
            if cur.fetchone() is None:
                cur.execute(f"CREATE DATABASE {DB_NAME};")
                print(f"[DB] Створена база {DB_NAME}")
            else:
                print(f"[DB] База {DB_NAME} вже існує")


def get_conn():
    return psycopg.connect(
        f"dbname={DB_NAME} user={USER} password={PASSWORD} host={HOST}"
    )


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

            cur.execute("ALTER TABLE employee ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN NOT NULL DEFAULT FALSE;")
            cur.execute("ALTER TABLE book ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN NOT NULL DEFAULT FALSE;")
            cur.execute("ALTER TABLE sale ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN NOT NULL DEFAULT FALSE;")

    print("[DB] Таблиці готові")


def seed_data():
    from datetime import date

    with get_conn() as conn:
        with conn.cursor() as cur:

            cur.execute("SELECT COUNT(*) FROM employee;")
            if cur.fetchone()[0] > 0:
                print("[DB] Seed пропущено (дані вже існують)")
                return

            print("[DB] Додаємо seed-дані...")


            cur.execute("""
                INSERT INTO employee (name, position, phone, email)
                VALUES
                ('Іван Петров', 'Продавець', '+380501111111', 'ivan@test.com'),
                ('Марія Коваль', 'Старший продавець', '+380502222222', 'maria@test.com'),
                ('Андрій Сидоренко', 'Менеджер', '+380503333333', 'andriy@test.com'),
                ('Ольга Романюк', 'Продавець', '+380504444444', 'olga@test.com');
            """)


            cur.execute("""
                INSERT INTO book (isbn, title, author, genre, year, cost_price, sale_price, quantity)
                VALUES
                ('9780000000001', 'Python Basics', 'John Smith', 'Education', 2020, 200, 400, 20),
                ('9780000000002', 'Advanced Python', 'Anna Brown', 'Programming', 2021, 250, 500, 15),
                ('9780000000003', 'SQL Mastery', 'David Green', 'Education', 2019, 300, 600, 18),
                ('9780000000004', 'Clean Code', 'Robert Martin', 'Programming', 2008, 350, 700, 10),
                ('9780000000005', 'Data Science 101', 'Emily White', 'Data', 2022, 400, 800, 12),
                ('9780000000006', 'Machine Learning', 'Andrew Lee', 'Data', 2021, 450, 900, 8),
                ('9780000000007', 'PostgreSQL Guide', 'Ivan Petrov', 'Database', 2020, 280, 550, 14),
                ('9780000000008', 'Algorithms', 'Thomas Black', 'Programming', 2015, 320, 650, 16),
                ('9780000000009', 'Web Development', 'Sarah King', 'Web', 2018, 270, 540, 11),
                ('9780000000010', 'Design Patterns', 'Erich Gamma', 'Programming', 1994, 380, 760, 9);
            """)


            sales = [
                (1, 1, 2, 800),
                (2, 2, 1, 500),
                (3, 3, 3, 1800),
                (4, 4, 1, 700),
                (1, 5, 2, 1600),
                (2, 6, 1, 900),
                (3, 7, 2, 1100),
                (4, 8, 1, 650),
                (1, 9, 3, 1620),
                (2, 10, 1, 760),
            ]

            today = date.today()

            for employee_id, book_id, qty, total_price in sales:
                cur.execute("""
                    INSERT INTO sale (employee_id, book_id, sale_date, real_price, quantity_sold)
                    VALUES (%s, %s, %s, %s, %s)
                """, (employee_id, book_id, today, total_price, qty))

                cur.execute("""
                    UPDATE book
                    SET quantity = quantity - %s
                    WHERE id = %s
                """, (qty, book_id))

    print("[DB] Seed-дані успішно додані")


def init_db():
    create_db_if_not_exists()
    init_tables()
    seed_data()