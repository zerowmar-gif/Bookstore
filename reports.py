import csv
import os
from datetime import datetime
from database import get_conn


def input_date_str(prompt: str) -> str:
    while True:
        s = input(prompt).strip()
        try:
            datetime.strptime(s, "%Y-%m-%d")
            return s
        except ValueError:
            print("Помилка: дата повинна бути YYYY-MM-DD (приклад 2026-02-24).")


def export_to_csv(filename: str, header: list, rows: list):
    os.makedirs("export", exist_ok=True)
    path = os.path.join("export", filename)
    try:
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(header)
            for r in rows:
                w.writerow(r)
        print(f"Экспортовано в {path}")
    except Exception as e:
        print("Помилка экспорту:", e)


def report_employees_full():
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, name, position, phone, email
                    FROM employee
                    WHERE is_deleted = FALSE
                    ORDER BY id
                """)
                rows = cur.fetchall()
    except Exception as e:
        print("Помилка звіту:", e)
        return

    if not rows:
        print("Співробітників немає.")
        return

    print("\nID | ФІО | Посада | Телефон | Email")
    print("-" * 80)
    for r in rows:
        print(f"{r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]}")


def report_books_full():
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, isbn, title, author, genre, year, cost_price, sale_price, quantity
                    FROM book
                    WHERE is_deleted = FALSE
                    ORDER BY id
                """)
                rows = cur.fetchall()
    except Exception as e:
        print("Помилка звіту:", e)
        return

    if not rows:
        print("Книг немає.")
        return

    print("\nID | ISBN | Title | Author | Genre | Year | Cost | Price | Qty")
    print("-" * 120)
    for r in rows:
        print(f"{r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} | {r[6]} | {r[7]} | {r[8]}")


def report_sales_full(export_csv=False):
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT s.id, s.sale_date, e.name, b.title, s.quantity_sold, s.real_price
                    FROM sale s
                    JOIN employee e ON e.id = s.employee_id
                    JOIN book b ON b.id = s.book_id
                    WHERE s.is_deleted = FALSE
                    ORDER BY s.sale_date, s.id
                """)
                rows = cur.fetchall()
    except Exception as e:
        print("Помилка звіту:", e)
        return

    if not rows:
        print("Продажів немає.")
        return

    print("\nID | Дата | Співробітник | Книга | Кількість | Сума")
    print("-" * 90)
    for r in rows:
        print(f"{r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]}")

    if export_csv:
        export_to_csv(
            "sales_all.csv",
            ["id", "sale_date", "employee", "book", "quantity_sold", "real_price"],
            rows
        )


def sales_by_date():
    date_str = input_date_str("Введіть дату (YYYY-MM-DD): ")

    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT s.id, s.sale_date, e.name, b.title, s.quantity_sold, s.real_price
                    FROM sale s
                    JOIN employee e ON e.id = s.employee_id
                    JOIN book b ON b.id = s.book_id
                    WHERE s.sale_date = %s
                      AND s.is_deleted = FALSE
                    ORDER BY s.id
                """, (date_str,))
                rows = cur.fetchall()
    except Exception as e:
        print("Помилка звіту:", e)
        return

    if not rows:
        print("Немає продажів за цю дату.")
        return

    print("\nID | Дата | Співробітник | Книга | Кількість | Сума")
    print("-" * 90)
    for r in rows:
        print(f"{r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]}")


def sales_by_period(export_csv=False):
    date_from = input_date_str("Дата від (YYYY-MM-DD): ")
    date_to = input_date_str("Дата до (YYYY-MM-DD): ")

    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT s.id, s.sale_date, e.name, b.title, s.quantity_sold, s.real_price
                    FROM sale s
                    JOIN employee e ON e.id = s.employee_id
                    JOIN book b ON b.id = s.book_id
                    WHERE s.sale_date BETWEEN %s AND %s
                      AND s.is_deleted = FALSE
                    ORDER BY s.sale_date, s.id
                """, (date_from, date_to))
                rows = cur.fetchall()
    except Exception as e:
        print("Помилка звіту:", e)
        return

    if not rows:
        print("Немає продажів за період.")
        return

    print("\nID | Дата | Співробітник | Книга | Кількість | Сума")
    print("-" * 90)
    for r in rows:
        print(f"{r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]}")

    if export_csv:
        export_to_csv(
            f"sales_{date_from}_to_{date_to}.csv",
            ["id", "sale_date", "employee", "book", "quantity_sold", "real_price"],
            rows
        )


def sales_by_employee():
    emp_id_str = input("Введіть ID співробітника: ").strip()
    if not emp_id_str.isdigit():
        print("Помилка: ID повинен бути числом.")
        return
    emp_id = int(emp_id_str)

    date_from = input_date_str("Дата від (YYYY-MM-DD): ")
    date_to = input_date_str("Дата до (YYYY-MM-DD): ")

    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT name FROM employee WHERE id=%s AND is_deleted=FALSE", (emp_id,))
                emp = cur.fetchone()
                if emp is None:
                    print("Співробітника не знайдено або його видалено.")
                    return

                cur.execute("""
                    SELECT s.id, s.sale_date, b.title, s.quantity_sold, s.real_price
                    FROM sale s
                    JOIN book b ON b.id = s.book_id
                    WHERE s.employee_id = %s
                      AND s.sale_date BETWEEN %s AND %s
                      AND s.is_deleted = FALSE
                    ORDER BY s.sale_date, s.id
                """, (emp_id, date_from, date_to))
                rows = cur.fetchall()
    except Exception as e:
        print("Помилка звіту:", e)
        return

    if not rows:
        print("У співробітника немає продажів за період.")
        return

    print(f"\nПродажі співробітника: {emp[0]}")
    print("ID | Дата | Книга | Кількість | Сума")
    print("-" * 80)
    for r in rows:
        print(f"{r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]}")


def most_sold_book_by_period():
    date_from = input_date_str("Дата від (YYYY-MM-DD): ")
    date_to = input_date_str("Дата до (YYYY-MM-DD): ")

    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT b.id, b.title, COALESCE(SUM(s.quantity_sold), 0) AS total_qty
                    FROM sale s
                    JOIN book b ON b.id = s.book_id
                    WHERE s.sale_date BETWEEN %s AND %s
                      AND s.is_deleted = FALSE
                    GROUP BY b.id, b.title
                    ORDER BY total_qty DESC
                    LIMIT 1
                """, (date_from, date_to))
                row = cur.fetchone()
    except Exception as e:
        print("Помилка звіту:", e)
        return

    if row is None:
        print("Немає продажів за період.")
        return

    print(f"Найбільш продавана книга: ID={row[0]}, {row[1]}")
    print(f"Кількість проданого: {row[2]}")


def best_seller_by_profit():
    date_from = input_date_str("Дата від (YYYY-MM-DD): ")
    date_to = input_date_str("Дата до (YYYY-MM-DD): ")

    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT e.id, e.name,
                           COALESCE(SUM((b.sale_price - b.cost_price) * s.quantity_sold), 0) AS profit
                    FROM sale s
                    JOIN employee e ON e.id = s.employee_id
                    JOIN book b ON b.id = s.book_id
                    WHERE s.sale_date BETWEEN %s AND %s
                      AND s.is_deleted = FALSE
                    GROUP BY e.id, e.name
                    ORDER BY profit DESC
                    LIMIT 1
                """, (date_from, date_to))
                row = cur.fetchone()
    except Exception as e:
        print("Помилка звіту:", e)
        return

    if row is None:
        print("Немає продажів за період.")
        return

    print(f"Найкращий продавець за період: ID={row[0]}, {row[1]}")
    print(f"Прибуток: {row[2]}")


def profit_by_period():
    date_from = input_date_str("Дата від (YYYY-MM-DD): ")
    date_to = input_date_str("Дата до (YYYY-MM-DD): ")

    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT COALESCE(SUM((b.sale_price - b.cost_price) * s.quantity_sold), 0)
                    FROM sale s
                    JOIN book b ON b.id = s.book_id
                    WHERE s.sale_date BETWEEN %s AND %s
                      AND s.is_deleted = FALSE
                """, (date_from, date_to))
                total_profit = cur.fetchone()[0]
    except Exception as e:
        print("Помилка звіту:", e)
        return

    print(f"Сумарний прибуток за період: {total_profit}")


def top_author_by_period():
    date_from = input_date_str("Дата від (YYYY-MM-DD): ")
    date_to = input_date_str("Дата до (YYYY-MM-DD): ")

    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT b.author, COALESCE(SUM(s.quantity_sold), 0) AS total_qty
                    FROM sale s
                    JOIN book b ON b.id = s.book_id
                    WHERE s.sale_date BETWEEN %s AND %s
                      AND s.is_deleted = FALSE
                    GROUP BY b.author
                    ORDER BY total_qty DESC
                    LIMIT 1
                """, (date_from, date_to))
                row = cur.fetchone()
    except Exception as e:
        print("Помилка звіту:", e)
        return

    if row is None:
        print("Немає продажів за період.")
        return

    print(f"Топ автор за період: {row[0]}")
    print(f"Продано екземплярів: {row[1]}")


def top_genre_by_period():
    date_from = input_date_str("Дата від (YYYY-MM-DD): ")
    date_to = input_date_str("Дата до (YYYY-MM-DD): ")

    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT b.genre, COALESCE(SUM(s.quantity_sold), 0) AS total_qty
                    FROM sale s
                    JOIN book b ON b.id = s.book_id
                    WHERE s.sale_date BETWEEN %s AND %s
                      AND s.is_deleted = FALSE
                    GROUP BY b.genre
                    ORDER BY total_qty DESC
                    LIMIT 1
                """, (date_from, date_to))
                row = cur.fetchone()
    except Exception as e:
        print("Помилка звіту:", e)
        return

    if row is None:
        print("Немає продажів за період.")
        return

    print(f"Топ жанр за період: {row[0]}")
    print(f"Продано екземплярів: {row[1]}")