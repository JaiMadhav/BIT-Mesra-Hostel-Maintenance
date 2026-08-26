from flask import Flask, request, jsonify, render_template, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "bit-mesra-hostel-demo-key")

DATABASE = "database.db"

CATEGORIES = [
    "Electrical / Power",
    "Wi-Fi / Internet",
    "Plumbing / Water",
    "Washroom / Hygiene",
    "Furniture / Room",
    "Washing Machine",
    "Geyser",
    "Cleaning",
    "Pest Control",
    "Other",
]

PRIORITIES = ["Low", "Medium", "High", "Urgent"]
STATUSES = ["Pending", "In Progress", "Resolved", "Rejected"]
HOSTELS = [f"H{i}" for i in range(1, 15)]

MAINTENANCE_STAFF = [
    "Electrical Maintenance",
    "Plumbing Maintenance",
    "Network Support",
    "Housekeeping",
    "General Maintenance",
]


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def is_logged_in():
    return "user_id" in session


def is_admin():
    return session.get("role") == "admin"


def is_warden():
    return session.get("role") == "warden"


def has_staff_access():
    return is_admin() or is_warden()


def get_scoped_complaint(conn, complaint_id):
    """Return a complaint only when the current user is allowed to access it."""
    if is_admin():
        return conn.execute(
            "SELECT * FROM complaints WHERE id = ?",
            (complaint_id,),
        ).fetchone()

    assigned_hostel = session.get("assigned_hostel")

    if not is_warden() or not assigned_hostel:
        return None

    return conn.execute(
        """
        SELECT *
        FROM complaints
        WHERE id = ? AND hostel_name = ?
        """,
        (complaint_id, assigned_hostel),
    ).fetchone()


@app.route("/")
def index():
    return render_template("index.html")


# -------------------------
# Authentication
# -------------------------

@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.get_json() or {}

    full_name = data.get("full_name", "").strip()
    roll_number = data.get("roll_number", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    assigned_hostel = data.get("assigned_hostel", "").strip()

    if not all([full_name, roll_number, email, password, assigned_hostel]):
        return jsonify({"error": "Please fill in all required fields."}), 400

    if not email.endswith("@bitmesra.ac.in"):
        return jsonify({"error": "Please use your BIT Mesra institute email."}), 400

    if assigned_hostel not in HOSTELS:
        return jsonify({"error": "Please select a valid hostel."}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must contain at least 6 characters."}), 400

    conn = get_db_connection()

    try:
        conn.execute(
            """
            INSERT INTO users
                (full_name, roll_number, email, password, role, assigned_hostel)
            VALUES (?, ?, ?, ?, 'student', ?)
            """,
            (
                full_name,
                roll_number,
                email,
                generate_password_hash(password),
                assigned_hostel,
            ),
        )
        conn.commit()

        return jsonify({
            "message": "Account created successfully."
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({
            "error": "An account with this email already exists."
        }), 400

    finally:
        conn.close()


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json() or {}

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({
            "error": "Email and password are required."
        }), 400

    conn = get_db_connection()

    user = conn.execute(
        "SELECT * FROM users WHERE email = ?",
        (email,),
    ).fetchone()

    conn.close()

    if not user or not check_password_hash(user["password"], password):
        return jsonify({
            "error": "Invalid email or password."
        }), 401

    session.clear()
    session["user_id"] = user["id"]
    session["role"] = user["role"]
    session["full_name"] = user["full_name"]
    session["email"] = user["email"]
    session["roll_number"] = user["roll_number"]
    session["assigned_hostel"] = user["assigned_hostel"]

    return jsonify({
        "message": "Login successful.",
        "role": user["role"],
        "full_name": user["full_name"],
        "assigned_hostel": user["assigned_hostel"],
    })


@app.route("/api/forgot-password", methods=["POST"])
def forgot_password():
    """Reset a local demo account after checking registered identity details."""
    data = request.get_json() or {}

    email = data.get("email", "").strip().lower()
    verification = data.get("verification", "").strip()
    new_password = data.get("new_password", "")

    if not email or not verification or not new_password:
        return jsonify({"error": "Please complete all reset fields."}), 400

    if len(new_password) < 6:
        return jsonify({"error": "New password must contain at least 6 characters."}), 400

    conn = get_db_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE email = ?",
        (email,),
    ).fetchone()

    if user is None:
        conn.close()
        return jsonify({"error": "No account was found for this email."}), 404

    # Students verify with their registered roll number.
    if user["role"] == "student":
        valid = verification.lower() == (user["roll_number"] or "").lower()

    # Demo wardens verify with their assigned hostel.
    elif user["role"] == "warden":
        valid = verification.upper() == (user["assigned_hostel"] or "").upper()

    # Admin resets are intentionally disabled from the public login page.
    else:
        conn.close()
        return jsonify({
            "error": "Admin password reset is disabled from the public login page. Change the admin password manually in the database or via the administration workflow."
        }), 403

    if not valid:
        conn.close()
        return jsonify({"error": "The verification details do not match the account."}), 403

    conn.execute(
        "UPDATE users SET password = ? WHERE id = ?",
        (generate_password_hash(new_password), user["id"]),
    )
    conn.commit()
    conn.close()

    return jsonify({
        "message": "Password reset successfully. You can now sign in with your new password."
    })


@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully."})


@app.route("/api/me")
def current_user():
    if not is_logged_in():
        return jsonify({"error": "Not logged in."}), 401

    return jsonify({
        "id": session["user_id"],
        "role": session["role"],
        "full_name": session["full_name"],
        "email": session["email"],
        "roll_number": session["roll_number"],
        "assigned_hostel": session.get("assigned_hostel"),
    })


# -------------------------
# Complaints
# -------------------------

@app.route("/api/complaints", methods=["GET", "POST"])
def complaints():
    if not is_logged_in():
        return jsonify({"error": "Please log in first."}), 401

    conn = get_db_connection()

    if request.method == "POST":
        if session.get("role") != "student":
            conn.close()
            return jsonify({
                "error": "Only students can submit complaints."
            }), 403

        data = request.get_json() or {}

        room = data.get("room_number", "").strip()
        category = data.get("category", "").strip()
        priority = data.get("priority", "Medium").strip()
        title = data.get("issue_title", "").strip()
        description = data.get("issue_description", "").strip()

        # The hostel is always taken from the authenticated student profile.
        hostel = session.get("assigned_hostel")

        if not all([hostel, room, category, priority, title, description]):
            conn.close()
            return jsonify({
                "error": "Please complete all complaint fields."
            }), 400

        if hostel not in HOSTELS:
            conn.close()
            return jsonify({
                "error": "Your profile has an invalid hostel assignment."
            }), 400

        if category not in CATEGORIES:
            conn.close()
            return jsonify({
                "error": "Please select a valid category."
            }), 400

        if priority not in PRIORITIES:
            conn.close()
            return jsonify({
                "error": "Please select a valid priority."
            }), 400

        cursor = conn.execute(
            """
            INSERT INTO complaints (
                student_name,
                roll_number,
                college_email,
                hostel_name,
                room_number,
                category,
                priority,
                issue_title,
                issue_description,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pending')
            """,
            (
                session["full_name"],
                session["roll_number"],
                session["email"],
                hostel,
                room,
                category,
                priority,
                title,
                description,
            ),
        )

        complaint_id = cursor.lastrowid

        conn.execute(
            """
            INSERT INTO complaint_history (
                complaint_id,
                status,
                changed_by,
                note
            )
            VALUES (?, 'Pending', ?, ?)
            """,
            (
                complaint_id,
                session["full_name"],
                "Complaint submitted",
            ),
        )

        conn.commit()
        conn.close()

        return jsonify({
            "message": "Complaint submitted successfully.",
            "complaint_id": complaint_id,
        }), 201

    # Student: own complaints only.
    if session["role"] == "student":
        rows = conn.execute(
            """
            SELECT *
            FROM complaints
            WHERE college_email = ?
            ORDER BY date_submitted DESC
            """,
            (session["email"],),
        ).fetchall()

    # Admin: all hostels.
    elif is_admin():
        rows = conn.execute(
            """
            SELECT *
            FROM complaints
            ORDER BY date_submitted DESC
            """
        ).fetchall()

    # Warden: assigned hostel only.
    else:
        assigned_hostel = session.get("assigned_hostel")

        if not assigned_hostel:
            conn.close()
            return jsonify({
                "error": "No hostel is assigned to this warden account."
            }), 403

        rows = conn.execute(
            """
            SELECT *
            FROM complaints
            WHERE hostel_name = ?
            ORDER BY date_submitted DESC
            """,
            (assigned_hostel,),
        ).fetchall()

    conn.close()
    return jsonify([dict(row) for row in rows])


@app.route("/api/complaints/<int:complaint_id>", methods=["PATCH"])
def update_complaint(complaint_id):
    if not has_staff_access():
        return jsonify({
            "error": "You do not have permission to update complaints."
        }), 403

    data = request.get_json() or {}

    status = data.get("status")
    assigned_staff = data.get("assigned_staff")
    resolution_note = data.get("resolution_note")

    if status is not None and status not in STATUSES:
        return jsonify({
            "error": "Invalid complaint status."
        }), 400

    if assigned_staff is not None and assigned_staff not in MAINTENANCE_STAFF + [""]:
        return jsonify({
            "error": "Invalid maintenance staff selection."
        }), 400

    conn = get_db_connection()

    complaint = get_scoped_complaint(conn, complaint_id)

    if complaint is None:
        conn.close()
        return jsonify({
            "error": "Complaint not found or outside your hostel scope."
        }), 404

    old_status = complaint["status"]
    new_status = status if status is not None else old_status

    old_assigned = complaint["assigned_staff"]
    new_assigned = (
        assigned_staff
        if assigned_staff is not None
        else old_assigned
    )

    old_note = complaint["resolution_note"]
    new_note = (
        resolution_note.strip()
        if isinstance(resolution_note, str)
        else old_note
    )

    if is_warden() and new_status == "Rejected":
        conn.close()
        return jsonify({
            "error": "Only an administrator can reject complaints."
        }), 403

    if new_status == "In Progress" and not new_assigned:
        conn.close()
        return jsonify({
            "error": "Assign maintenance staff before moving the complaint to In Progress."
        }), 400

    if new_status == "Resolved" and not new_note:
        conn.close()
        return jsonify({
            "error": "Add a resolution note before marking the complaint as resolved."
        }), 400

    conn.execute(
        """
        UPDATE complaints
        SET status = ?,
            assigned_staff = ?,
            resolution_note = ?,
            date_updated = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (
            new_status,
            new_assigned,
            new_note,
            complaint_id,
        ),
    )

    if (
        new_status != old_status
        or new_assigned != old_assigned
        or new_note != old_note
    ):
        changes = []

        if new_status != old_status:
            changes.append(f"Status: {new_status}")

        if new_assigned != old_assigned:
            changes.append(
                f"Assigned to: {new_assigned}"
                if new_assigned
                else "Assignment removed"
            )

        if new_note != old_note and new_note:
            changes.append("Resolution note updated")

        conn.execute(
            """
            INSERT INTO complaint_history (
                complaint_id,
                status,
                changed_by,
                note
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                complaint_id,
                new_status,
                session["full_name"],
                " | ".join(changes),
            ),
        )

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Complaint updated successfully."
    })


@app.route("/api/complaints/<int:complaint_id>/history")
def complaint_history(complaint_id):
    if not is_logged_in():
        return jsonify({
            "error": "Please log in first."
        }), 401

    conn = get_db_connection()

    complaint = conn.execute(
        "SELECT * FROM complaints WHERE id = ?",
        (complaint_id,),
    ).fetchone()

    if complaint is None:
        conn.close()
        return jsonify({
            "error": "Complaint not found."
        }), 404

    if session["role"] == "student":
        allowed = complaint["college_email"] == session["email"]
    elif is_admin():
        allowed = True
    else:
        allowed = complaint["hostel_name"] == session.get("assigned_hostel")

    if not allowed:
        conn.close()
        return jsonify({
            "error": "Unauthorized."
        }), 403

    rows = conn.execute(
        """
        SELECT status, changed_by, note, changed_at
        FROM complaint_history
        WHERE complaint_id = ?
        ORDER BY changed_at ASC, id ASC
        """,
        (complaint_id,),
    ).fetchall()

    conn.close()
    return jsonify([dict(row) for row in rows])


# -------------------------
# Warden dashboard
# -------------------------

@app.route("/api/dashboard")
def dashboard():
    if not has_staff_access():
        return jsonify({
            "error": "Warden/Admin access required."
        }), 403

    conn = get_db_connection()

    if is_warden():
        assigned_hostel = session.get("assigned_hostel")

        if not assigned_hostel:
            conn.close()
            return jsonify({
                "error": "No hostel is assigned to this warden account."
            }), 403

        where = "WHERE hostel_name = ?"
        params = (assigned_hostel,)

    else:
        where = ""
        params = ()

    total = conn.execute(
        f"SELECT COUNT(*) AS count FROM complaints {where}",
        params,
    ).fetchone()["count"]

    pending = conn.execute(
        f"SELECT COUNT(*) AS count FROM complaints "
        f"{'WHERE hostel_name = ? AND' if is_warden() else 'WHERE'} "
        f"status = 'Pending'",
        params,
    ).fetchone()["count"]

    in_progress = conn.execute(
        f"SELECT COUNT(*) AS count FROM complaints "
        f"{'WHERE hostel_name = ? AND' if is_warden() else 'WHERE'} "
        f"status = 'In Progress'",
        params,
    ).fetchone()["count"]

    resolved = conn.execute(
        f"SELECT COUNT(*) AS count FROM complaints "
        f"{'WHERE hostel_name = ? AND' if is_warden() else 'WHERE'} "
        f"status = 'Resolved'",
        params,
    ).fetchone()["count"]

    urgent = conn.execute(
        f"SELECT COUNT(*) AS count FROM complaints "
        f"{'WHERE hostel_name = ? AND' if is_warden() else 'WHERE'} "
        f"priority = 'Urgent'",
        params,
    ).fetchone()["count"]

    if is_warden():
        by_category = conn.execute(
            """
            SELECT category, COUNT(*) AS count
            FROM complaints
            WHERE hostel_name = ?
            GROUP BY category
            ORDER BY count DESC
            """,
            (assigned_hostel,),
        ).fetchall()

        by_hostel = conn.execute(
            """
            SELECT hostel_name, COUNT(*) AS count
            FROM complaints
            WHERE hostel_name = ?
            GROUP BY hostel_name
            ORDER BY count DESC
            """,
            (assigned_hostel,),
        ).fetchall()

    else:
        by_category = conn.execute(
            """
            SELECT category, COUNT(*) AS count
            FROM complaints
            GROUP BY category
            ORDER BY count DESC
            """
        ).fetchall()

        by_hostel = conn.execute(
            """
            SELECT hostel_name, COUNT(*) AS count
            FROM complaints
            GROUP BY hostel_name
            ORDER BY count DESC
            """
        ).fetchall()

    conn.close()

    return jsonify({
        "total": total,
        "pending": pending,
        "in_progress": in_progress,
        "resolved": resolved,
        "urgent": urgent,
        "by_category": [dict(row) for row in by_category],
        "by_hostel": [dict(row) for row in by_hostel],
    })


# -------------------------
# Admin-only directories
# -------------------------

@app.route("/api/students")
def students():
    if not is_admin():
        return jsonify({
            "error": "Administrator access required."
        }), 403

    conn = get_db_connection()

    rows = conn.execute(
        """
        SELECT id, full_name, roll_number, email, assigned_hostel
        FROM users
        WHERE role = 'student'
        ORDER BY full_name
        """
    ).fetchall()

    total = conn.execute(
        "SELECT COUNT(*) AS count FROM users WHERE role = 'student'"
    ).fetchone()["count"]

    conn.close()

    return jsonify({
        "total": total,
        "students": [dict(row) for row in rows],
    })


@app.route("/api/wardens")
def wardens():
    if not is_admin():
        return jsonify({
            "error": "Administrator access required."
        }), 403

    conn = get_db_connection()

    rows = conn.execute(
        """
        SELECT id, full_name, email, assigned_hostel
        FROM users
        WHERE role = 'warden'
        ORDER BY assigned_hostel
        """
    ).fetchall()

    conn.close()

    return jsonify([dict(row) for row in rows])


if __name__ == "__main__":
    app.run(debug=True, port=5000)
