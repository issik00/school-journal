import sqlite3

DB_NAME = "school.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def execute(query, params=(), fetchone=False, fetchall=False, commit=False):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)

    result = None
    if fetchone:
        result = cursor.fetchone()
    elif fetchall:
        result = cursor.fetchall()

    if commit:
        conn.commit()

    conn.close()
    return result


execute("""
CREATE TABLE IF NOT EXISTS classes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
)
""", commit=True)

execute("""
CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
)
""", commit=True)

execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    class_id INTEGER NOT NULL,
    FOREIGN KEY (class_id) REFERENCES classes(id)
)
""", commit=True)

execute("""
CREATE TABLE IF NOT EXISTS grades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    year TEXT NOT NULL,
    month TEXT NOT NULL,
    day INTEGER NOT NULL,
    value TEXT,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (subject_id) REFERENCES subjects(id),
    UNIQUE(student_id, subject_id, year, month, day)
)
""", commit=True)


def add_class(class_name):
    execute("INSERT INTO classes (name) VALUES (?)", (class_name,), commit=True)


def get_classes():
    rows = execute("SELECT name FROM classes ORDER BY name", fetchall=True)
    return [row[0] for row in rows]


def get_class_id(class_name):
    row = execute("SELECT id FROM classes WHERE name = ?", (class_name,), fetchone=True)
    return row[0] if row else None


def add_subject(subject_name):
    execute("INSERT INTO subjects (name) VALUES (?)", (subject_name,), commit=True)


def get_subjects():
    rows = execute("SELECT name FROM subjects ORDER BY name", fetchall=True)
    return [row[0] for row in rows]


def get_subject_id(subject_name):
    row = execute("SELECT id FROM subjects WHERE name = ?", (subject_name,), fetchone=True)
    return row[0] if row else None


def add_student(student_name, class_id):
    execute(
        "INSERT INTO students (name, class_id) VALUES (?, ?)",
        (student_name, class_id),
        commit=True
    )


def get_students_by_class(class_id):
    return execute(
        "SELECT id, name FROM students WHERE class_id = ? ORDER BY name",
        (class_id,),
        fetchall=True
    )


def delete_student(student_id):
    execute("DELETE FROM grades WHERE student_id = ?", (student_id,), commit=True)
    execute("DELETE FROM students WHERE id = ?", (student_id,), commit=True)


def save_grade(student_id, subject_id, year, month, day, value):
    row = execute("""
        SELECT id FROM grades
        WHERE student_id = ? AND subject_id = ? AND year = ? AND month = ? AND day = ?
    """, (student_id, subject_id, year, month, day), fetchone=True)

    if row:
        execute("""
            UPDATE grades
            SET value = ?
            WHERE student_id = ? AND subject_id = ? AND year = ? AND month = ? AND day = ?
        """, (value, student_id, subject_id, year, month, day), commit=True)
    else:
        execute("""
            INSERT INTO grades (student_id, subject_id, year, month, day, value)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (student_id, subject_id, year, month, day, value), commit=True)


def get_grade(student_id, subject_id, year, month, day):
    row = execute("""
        SELECT value FROM grades
        WHERE student_id = ? AND subject_id = ? AND year = ? AND month = ? AND day = ?
    """, (student_id, subject_id, year, month, day), fetchone=True)

    return row[0] if row else ""