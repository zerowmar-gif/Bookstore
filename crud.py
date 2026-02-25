import re
from datetime import date, datetime
from database import get_conn

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _input_non_empty(prompt):
    value = input(prompt).strip()
    if not value:
        raise ValueError("Поле не може бути порожнім.")
    return value


def _input_int(prompt, min_value=None):
    s = input(prompt).strip()
    if not s.isdigit():
        raise ValueError("Потрібно ввести ціле число.")
    v = int(s)
    if min_value is not None and v < min_value:
        raise ValueError(f"Число має бути >= {min_value}.")
    return v


def _input_float(prompt, min_value=None):
    s = input(prompt).strip().replace(",", ".")
    try:
        v = float(s)
    except ValueError:
        raise ValueError("Потрібно ввести число.")
    if min_value is not None and v < min_value:
        raise ValueError(f"Число має бути >= {min_value}.")
    return v


def _input_date(prompt):
    s = input(prompt).strip()
    try:
        datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Дата має бути у форматі YYYY-MM-DD.")
    return s


def _input_email(prompt):
    s = input(prompt).strip()
    if not EMAIL_RE.match(s):
        raise ValueError("Email має некоректний формат.")
    return s


class EmployeeCRUD:
    def add(self):
        print("\n--- Додати співробітника ---")
        try:
            name = _input_non_empty("ПІБ: ")
            position = input("Посада: ").strip()
            phone = input("Телефон: ").strip()
            email = _input_email("Email: ")

            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO employee (name, position, phone, email)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (name, position, phone, email),
                    )
            print("Співробітника додано.")
        except Exception as e:
            print("Помилка:", e)

    def list_all(self):
        print("\n--- Список співробітників ---")
        try:
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT id, name, position, phone, email
                        FROM employee
                        WHERE is_deleted = FALSE
                        ORDER BY id
                        """
                    )
                    rows = cur.fetchall()

            if not rows:
                print("Немає співробітників.")
                return

            print("ID | ПІБ | Посада | Телефон | Email")
            print("-" * 80)
            for r in rows:
                print(f"{r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]}")
        except Exception as e:
            print("Помилка:", e)

    def details(self):
        print("\n--- Деталі співробітника ---")
        try:
            emp_id = _input_int("Введіть ID: ", min_value=1)
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT id, name, position, phone, email
                        FROM employee
                        WHERE id = %s AND is_deleted = FALSE
                        """,
                        (emp_id,),
                    )
                    row = cur.fetchone()

            if row is None:
                print("Співробітника не знайдено.")
                return

            print(f"ID: {row[0]}")
            print(f"ПІБ: {row[1]}")
            print(f"Посада: {row[2]}")
            print(f"Телефон: {row[3]}")
            print(f"Email: {row[4]}")
        except Exception as e:
            print("Помилка:", e)

    def update(self):
        print("\n--- Редагувати співробітника ---")
        try:
            emp_id = _input_int("Введіть ID: ", min_value=1)

            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT name, position, phone, email
                        FROM employee
                        WHERE id=%s AND is_deleted=FALSE
                        """,
                        (emp_id,),
                    )
                    row = cur.fetchone()
                    if row is None:
                        print("Співробітника не знайдено.")
                        return

                    old_name, old_position, old_phone, old_email = row

                    print("Залиште порожнім, якщо не хочете змінювати.")
                    new_name = input(f"ПІБ ({old_name}): ").strip() or old_name
                    new_position = input(f"Посада ({old_position}): ").strip() or old_position
                    new_phone = input(f"Телефон ({old_phone}): ").strip() or old_phone
                    new_email = input(f"Email ({old_email}): ").strip() or old_email

                    if not new_name:
                        raise ValueError("ПІБ не може бути порожнім.")
                    if not EMAIL_RE.match(new_email):
                        raise ValueError("Email має некоректний формат.")

                    cur.execute(
                        """
                        UPDATE employee
                        SET name = %s, position = %s, phone = %s, email = %s
                        WHERE id=%s
                        """,
                        (new_name, new_position, new_phone, new_email, emp_id),
                    )

            print("Дані оновлено.")
        except Exception as e:
            print("Помилка:", e)

    def delete(self):
        print("\n--- Видалити співробітника (soft delete) ---")
        try:
            emp_id = _input_int("Введіть ID: ", min_value=1)
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT id FROM employee WHERE id=%s AND is_deleted=FALSE;",
                        (emp_id,),
                    )
                    if cur.fetchone() is None:
                        print("Співробітника не знайдено.")
                        return

                    cur.execute(
                        "UPDATE employee SET is_deleted=TRUE WHERE id=%s;",
                        (emp_id,),
                    )

            print("Співробітника позначено як видаленого.")
        except Exception as e:
            print("Помилка:", e)


class BookCRUD:
    def add(self):
        print("\n--- Додати книгу ---")
        try:
            isbn = _input_non_empty("ISBN: ")
            title = _input_non_empty("Назва: ")
            author = _input_non_empty("Автор: ")
            genre = input("Жанр: ").strip()
            year = _input_int("Рік публікації: ", min_value=1)
            cost_price = _input_float("Собівартість: ", min_value=0.01)
            sale_price = _input_float("Потенційна ціна продажу: ", min_value=0.01)
            quantity = _input_int("Кількість на складі: ", min_value=0)

            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO book (isbn, title, author, genre, year, cost_price, sale_price, quantity)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (isbn, title, author, genre, year, cost_price, sale_price, quantity),
                    )
            print("Книгу додано.")
        except Exception as e:
            print("Помилка:", e)

    def list_all(self):
        print("\n--- Список книг ---")
        try:
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT id, isbn, title, author, genre, year, cost_price, sale_price, quantity
                        FROM book
                        WHERE is_deleted = FALSE
                        ORDER BY id
                        """
                    )
                    rows = cur.fetchall()

            if not rows:
                print("Немає книг.")
                return

            print("ID | ISBN | Назва | Автор | Жанр | Рік | Собівартість | Ціна | К-ть")
            print("-" * 120)
            for r in rows:
                print(f"{r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} | {r[6]} | {r[7]} | {r[8]}")
        except Exception as e:
            print("Помилка:", e)

    def details(self):
        print("\n--- Деталі книги ---")
        try:
            book_id = _input_int("Введіть ID: ", min_value=1)
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT id, isbn, title, author, genre, year, cost_price, sale_price, quantity
                        FROM book
                        WHERE id=%s AND is_deleted=FALSE
                        """,
                        (book_id,),
                    )
                    row = cur.fetchone()
            if row is None:
                print("Книгу не знайдено.")
                return

            print(f"ID: {row[0]}")
            print(f"ISBN: {row[1]}")
            print(f"Назва: {row[2]}")
            print(f"Автор: {row[3]}")
            print(f"Жанр: {row[4]}")
            print(f"Рік: {row[5]}")
            print(f"Собівартість: {row[6]}")
            print(f"Потенційна ціна: {row[7]}")
            print(f"Залишок: {row[8]}")
        except Exception as e:
            print("Помилка:", e)

    def update(self):
        print("\n--- Редагувати книгу ---")
        try:
            book_id = _input_int("Введіть ID книги: ", min_value=1)
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT isbn, title, author, genre, year, cost_price, sale_price, quantity
                        FROM book
                        WHERE id=%s AND is_deleted=FALSE
                        """,
                        (book_id,),
                    )
                    row = cur.fetchone()
                    if row is None:
                        print("Книгу не знайдено.")
                        return

                    old_isbn, old_title, old_author, old_genre, old_year, old_cost, old_sale, old_qty = row
                    print("Залиште порожнім, якщо не хочете змінювати.")

                    new_isbn = input(f"ISBN ({old_isbn}): ").strip() or old_isbn
                    new_title = input(f"Назва ({old_title}): ").strip() or old_title
                    new_author = input(f"Автор ({old_author}): ").strip() or old_author
                    new_genre = input(f"Жанр ({old_genre}): ").strip() or old_genre

                    year_str = input(f"Рік ({old_year}): ").strip()
                    cost_str = input(f"Собівартість ({old_cost}): ").strip()
                    sale_str = input(f"Ціна ({old_sale}): ").strip()
                    qty_str = input(f"К-ть ({old_qty}): ").strip()

                    new_year = old_year if not year_str else int(year_str)
                    new_cost = float(old_cost) if not cost_str else float(cost_str.replace(",", "."))
                    new_sale = float(old_sale) if not sale_str else float(sale_str.replace(",", "."))
                    new_qty = int(old_qty) if not qty_str else int(qty_str)

                    if not new_title or not new_author:
                        raise ValueError("Назва та автор не можуть бути порожні.")
                    if new_cost <= 0 or new_sale <= 0:
                        raise ValueError("Ціни мають бути > 0.")
                    if new_qty < 0:
                        raise ValueError("К-ть не може бути від'ємною.")

                    cur.execute(
                        """
                        UPDATE book
                        SET isbn = %s, title = %s, author = %s, genre = %s, year = %s,
                            cost_price = %s, sale_price = %s, quantity = %s
                        WHERE id=%s
                        """,
                        (new_isbn, new_title, new_author, new_genre, new_year, new_cost, new_sale, new_qty, book_id),
                    )

            print("Книгу оновлено.")
        except Exception as e:
            print("Помилка:", e)

    def delete(self):
        print("\n--- Видалити книгу (soft delete) ---")
        try:
            book_id = _input_int("Введіть ID книги: ", min_value=1)
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT id FROM book WHERE id=%s AND is_deleted=FALSE;", (book_id,))
                    if cur.fetchone() is None:
                        print("Книгу не знайдено.")
                        return
                    cur.execute("UPDATE book SET is_deleted=TRUE WHERE id=%s;", (book_id,))
            print("Книгу позначено як видалену.")
        except Exception as e:
            print("Помилка:", e)


class SaleCRUD:
    def create_sale(self):
        print("\n--- Продаж книги ---")
        try:
            emp_id = _input_int("ID співробітника: ", min_value=1)
            book_id = _input_int("ID книги: ", min_value=1)
            quantity_sold = _input_int("Кількість: ", min_value=1)
            real_price = _input_float("Фактична сума продажу (TOTAL): ", min_value=0.01)

            with get_conn() as conn:
                with conn.transaction():
                    with conn.cursor() as cur:
                        cur.execute("SELECT id FROM employee WHERE id=%s AND is_deleted=FALSE;", (emp_id,))
                        if cur.fetchone() is None:
                            print("Співробітника не знайдено.")
                            return

                        cur.execute("SELECT quantity FROM book WHERE id=%s AND is_deleted=FALSE;", (book_id,))
                        row = cur.fetchone()
                        if row is None:
                            print("Книгу не знайдено.")
                            return

                        current_quantity = row[0]
                        if current_quantity < quantity_sold:
                            print("Недостатньо книг на складі.")
                            return

                        cur.execute(
                            "UPDATE book SET quantity = quantity - %s WHERE id=%s;",
                            (quantity_sold, book_id),
                        )

                        cur.execute(
                            """
                            INSERT INTO sale (employee_id, book_id, sale_date, real_price, quantity_sold)
                            VALUES (%s, %s, %s, %s, %s)
                            """,
                            (emp_id, book_id, date.today(), real_price, quantity_sold),
                        )

            print("Продаж виконано.")
        except Exception as e:
            print("Помилка:", e)

    def list_all(self):
        print("\n--- Список продажів ---")
        try:
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT s.id, s.sale_date, e.name, b.title, s.quantity_sold, s.real_price
                        FROM sale s
                        JOIN employee e ON e.id = s.employee_id
                        JOIN book b ON b.id = s.book_id
                        WHERE s.is_deleted=FALSE
                          AND e.is_deleted=FALSE
                          AND b.is_deleted=FALSE
                        ORDER BY s.id
                        """
                    )
                    rows = cur.fetchall()

            if not rows:
                print("Немає продажів.")
                return

            print("ID | Дата | Співробітник | Книга | К-ть | Сума (TOTAL)")
            print("-" * 100)
            for r in rows:
                print(f"{r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]}")
        except Exception as e:
            print("Помилка:", e)

    def details(self):
        print("\n--- Деталі продажу ---")
        try:
            sale_id = _input_int("Введіть ID продажу: ", min_value=1)
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT s.id, s.sale_date, e.name, b.title, s.quantity_sold, s.real_price
                        FROM sale s
                        JOIN employee e ON e.id = s.employee_id
                        JOIN book b ON b.id = s.book_id
                        WHERE s.id=%s AND s.is_deleted=FALSE
                        """,
                        (sale_id,),
                    )
                    row = cur.fetchone()

            if row is None:
                print("Продаж не знайдено.")
                return

            print(f"ID: {row[0]}")
            print(f"Дата: {row[1]}")
            print(f"Співробітник: {row[2]}")
            print(f"Книга: {row[3]}")
            print(f"Кількість: {row[4]}")
            print(f"Сума (TOTAL): {row[5]}")
        except Exception as e:
            print("Помилка:", e)

    def update(self):
        print("\n--- Редагувати продаж ---")
        try:
            sale_id = _input_int("ID продажу: ", min_value=1)

            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT employee_id, sale_date, real_price
                        FROM sale
                        WHERE id=%s AND is_deleted=FALSE
                        """,
                        (sale_id,),
                    )
                    row = cur.fetchone()
                    if row is None:
                        print("Продаж не знайдено.")
                        return

                    old_emp_id, old_date, old_total = row

                    print("Залиште порожнім, якщо не хочете змінювати.")
                    emp_str = input(f"Новий ID співробітника ({old_emp_id}): ").strip()
                    date_str = input(f"Нова дата ({old_date}) [YYYY-MM-DD]: ").strip()
                    total_str = input(f"Нова сума (TOTAL) ({old_total}): ").strip()

                    new_emp_id = old_emp_id if not emp_str else int(emp_str)
                    new_total = float(old_total) if not total_str else float(total_str.replace(",", "."))

                    if new_total <= 0:
                        raise ValueError("Сума має бути > 0.")

                    if date_str:
                        datetime.strptime(date_str, "%Y-%m-%d")
                        new_date = date_str
                    else:
                        new_date = old_date

                    cur.execute("SELECT id FROM employee WHERE id=%s AND is_deleted=FALSE;", (new_emp_id,))
                    if cur.fetchone() is None:
                        print("Співробітника не знайдено.")
                        return

                    cur.execute(
                        """
                        UPDATE sale
                        SET employee_id = %s, sale_date = %s, real_price = %s
                        WHERE id=%s
                        """,
                        (new_emp_id, new_date, new_total, sale_id),
                    )

            print("Продаж оновлено.")
        except Exception as e:
            print("Помилка:", e)

    def delete(self):
        print("\n--- Видалити продаж (soft delete) ---")
        try:
            sale_id = _input_int("ID продажу: ", min_value=1)

            with get_conn() as conn:
                with conn.transaction():
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            SELECT book_id, quantity_sold
                            FROM sale
                            WHERE id=%s AND is_deleted=FALSE
                            """,
                            (sale_id,),
                        )
                        row = cur.fetchone()
                        if row is None:
                            print("Продаж не знайдено.")
                            return

                        book_id, qty = row

                        cur.execute("UPDATE book SET quantity = quantity + %s WHERE id=%s;", (qty, book_id))
                        cur.execute("UPDATE sale SET is_deleted=TRUE WHERE id=%s;", (sale_id,))

            print("Продаж видалено (soft delete).")
        except Exception as e:
            print("Помилка:", e)


def employees_menu():
    emp = EmployeeCRUD()
    while True:
        print("\n--- СПІВРОБІТНИКИ ---")
        print("1) Додати")
        print("2) Список")
        print("3) Деталі")
        print("4) Редагувати")
        print("5) Видалити")
        print("0) Назад")

        choice = input("Оберіть пункт: ").strip()
        if choice == "0":
            break
        elif choice == "1":
            emp.add()
        elif choice == "2":
            emp.list_all()
        elif choice == "3":
            emp.details()
        elif choice == "4":
            emp.update()
        elif choice == "5":
            emp.delete()
        else:
            print("Невірний пункт.")


def books_menu():
    book = BookCRUD()
    while True:
        print("\n--- КНИГИ ---")
        print("1) Додати")
        print("2) Список")
        print("3) Деталі")
        print("4) Редагувати")
        print("5) Видалити")
        print("0) Назад")

        choice = input("Оберіть пункт: ").strip()
        if choice == "0":
            break
        elif choice == "1":
            book.add()
        elif choice == "2":
            book.list_all()
        elif choice == "3":
            book.details()
        elif choice == "4":
            book.update()
        elif choice == "5":
            book.delete()
        else:
            print("Невірний пункт.")


def sales_menu():
    sale = SaleCRUD()
    while True:
        print("\n--- ПРОДАЖІ ---")
        print("1) Створити продаж")
        print("2) Список продажів")
        print("3) Деталі продажу")
        print("4) Редагувати продаж")
        print("5) Видалити продаж")
        print("0) Назад")

        choice = input("Оберіть пункт: ").strip()
        if choice == "0":
            break
        elif choice == "1":
            sale.create_sale()
        elif choice == "2":
            sale.list_all()
        elif choice == "3":
            sale.details()
        elif choice == "4":
            sale.update()
        elif choice == "5":
            sale.delete()
        else:
            print("Невірний пункт.")