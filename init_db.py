import sqlite3
from werkzeug.security import generate_password_hash

DATABASE = "database.db"

HOSTELS = [f"H{i}" for i in range(1, 15)]

connection = sqlite3.connect(DATABASE)
cursor = connection.cursor()

# Fresh local development database.
connection.execute("PRAGMA foreign_keys = ON")
connection.execute("DROP TABLE IF EXISTS complaint_history")
connection.execute("DROP TABLE IF EXISTS complaints")
connection.execute("DROP TABLE IF EXISTS users")


# -------------------------
# Users
# -------------------------

connection.execute("""
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        roll_number TEXT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'student',
        assigned_hostel TEXT
    )
""")


# -------------------------
# Demo administrator
# -------------------------

ADMIN_EMAIL = "admin.demo@bitmesra.ac.in"
ADMIN_PASSWORD = "BITMesra@2026"

cursor.execute("""
    INSERT INTO users
        (full_name, email, password, role, assigned_hostel)
    VALUES (?, ?, ?, 'admin', NULL)
""", (
    "Hostel System Administrator (Demo)",
    ADMIN_EMAIL,
    generate_password_hash(ADMIN_PASSWORD),
))


# -------------------------
# Demo wardens
# -------------------------

WARDEN_PASSWORD = "BITMesra@2026"

wardens = [
    ("Hostel 1 Warden (Demo)", "hostel1.warden.demo@bitmesra.ac.in", "H1"),
    ("Hostel 2 Warden (Demo)", "hostel2.warden.demo@bitmesra.ac.in", "H2"),
    ("Hostel 3 Warden (Demo)", "hostel3.warden.demo@bitmesra.ac.in", "H3"),
    ("Hostel 4 Warden (Demo)", "hostel4.warden.demo@bitmesra.ac.in", "H4"),
    ("Hostel 5 Warden (Demo)", "hostel5.warden.demo@bitmesra.ac.in", "H5"),
    ("Hostel 6 Warden (Demo)", "hostel6.warden.demo@bitmesra.ac.in", "H6"),
    ("Hostel 7 Warden (Demo)", "hostel7.warden.demo@bitmesra.ac.in", "H7"),
    ("Hostel 8 Warden (Demo)", "hostel8.warden.demo@bitmesra.ac.in", "H8"),
    ("Hostel 9 Warden (Demo)", "hostel9.warden.demo@bitmesra.ac.in", "H9"),
    ("Hostel 10 Warden (Demo)", "hostel10.warden.demo@bitmesra.ac.in", "H10"),
    ("Hostel 11 Warden (Demo)", "hostel11.warden.demo@bitmesra.ac.in", "H11"),
    ("Hostel 12 Warden (Demo)", "hostel12.warden.demo@bitmesra.ac.in", "H12"),
    ("Hostel 13 Warden (Demo)", "hostel13.warden.demo@bitmesra.ac.in", "H13"),
    ("Hostel 14 Warden (Demo)", "hostel14.warden.demo@bitmesra.ac.in", "H14"),
]

for name, email, hostel in wardens:
    cursor.execute("""
        INSERT INTO users
            (full_name, email, password, role, assigned_hostel)
        VALUES (?, ?, ?, 'warden', ?)
    """, (
        name,
        email,
        generate_password_hash(WARDEN_PASSWORD),
        hostel,
    ))


# -------------------------
# Complaints
# -------------------------

connection.execute("""
    CREATE TABLE complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT NOT NULL,
        roll_number TEXT NOT NULL,
        college_email TEXT NOT NULL,
        hostel_name TEXT NOT NULL,
        room_number TEXT NOT NULL,
        category TEXT NOT NULL,
        priority TEXT NOT NULL DEFAULT 'Medium',
        issue_title TEXT NOT NULL,
        issue_description TEXT NOT NULL,
        assigned_staff TEXT,
        resolution_note TEXT,
        status TEXT NOT NULL DEFAULT 'Pending',
        date_submitted TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        date_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")


# -------------------------
# Complaint history
# -------------------------

connection.execute("""
    CREATE TABLE complaint_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        complaint_id INTEGER NOT NULL,
        status TEXT NOT NULL,
        changed_by TEXT NOT NULL,
        note TEXT,
        changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (complaint_id)
            REFERENCES complaints(id)
            ON DELETE CASCADE
    )
""")

connection.commit()
connection.close()

print("BIT Mesra hostel database initialized successfully.")
print(f"Hostels configured: {len(HOSTELS)}")
print(f"Demo wardens created: {len(wardens)}")
print(f"Admin account: {ADMIN_EMAIL}")
print("Demo account password: BITMesra@2026")
