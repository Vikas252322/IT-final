import sqlite3

def connect():
    return sqlite3.connect("workforce.db", check_same_thread=False)

def create_tables():
    conn = connect()
    c = conn.cursor()

    # Users Table
    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)

    # Default Admin
    c.execute("SELECT * FROM users WHERE username='admin'")
    if not c.fetchone():
        c.execute("INSERT INTO users(username,password,role) VALUES('admin','admin123','Admin')")

    # Branches
    c.execute("""
    CREATE TABLE IF NOT EXISTS branches(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        branch_name TEXT UNIQUE
    )
    """)

    # Employees
    c.execute("""
    CREATE TABLE IF NOT EXISTS employees(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        branch_id INTEGER,
        role TEXT,
        salary REAL
    )
    """)

    # Skills
    c.execute("""
    CREATE TABLE IF NOT EXISTS skills(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        skill_name TEXT UNIQUE
    )
    """)

    # Employee Skills
    c.execute("""
    CREATE TABLE IF NOT EXISTS employee_skills(
        employee_id INTEGER,
        skill_id INTEGER,
        level INTEGER
    )
    """)

    # Leave Balance
    c.execute("""
    CREATE TABLE IF NOT EXISTS leave_balance(
        employee_id INTEGER UNIQUE,
        paid_left INTEGER DEFAULT 12,
        casual_left INTEGER DEFAULT 8,
        sick_left INTEGER DEFAULT 6
    )
    """)

    # Leave Records
    c.execute("""
    CREATE TABLE IF NOT EXISTS leave_records(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        leave_type TEXT,
        days INTEGER,
        date TEXT
    )
    """)

    # Payroll
    c.execute("""
    CREATE TABLE IF NOT EXISTS payroll(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        month TEXT,
        basic_salary REAL,
        deduction REAL,
        net_salary REAL
    )
    """)

    conn.commit()
    conn.close()
