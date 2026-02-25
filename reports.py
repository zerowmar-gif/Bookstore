import csv
import os
from datetime import datetime
from database import get_conn


def _validate_date_str(s: str) -> bool:
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def _ensure_export_dir():
    os.makedirs("export", exist_ok=True)


def report_employees_full():
    print("\n--- Повна інформація про співробітників ---")
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, name, position, phone, email
                    FROM employee
                    WHERE is_deleted=FALSE
                    ORDER BY id
                """)
                rows = cur.fetchall()
        if not rows:
            print("Немає співробітників.")
            return

        print("ID | ПІБ | Посада | Телефон | Email")
        print("-" * 80)
        for r in rows:
            print(f"{r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]}")
    except Exception as e:
        print("Помилка звіту:", e)


def report_books_full():
    print("\n--- Повна інформація про книги ---")
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, isbn, title, author, genre, year, cost_price, sale_price, quantity
                    FROM book
                    WHERE is_deleted=FALSE
                    ORDER BY id
                """)
                rows = cur.fetchall()
        if not rows:
            print("Немає книг.")
            return

        print("ID | ISBN | Назва | Автор | Жанр | Рік | Собівартість | Ціна | К-ть")
        print("-" * 120)
        for r in rows:
            print(f"{r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} | {r[6]} | {r[7]} | {r[8]}")
    except Exception as e:
        print("Помилка звіту:", e)


def report_sales_full(export_csv: bool = False):
    print("\n--- Повна інформація про продажі ---")
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT s.id, s.sale_date, e.name, b.title, s.quantity_sold, s.real_price
                    FROM sale s
                    JOIN employee e ON e.id = s.employee_id
                    JOIN book b ON b.id = s.book_id
                    WHERE s.is_deleted=FALSE
                      AND e.is_deleted=FALSE
                      AND b.is_deleted=FALSE
                    ORDER BY s.id
                """)
                rows = cur.fetchall()
        if not rows:
            print("Немає продажів.")
            return

        print("ID | Дата | Співробітник | Книга | К-ть | Сума (TOTAL)")
        print("-" * 100)
        for r in rows:
            print(f"{r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]}")

        if export_csv:
            _ensure_export_dir()
            filename = "export/sales_all.csv"
            with open(filename, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["id", "sale_date", "employee", "book", "quantity_sold", "real_price_total"])
                w.writerows(rows)
            print(f"Експортовано в {filename}")
    except Exception as e:
        print("Помилка звіту:", e)


def sales_by_date():
    date_str = input("Введіть дату (YYYY-MM-DD): ").strip()
    if not _validate_date_str(date_str):
        print("Некоректна дата.")
        return

    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT s.id, s.sale_date, e.name, b.title, s.quantity_sold, s.real_price
                    FROM sale s
                    JOIN employee e ON e.id = s.employee_id
                    JOIN book b ON b.id = s.book_id
                    WHERE s.is_deleted=FALSE
                      AND s.sale_date = %s
                    ORDER BY s.id
                """, (date_str,))
                rows = cur.fetchall()
        if not rows:
            print("Немає продажів на цю дату.")
            return

        print("\nID | Дата | Співробітник | Книга | К-ть | Сума (TOTAL)")
        print("-" * 100)
        for r in rows:
            print(f"{r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]}")
    except Exception as e:
        print("Помилка звіту:", e)


def sales_by_period(export_csv: bool = False):
    date_from = input("Дата від (YYYY-MM-DD): ").strip()
    date_to = input("Дата до (YYYY-MM-DD): ").strip()
    if not _validate_date_str(date_from) or not _validate_date_str(date_to):
        print("Некоректний формат дати.")
        return

    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT s.id, s.sale_date, e.name, b.title, s.quantity_sold, s.real_price
                    FROM sale s
                    JOIN employee e ON e.id = s.employee_id
                    JOIN book b ON b.id = s.book_id
                    WHERE s.is_deleted=FALSE
                      AND s.sale_date BETWEEN %s AND %s
                    ORDER BY s.sale_date, s.id
                """, (date_from, date_to))
                rows = cur.fetchall()
        if not rows:
            print("Немає продажів за період.")
            return

        print("\nID | Дата | Співробітник | Книга | К-ть | Сума (TOTAL)")
        print("-" * 100)
        for r in rows:
            print(f"{r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]}")

        if export_csv:
            _ensure_export_dir()
            filename = f"export/sales_{date_from}_to_{date_to}.csv"
            with open(filename, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["id", "sale_date", "employee", "book", "quantity_sold", "real_price_total"])
                w.writerows(rows)
            print(f"Експортовано в {filename}")
    except Exception as e:
        print("Помилка звіту:", e)


def sales_by_employee():
    emp_id = input("ID співробітника: ").strip()
    if not emp_id.isdigit():
        print("ID має бути числом.")
        return
    emp_id = int(emp_id)

    date_from = input("Дата від (YYYY-MM-DD): ").strip()
    date_to = input("Дата до (YYYY-MM-DD): ").strip()
    if not _validate_date_str(date_from) or not _validate_date_str(date_to):
        print("Некоректний формат дати.")
        return

    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT s.id, s.sale_date, b.title, s.quantity_sold, s.real_price
                    FROM sale s
                    JOIN book b ON b.id = s.book_id
                    WHERE s.is_deleted=FALSE
                      AND s.employee_id=%s
                      AND s.sale_date BETWEEN %s AND %s
                    ORDER BY s.sale_date, s.id
                """, (emp_id, date_from, date_to))
                rows = cur.fetchall()
        if not rows:
            print("Немає продажів для цього співробітника за період.")
            return

        print("\nID | Дата | Книга | К-ть | Сума (TOTAL)")
        print("-" * 80)
        for r in rows:
            print(f"{r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]}")
    except Exception as e:
        print("Помилка звіту:", e)


def most_sold_book_by_period():
    date_from = input("Дата від (YYYY-MM-DD): ").strip()
    date_to = input("Дата до (YYYY-MM-DD): ").strip()
    if not _validate_date_str(date_from) or not _validate_date_str(date_to):
        print("Некоректний формат дати.")
        return

    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT b.id, b.title, SUM(s.quantity_sold) AS total_qty
                    FROM sale s
                    JOIN book b ON b.id = s.book_id
                    WHERE s.is_deleted=FALSE
                      AND s.sale_date BETWEEN %s AND %s
                    GROUP BY b.id, b.title
                    ORDER BY total_qty DESC
                    LIMIT 1;
                """, (date_from, date_to))
                row = cur.fetchone()
        if row is None:
            print("Немає продажів за період.")
            return
        print(f"Найбільш продавана книга: ID={row[0]}, {row[1]} (кількість: {row[2]})")
    except Exception as e:
        print("Помилка звіту:", e)


def profit_by_period():
    date_from = input("Дата від (YYYY-MM-DD): ").strip()
    date_to = input("Дата до (YYYY-MM-DD): ").strip()
    if not _validate_date_str(date_from) or not _validate_date_str(date_to):
        print("Некоректний формат дати.")
        return

    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT COALESCE(SUM(s.real_price - b.cost_price * s.quantity_sold), 0)
                    FROM sale s
                    JOIN book b ON b.id = s.book_id
                    WHERE s.is_deleted=FALSE
                      AND s.sale_date BETWEEN %s AND %s
                """, (date_from, date_to))
                total_profit = cur.fetchone()[0]
        print(f"Сумарний прибуток за період: {total_profit}")
    except Exception as e:
        print("Помилка звіту:", e)


def best_seller_by_profit():
    date_from = input("Дата від (YYYY-MM-DD): ").strip()
    date_to = input("Дата до (YYYY-MM-DD): ").strip()
    if not _validate_date_str(date_from) or not _validate_date_str(date_to):
        print("Некоректний формат дати.")
        return

    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT e.id, e.name,
                           COALESCE(SUM(s.real_price - b.cost_price * s.quantity_sold), 0) AS profit
                    FROM sale s
                    JOIN employee e ON e.id = s.employee_id
                    JOIN book b ON b.id = s.book_id
                    WHERE s.is_deleted=FALSE
                      AND s.sale_date BETWEEN %s AND %s
                    GROUP BY e.id, e.name
                    ORDER BY profit DESC
                    LIMIT 1;
                """, (date_from, date_to))
                row = cur.fetchone()
        if row is None:
            print("Немає продажів за період.")
            return

        print(f"Найуспішніший продавець: ID={row[0]}, {row[1]}")
        print(f"Прибуток: {row[2]}")
    except Exception as e:
        print("Помилка звіту:", e)


def top_author_by_period():
    date_from = input("Дата від (YYYY-MM-DD): ").strip()
    date_to = input("Дата до (YYYY-MM-DD): ").strip()
    if not _validate_date_str(date_from) or not _validate_date_str(date_to):
        print("Некоректний формат дати.")
        return

    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT b.author, SUM(s.quantity_sold) AS total_qty
                    FROM sale s
                    JOIN book b ON b.id = s.book_id
                    WHERE s.is_deleted=FALSE
                      AND s.sale_date BETWEEN %s AND %s
                    GROUP BY b.author
                    ORDER BY total_qty DESC
                    LIMIT 1;
                """, (date_from, date_to))
                row = cur.fetchone()
        if row is None:
            print("Немає продажів за період.")
            return
        print(f"ТОП автор: {row[0]} (кількість: {row[1]})")
    except Exception as e:
        print("Помилка звіту:", e)


def top_genre_by_period():
    date_from = input("Дата від (YYYY-MM-DD): ").strip()
    date_to = input("Дата до (YYYY-MM-DD): ").strip()
    if not _validate_date_str(date_from) or not _validate_date_str(date_to):
        print("Некоректний формат дати.")
        return

    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT b.genre, SUM(s.quantity_sold) AS total_qty
                    FROM sale s
                    JOIN book b ON b.id = s.book_id
                    WHERE s.is_deleted=FALSE
                      AND s.sale_date BETWEEN %s AND %s
                    GROUP BY b.genre
                    ORDER BY total_qty DESC
                    LIMIT 1;
                """, (date_from, date_to))
                row = cur.fetchone()
        if row is None:
            print("Немає продажів за період.")
            return
        print(f"ТОП жанр: {row[0]} (кількість: {row[1]})")
    except Exception as e:
        print("Помилка звіту:", e)