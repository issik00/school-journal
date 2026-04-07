import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog
import csv
import datetime
import calendar
import database

root = tk.Tk()
root.title("Школьный журнал")
root.geometry("1800x750")

months = {
    "Январь": 1, "Февраль": 2, "Март": 3, "Апрель": 4,
    "Май": 5, "Июнь": 6, "Июль": 7, "Август": 8,
    "Сентябрь": 9, "Октябрь": 10, "Ноябрь": 11, "Декабрь": 12
}

weekdays_short = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
years = [str(year) for year in range(2024, 2036)]
grade_values = ["", "2", "3", "4", "5", "Н", "Б"]


def get_days_in_month(year, month_name):
    return calendar.monthrange(int(year), months[month_name])[1]


def get_calendar_weeks(year, month_name):
    return calendar.Calendar(firstweekday=0).monthdayscalendar(int(year), months[month_name])


def update_combo(combo, values):
    combo["values"] = values
    if values and combo.get() not in values:
        combo.current(0)


def update_class_combo():
    update_combo(combo_class, database.get_classes())


def update_subject_combo():
    update_combo(combo_subject, database.get_subjects())


def ask_name(title, prompt):
    value = simpledialog.askstring(title, prompt)
    return value.strip() if value and value.strip() else None


def add_class():
    class_name = ask_name("Добавить класс", "Введите класс:")
    if not class_name:
        return
    try:
        database.add_class(class_name)
        update_class_combo()
        create_table()
    except:
        messagebox.showinfo("Информация", "Такой класс уже есть")


def add_subject():
    subject_name = ask_name("Добавить предмет", "Введите предмет:")
    if not subject_name:
        return
    try:
        database.add_subject(subject_name)
        update_subject_combo()
        create_table()
    except:
        messagebox.showinfo("Информация", "Такой предмет уже есть")


def add_student():
    selected_class = combo_class.get()
    if not selected_class:
        messagebox.showerror("Ошибка", "Сначала выберите класс")
        return

    student_name = ask_name("Добавить ученика", "Введите ФИО ученика:")
    if not student_name:
        return

    database.add_student(student_name, database.get_class_id(selected_class))
    create_table()


def delete_student():
    selected_class = combo_class.get()
    if not selected_class:
        messagebox.showerror("Ошибка", "Сначала выберите класс")
        return

    class_id = database.get_class_id(selected_class)
    students = database.get_students_by_class(class_id)

    if not students:
        messagebox.showinfo("Информация", "В этом классе нет учеников")
        return

    delete_window = tk.Toplevel(root)
    delete_window.title("Удалить ученика")
    delete_window.geometry("420x380")
    delete_window.grab_set()

    tk.Label(delete_window, text="Выберите ученика для удаления:", font=("Arial", 12)).pack(pady=10)

    listbox = tk.Listbox(delete_window, width=45, height=14, font=("Arial", 11))
    listbox.pack(pady=10, padx=10, fill="both", expand=True)

    for _, name in students:
        listbox.insert(tk.END, name)

    def confirm_delete():
        selected_index = listbox.curselection()
        if not selected_index:
            messagebox.showerror("Ошибка", "Сначала выберите ученика")
            return

        student_id, student_name = students[selected_index[0]]

        if messagebox.askyesno(
            "Подтверждение",
            f"Удалить ученика:\n{student_name}?\n\nВсе его оценки тоже удалятся."
        ):
            database.delete_student(student_id)
            delete_window.destroy()
            create_table()
            messagebox.showinfo("Готово", "Ученик удалён")

    tk.Button(
        delete_window, text="Удалить", command=confirm_delete,
        bg="#d9534f", fg="white", width=16
    ).pack(pady=10)


def save_grade(event, student_id, day, combobox):
    selected_subject = combo_subject.get()
    if not selected_subject:
        return

    selected_month = combo_month.get()
    selected_year = combo_year.get()
    subject_id = database.get_subject_id(selected_subject)

    new_value = combobox.get()
    old_value = database.get_grade(student_id, subject_id, selected_year, selected_month, day) or ""

    if old_value and old_value != new_value:
        answer = messagebox.askyesno(
            "Подтверждение изменения",
            f"В этой ячейке уже стоит значение: {old_value}\nЗаменить его на: {new_value}?"
        )
        if not answer:
            combobox.set(old_value)
            return

    database.save_grade(student_id, subject_id, selected_year, selected_month, day, new_value)


def export_to_excel():
    selected_class = combo_class.get()
    selected_subject = combo_subject.get()
    selected_month = combo_month.get()
    selected_year = combo_year.get()

    if not selected_class:
        messagebox.showerror("Ошибка", "Сначала выберите класс")
        return
    if not selected_subject:
        messagebox.showerror("Ошибка", "Сначала выберите предмет")
        return

    class_id = database.get_class_id(selected_class)
    subject_id = database.get_subject_id(selected_subject)
    students = database.get_students_by_class(class_id)

    if not students:
        messagebox.showinfo("Информация", "В этом классе нет учеников")
        return

    days = get_days_in_month(selected_year, selected_month)
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")],
        initialfile=f"Журнал_{selected_class}_{selected_subject}_{selected_month}_{selected_year}.csv"
    )

    if not file_path:
        return

    with open(file_path, mode="w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow([f"Журнал: {selected_class} | {selected_subject} | {selected_month} | {selected_year}"])
        writer.writerow([])

        header_weekdays = ["День"]
        header_days = ["ФИО"]
        month_number = months[selected_month]

        for day in range(1, days + 1):
            weekday_index = datetime.date(int(selected_year), month_number, day).weekday()
            header_weekdays.append(weekdays_short[weekday_index])
            header_days.append(str(day))

        writer.writerow(header_weekdays)
        writer.writerow(header_days)

        for student_id, student_name in students:
            row = [student_name]
            for day in range(1, days + 1):
                value = database.get_grade(student_id, subject_id, selected_year, selected_month, day)
                row.append(value if value is not None else "")
            writer.writerow(row)

    messagebox.showinfo("Готово", f"Файл сохранён:\n{file_path}")


def make_label(parent, text="", width=None, height=2, bg=None, row=0, column=0, columnspan=1, sticky="nsew",
               font=None, fg=None, relief="solid", anchor="center"):
    label = tk.Label(
        parent, text=text, width=width, height=height, bg=bg,
        font=font, fg=fg, relief=relief, anchor=anchor
    )
    label.grid(row=row, column=column, columnspan=columnspan, sticky=sticky)
    return label


def create_table(event=None):
    for widget in table_frame.winfo_children():
        widget.destroy()

    selected_month = combo_month.get()
    selected_year = combo_year.get()
    selected_class = combo_class.get()
    selected_subject = combo_subject.get()

    weeks = get_calendar_weeks(selected_year, selected_month)

    make_label(table_frame, "", width=25, bg="#b7d9f7", row=0, column=0)
    make_label(table_frame, "", width=25, bg="#d9ecff", row=1, column=0)
    make_label(table_frame, "ФИО", width=25, bg="lightblue", row=2, column=0)

    current_column = 1
    valid_days = []
    week_number = 1

    for week in weeks:
        days_in_this_week = [day for day in week if day != 0]
        if not days_in_this_week:
            continue

        make_label(
            table_frame, f"{week_number} неделя", bg="#b7d9f7",
            row=0, column=current_column, columnspan=len(days_in_this_week)
        )
        current_column += len(days_in_this_week)
        week_number += 1

    current_column = 1
    for week in weeks:
        for weekday_index, day in enumerate(week):
            if day == 0:
                continue

            bg_color = "#f7d6d6" if weekday_index in [5, 6] else "#d9ecff"
            make_label(
                table_frame, weekdays_short[weekday_index], width=4,
                bg=bg_color, row=1, column=current_column
            )
            valid_days.append((day, current_column, weekday_index))
            current_column += 1

    for day, column_index, weekday_index in valid_days:
        bg_color = "#ffe3e3" if weekday_index in [5, 6] else "lightblue"
        make_label(table_frame, str(day), width=4, bg=bg_color, row=2, column=column_index)

    total_columns = len(valid_days)

    if not selected_class:
        make_label(
            table_frame, "Добавьте класс", row=3, column=0,
            columnspan=total_columns + 1, font=("Arial", 14), fg="gray", relief="flat"
        )
        return

    if not selected_subject:
        make_label(
            table_frame, "Добавьте предмет", row=3, column=0,
            columnspan=total_columns + 1, font=("Arial", 14), fg="gray", relief="flat"
        )
        return

    class_id = database.get_class_id(selected_class)
    subject_id = database.get_subject_id(selected_subject)
    students = database.get_students_by_class(class_id)

    if not students:
        make_label(
            table_frame, "В этом классе пока нет учеников", row=3, column=0,
            columnspan=total_columns + 1, font=("Arial", 14), fg="gray", relief="flat"
        )
        return

    for row_index, (student_id, student_name) in enumerate(students, start=3):
        make_label(table_frame, student_name, width=25, row=row_index, column=0, anchor="w")

        for day, column_index, _ in valid_days:
            combo = ttk.Combobox(table_frame, values=grade_values, width=3, state="readonly")
            combo.grid(row=row_index, column=column_index, sticky="nsew")

            saved_value = database.get_grade(student_id, subject_id, selected_year, selected_month, day)
            combo.set(saved_value if saved_value is not None else "")

            combo.bind(
                "<<ComboboxSelected>>",
                lambda event, s_id=student_id, d=day, c=combo: save_grade(event, s_id, d, c)
            )


top_frame = tk.Frame(root)
top_frame.pack(pady=10)

tk.Label(top_frame, text="Класс:").grid(row=0, column=0, padx=5)
combo_class = ttk.Combobox(top_frame, values=[], state="readonly", width=12)
combo_class.grid(row=0, column=1, padx=5)
combo_class.bind("<<ComboboxSelected>>", create_table)

tk.Button(top_frame, text="Добавить класс", command=add_class).grid(row=0, column=2, padx=5)

tk.Label(top_frame, text="Месяц:").grid(row=0, column=3, padx=5)
combo_month = ttk.Combobox(top_frame, values=list(months.keys()), state="readonly", width=12)
combo_month.grid(row=0, column=4, padx=5)
combo_month.current(0)
combo_month.bind("<<ComboboxSelected>>", create_table)

tk.Label(top_frame, text="Предмет:").grid(row=0, column=5, padx=5)
combo_subject = ttk.Combobox(top_frame, values=[], state="readonly", width=15)
combo_subject.grid(row=0, column=6, padx=5)
combo_subject.bind("<<ComboboxSelected>>", create_table)

tk.Button(top_frame, text="Добавить предмет", command=add_subject).grid(row=0, column=7, padx=5)
tk.Button(top_frame, text="Добавить ученика", command=add_student).grid(row=0, column=8, padx=8)
tk.Button(top_frame, text="Удалить ученика", command=delete_student).grid(row=0, column=9, padx=8)
tk.Button(top_frame, text="Экспорт в Excel", command=export_to_excel).grid(row=0, column=10, padx=8)

tk.Label(top_frame, text="Год:").grid(row=0, column=11, padx=5)
combo_year = ttk.Combobox(top_frame, values=years, state="readonly", width=10)
combo_year.grid(row=0, column=12, padx=5)
current_year = datetime.datetime.now().year
combo_year.set(str(current_year if current_year <= 2035 else 2035))
combo_year.bind("<<ComboboxSelected>>", create_table)

table_container = tk.Frame(root)
table_container.pack(fill="both", expand=True, padx=10, pady=10)

canvas = tk.Canvas(table_container)
scrollbar_x = tk.Scrollbar(table_container, orient="horizontal", command=canvas.xview)
scrollbar_y = tk.Scrollbar(table_container, orient="vertical", command=canvas.yview)

table_frame = tk.Frame(canvas)
table_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

canvas.create_window((0, 0), window=table_frame, anchor="nw")
canvas.configure(xscrollcommand=scrollbar_x.set, yscrollcommand=scrollbar_y.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar_y.pack(side="right", fill="y")
scrollbar_x.pack(side="bottom", fill="x")

update_class_combo()
update_subject_combo()
create_table()

root.mainloop()