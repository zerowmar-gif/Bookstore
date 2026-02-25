from database import init_db
from crud import employees_menu, books_menu, sales_menu
from reports import (
    report_employees_full,
    report_books_full,
    report_sales_full,
    sales_by_date,
    sales_by_period,
    sales_by_employee,
    most_sold_book_by_period,
    best_seller_by_profit,
    profit_by_period,
    top_author_by_period,
    top_genre_by_period,
)


def main():
    init_db()

    while True:
        print("\n=== ГОЛОВНЕ МЕНЮ ===")
        print("1) Співробітники")
        print("2) Книги")
        print("3) Продажі")
        print("4) Звіти")
        print("0) Вихід")

        choice = input("Оберіть пункт: ").strip()

        if choice == "0":
            print("Вихід.")
            break
        elif choice == "1":
            employees_menu()
        elif choice == "2":
            books_menu()
        elif choice == "3":
            sales_menu()
        elif choice == "4":
            while True:
                print("\n=== ЗВІТИ ===")
                print("1) Повна інформація про співробітників")
                print("2) Повна інформація про книги")
                print("3) Повна інформація про продажі")
                print("4) Продажі за дату")
                print("5) Продажі за період")
                print("6) Продажі конкретного співробітника (за період)")
                print("7) Найбільш продавана книга за період")
                print("8) Найуспішніший продавець за період (за прибутком)")
                print("9) Сумарний прибуток за період")
                print("10) ТОП автор за період (бонус)")
                print("11) ТОП жанр за період (бонус)")
                print("12) Експорт ВСІХ продажів у CSV")
                print("13) Експорт продажів за період у CSV")
                print("0) Назад")

                r = input("Оберіть: ").strip()

                if r == "0":
                    break
                elif r == "1":
                    report_employees_full()
                elif r == "2":
                    report_books_full()
                elif r == "3":
                    report_sales_full(export_csv=False)
                elif r == "4":
                    sales_by_date()
                elif r == "5":
                    sales_by_period(export_csv=False)
                elif r == "6":
                    sales_by_employee()
                elif r == "7":
                    most_sold_book_by_period()
                elif r == "8":
                    best_seller_by_profit()
                elif r == "9":
                    profit_by_period()
                elif r == "10":
                    top_author_by_period()
                elif r == "11":
                    top_genre_by_period()
                elif r == "12":
                    report_sales_full(export_csv=True)
                elif r == "13":
                    sales_by_period(export_csv=True)
                else:
                    print("Невірний пункт.")
        else:
            print("Невірний ввід. Спробуйте ще раз.")


if __name__ == "__main__":
    main()