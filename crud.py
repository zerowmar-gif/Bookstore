from database import get_conn
from datetime import date, datetime
import re



EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def input_nonempty(prompt: str) -> str:
    while True:
        s = input(prompt).strip()
        if s:
            return s
        print("Помилка: поле не може бути пустим.")


def input_email(prompt: str) -> str:
    while True:
        s = input(prompt).strip()
        if EMAIL_RE.match(s):
            return s
        print("Помилка: email введено невірно. Приклад: name@gmail.com")


def input_int(prompt: str, *, min_value=None, max_value=None) -> int:
    while True:
        s = input(prompt).strip()
        try:
            v = int(s)
        except ValueError:
            print("Помилка: потрібно ціле число.")
            continue
        if min_value is not None and v < min_value:
            print(f"Помилка: число повинно бути >= {min_value}.")
            continue
        if max_value is not None and v > max_value:
            print(f"Помилка: число повинно бути <= {max_value}.")
            continue
        return v


def input_float(prompt: str, *, min_value=None) -> float:
    while True:
        s = input(prompt).strip().replace(",", ".")
        try:
            v = float(s)
        except ValueError:
            print("Помилка: потрібно число (пример: 12.5).")
            continue
        if min_value is not None and v < min_value:
            print(f"Помилка: число повинно бути >= {min_value}.")
            continue
        return v


def input_date_str(prompt: str) -> str:
    while True:
        s = input(prompt).strip()
        try:
            datetime.strptime(s, "%Y-%m-%d")
            return s
        except ValueError:
            print("Помилка: дата повинна бути в форматі YYYY-MM-DD (наприклад 2026-02-24).")


def input_isbn(prompt: str) -> str:
    while True:
        s = input(prompt).strip()
        raw = s.replace("-", "")
        if raw.isdigit() and 10 <= len(raw) <= 20:
            return s
        print("Помилка: ISBN повинен бути із цифр (можно с дефісами), довжина 10-20.")


class Employee:
    def add(self):
        print("\n--- Додати співробітника ---")
        name = input_nonempty("ФІО: ")
        position = input("Посада: ").strip()
        phone = input("Телефон: ").strip()
        email = input_email("Email: ")

        try:
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO employee (name, position, phone, email)
                        VALUES (%s, %s, %s, %s)
                    """, (name, position, phone, email))
            print("Співробітника додано.")
        except Exception as e:
            print("Помилка при додаванні співробітника:", e)

    def list_all(self):
        print("\n--- Список співробітників ---")
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
            print("Помилка при отриманні списка:", e)
            return

        if not rows:
            print("поки немає співробітників.")
            return

        print("ID | ФІО | Посада | Телефон | Email")
        print("-" * 70)
        for r in rows:
            print(f"{r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]}")

    def details(self):
        print("\n--- Деталі співробітника ---")
        emp_id = input_int("Введіть ID спіробітника: ", min_value=1)

        try:
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, name, position, phone, email
                        FROM employee
                        WHERE id=%s AND is_deleted=FALSE
                    """, (emp_id,))
                    row = cur.fetchone()
        except Exception as e:
            print("Помилка при отриманні даних:", e)
            return

        if row is None:
            print("Співробітника не знайдено.")
            return

        print(f"ID: {row[0]}\nФІО: {row[1]}\nПосада: {row[2]}\nТелефон: {row[3]}\nEmail: {row[4]}")

    def update(self):
        print("\n--- Редагування співробітника ---")
        emp_id = input_int("Введіть ID співробітника: ", min_value=1)

        try:
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, name, position, phone, email
                        FROM employee
                        WHERE id=%s AND is_deleted=FALSE
                    """, (emp_id,))
                    row = cur.fetchone()

                    if row is None:
                        print("Співробітника не знайдено.")
                        return

                    print("Залиште поле порожнім, якщо не хочете змінювати.")
                    new_name = input(f"Нове ПІБ ({row[1]}): ").strip()
                    new_position = input(f"Нова посада ({row[2]}): ").strip()
                    new_phone = input(f"Новий телефон ({row[3]}): ").strip()
                    new_email = input(f"Новий email ({row[4]}): ").strip()

                    if not new_name:
                        new_name = row[1]
                    if not new_position:
                        new_position = row[2]
                    if not new_phone:
                        new_phone = row[3]
                    if not new_email:
                        new_email = row[4]
                    else:
                        if not EMAIL_RE.match(new_email):
                            print("Помилка: email введено невірно.")
                            return

                    if not new_name.strip():
                        print("Помилка: ФІО не може бути порожнім.")
                        return

                    cur.execute("""
                        UPDATE employee
                        SET name = %s, position = %s, phone = %s, email = %s
                        WHERE id=%s
                    """, (new_name, new_position, new_phone, new_email, emp_id))

            print("Співробітника оновлено.")
        except Exception as e:
            print("Помилка при оновленні:", e)

    def delete(self):
        print("\n--- Видалення співробітника (soft delete) ---")
        emp_id = input_int("Введіть ID співробітника: ", min_value=1)

        try:
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, name, email
                        FROM employee
                        WHERE id=%s AND is_deleted = FALSE
                    """, (emp_id,))
                    row = cur.fetchone()

                    if row is None:
                        print("Співробітника не знайдено.")
                        return

                    print(f"Знайдено: ID={row[0]}, {row[1]}, {row[2]}")
                    confirm = input("Точно видалити? (y/n): ").strip().lower()
                    if confirm != "y":
                        print("Видалення скасовано.")
                        return

                    cur.execute("UPDATE employee SET is_deleted = TRUE WHERE id=%s", (emp_id,))
            print("Співробітника позначено як видаленого.")
        except Exception as e:
            print("Помилка при видаленні:", e)



class Book:
    def add(self):
        print("\n--- Додати книгу ---")
        isbn = input_isbn("ISBN: ")
        title = input_nonempty("Назва: ")
        author = input_nonempty("Автор: ")
        genre = input("Жанр: ").strip()

        year = input_int("Рік публікації: ", min_value=1500, max_value=2100)
        cost_price = input_float("Собівартість: ", min_value=0.01)
        sale_price = input_float("Ціна продажу: ", min_value=0.01)
        quantity = input_int("Кількість: ", min_value=0)

        try:
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO book (isbn, title, author, genre, year, cost_price, sale_price, quantity)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (isbn, title, author, genre, year, cost_price, sale_price, quantity))
            print("Книгу додано.")
        except Exception as e:
            print("Помилка при додаванні книги:", e)

    def list_all(self):
        print("\n--- Список книг ---")
        try:
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, isbn, title, author, genre, year, sale_price, quantity
                        FROM book
                        WHERE is_deleted=FALSE
                        ORDER BY id
                    """)
                    rows = cur.fetchall()
        except Exception as e:
            print("Помилка при отриманні списка:", e)
            return

        if not rows:
            print("Книг поки нема.")
            return

        print("ID | ISBN | Назва | Автор | Жанр | Рік | Ціна | Залишок")
        print("-" * 110)
        for r in rows:
            print(f"{r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} | {r[6]} | {r[7]}")

    def details(self):
        print("\n--- Деталі книги ---")
        book_id = input_int("Введіть ID книги: ", min_value=1)

        try:
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, isbn, title, author, genre, year, cost_price, sale_price, quantity
                        FROM book
                        WHERE id=%s AND is_deleted=FALSE
                    """, (book_id,))
                    row = cur.fetchone()
        except Exception as e:
            print("Помилка при отриманні даних:", e)
            return

        if row is None:
            print("Книга не знайдена.")
            return

        print(
            f"ID: {row[0]}\nISBN: {row[1]}\nНазва: {row[2]}\nАвтор: {row[3]}"
            f"\nЖанр: {row[4]}\nРік: {row[5]}\nСобівартість: {row[6]}"
            f"\nЦіна: {row[7]}\nЗалишок: {row[8]}"
        )

    def update(self):
        print("\n--- Редагування книги ---")
        book_id = input_int("Введіть ID книги: ", min_value=1)

        try:
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, isbn, title, author, genre, year, cost_price, sale_price, quantity
                        FROM book
                        WHERE id=%s AND is_deleted=FALSE
                    """, (book_id,))
                    row = cur.fetchone()
                    if row is None:
                        print("Книга не знайдена.")
                        return

                    print("Залиште порожнім, якщо не хочете змінювати.")
                    new_isbn = input(f"ISBN ({row[1]}): ").strip()
                    new_title = input(f"Назва ({row[2]}): ").strip()
                    new_author = input(f"Автор ({row[3]}): ").strip()
                    new_genre = input(f"Жанр ({row[4]}): ").strip()

                    year_in = input(f"Рік ({row[5]}): ").strip()
                    cost_in = input(f"Собівартість ({row[6]}): ").strip()
                    sale_in = input(f"Ціна ({row[7]}): ").strip()
                    qty_in = input(f"Залишок ({row[8]}): ").strip()

                    if not new_isbn:
                        new_isbn = row[1]
                    else:
                        raw = new_isbn.replace("-", "")
                        if not (raw.isdigit() and 10 <= len(raw) <= 20):
                            print("Помилка: ISBN невірний.")
                            return

                    if not new_title:
                        new_title = row[2]
                    if not new_author:
                        new_author = row[3]
                    if not new_genre:
                        new_genre = row[4]

                    if year_in:
                        try:
                            new_year = int(year_in)
                        except ValueError:
                            print("Помилка: рік повинен бути числом.")
                            return
                        if not (1500 <= new_year <= 2100):
                            print("Помилка: рік повинен бути 1500..2100.")
                            return
                    else:
                        new_year = row[5]

                    if cost_in:
                        try:
                            new_cost = float(cost_in.replace(",", "."))
                        except ValueError:
                            print("Помилка: собівартість має бути числом.")
                            return
                        if new_cost <= 0:
                            print("Помилка: собівартість має бути > 0.")
                            return
                    else:
                        new_cost = float(row[6])

                    if sale_in:
                        try:
                            new_sale = float(sale_in.replace(",", "."))
                        except ValueError:
                            print("Помилка: ціна має бути числом.")
                            return
                        if new_sale <= 0:
                            print("Помилка: ціна має бути > 0.")
                            return
                    else:
                        new_sale = float(row[7])

                    if qty_in:
                        if not qty_in.isdigit():
                            print("Помилка: залишок має бути цілим числом.")
                            return
                        new_qty = int(qty_in)
                        if new_qty < 0:
                            print("Помилка: залишок не може бути від’ємним.")
                            return
                    else:
                        new_qty = int(row[8])

                    if not new_title.strip() or not new_author.strip():
                        print("Помилка: назва та автор не можуть бути порожніми.")
                        return

                    cur.execute("""
                        UPDATE book
                        SET isbn = %s, title = %s, author = %s, genre = %s, year = %s,
                            cost_price = %s, sale_price = %s, quantity = %s
                        WHERE id = %s
                    """, (
                        new_isbn, new_title, new_author, new_genre, new_year,
                        new_cost, new_sale, new_qty, book_id
                    ))

            print("Книга оновлена.")
        except Exception as e:
            print("Помилка при оновленні:", e)

    def delete(self):
        print("\n--- Видалення книги (soft delete) ---")
        book_id = input_int("Введіть ID книги: ", min_value=1)

        try:
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, title, author
                        FROM book
                        WHERE id=%s AND is_deleted = FALSE
                    """, (book_id,))
                    row = cur.fetchone()
                    if row is None:
                        print("Книга не знайдена.")
                        return

                    print(f"Знайдена: ID={row[0]}, {row[1]} ({row[2]})")
                    confirm = input("Точно видалити? (y/n): ").strip().lower()
                    if confirm != "y":
                        print("Видалення скасовано.")
                        return

                    cur.execute("UPDATE book SET is_deleted = TRUE WHERE id=%s", (book_id,))

            print("Книгу позначено як видалену.")
        except Exception as e:
            print("Помилка при видаленні книги:", e)


class Sale:
    def create_sale(self):
        print("\n--- Продаж книги ---")
        emp_id = input_int("ID співробітника: ", min_value=1)
        book_id = input_int("ID книги: ", min_value=1)
        quantity_sold = input_int("Кількість: ", min_value=1)

        try:
            with get_conn() as conn:
                with conn.transaction():
                    with conn.cursor() as cur:
                        cur.execute("SELECT id FROM employee WHERE id=%s AND is_deleted = FALSE", (emp_id,))
                        if cur.fetchone() is None:
                            print("Співробітника не знайдено або видалено.")
                            return

                        cur.execute("""
                            SELECT quantity, cost_price, sale_price
                            FROM book
                            WHERE id=%s AND is_deleted = FALSE
                        """, (book_id,))
                        book = cur.fetchone()
                        if book is None:
                            print("Книга не знайдена або видалена.")
                            return

                        current_qty, cost_price, sale_price = book
                        if current_qty < quantity_sold:
                            print("Недостатньо книг на складі.")
                            return

                        new_qty = current_qty - quantity_sold
                        cur.execute("UPDATE book SET quantity = %s WHERE id=%s", (new_qty, book_id))

                        real_price = float(sale_price) * quantity_sold
                        cur.execute("""
                            INSERT INTO sale (employee_id, book_id, sale_date, real_price, quantity_sold)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (emp_id, book_id, date.today(), real_price, quantity_sold))

                        profit = (float(sale_price) - float(cost_price)) * quantity_sold
                        print(f"Продаж виконано. Прибуток: {profit}")

        except Exception as e:
            print("Помилка при продажі:", e)


def employees_menu():
    emp = Employee()
    while True:
        print("\n--- Співробітники ---")
        print("1) Додати")
        print("2) Список")
        print("3) Деталі")
        print("4) Редагувати")
        print("5) Видалити (soft)")
        print("0) Назад")

        c = input("Виберіть пункт: ").strip()
        if c == "0":
            break
        elif c == "1":
            emp.add()
        elif c == "2":
            emp.list_all()
        elif c == "3":
            emp.details()
        elif c == "4":
            emp.update()
        elif c == "5":
            emp.delete()
        else:
            print("Невірний пункт.")


def books_menu():
    book = Book()
    while True:
        print("\n--- Книги ---")
        print("1) Додати")
        print("2) Список")
        print("3) Деталі")
        print("4) Редагувати")
        print("5) Видалити (soft)")
        print("0) Назад")

        c = input("Виберіть пункт: ").strip()
        if c == "0":
            break
        elif c == "1":
            book.add()
        elif c == "2":
            book.list_all()
        elif c == "3":
            book.details()
        elif c == "4":
            book.update()
        elif c == "5":
            book.delete()
        else:
            print("Невірний пункт.")


def sales_menu():
    sale = Sale()
    while True:
        print("\n=== Продажі ===")
        print("1) Продати книгу")
        print("0) Назад")

        c = input("Виберіть пункт: ").strip()
        if c == "0":
            break
        elif c == "1":
            sale.create_sale()
        else:
            print("Невірний пункт.")