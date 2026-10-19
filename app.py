from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash
)
import mysql.connector
from mysql.connector import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
from dotenv import load_dotenv
import os
import secrets

# --------------------------------------------------
# APPLICATION SETUP
# --------------------------------------------------

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.permanent_session_lifetime = timedelta(minutes=30)


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("MYSQL_PASSWORD"),
        database="student_portal"
    )


# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.route("/")
def home():
    return redirect(url_for("login"))


# --------------------------------------------------
# LOGIN
# --------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT *
                FROM users
                WHERE email = %s
            """, (email,))
            user = cursor.fetchone()
        finally:
            cursor.close()
            connection.close()

        if user and check_password_hash(user["password"], password):
            session.clear()
            session.permanent = True

            session["user_id"] = user["id"]
            session["name"] = user["full_name"]
            session["email"] = user["email"]
            session["role"] = user["role"]
            session["must_change_password"] = bool(
                user["must_change_password"]
            )

            if (
                user["role"] == "student"
                and user["must_change_password"]
            ):
                return redirect(url_for("change_password"))

            if user["role"] == "admin":
                return redirect(url_for("admin_dashboard"))

            return redirect(url_for("dashboard"))

        error = "Invalid email or password."

    return render_template("login.html", error=error)


# --------------------------------------------------
# REQUIRE TEMPORARY PASSWORD CHANGE
# --------------------------------------------------

@app.before_request
def require_password_change():
    if (
        "user_id" not in session
        or session.get("role") != "student"
    ):
        return None

    if request.endpoint in {
        "change_password", "logout", "static"
    }:
        return None

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT must_change_password
            FROM users
            WHERE id = %s
        """, (session["user_id"],))
        user = cursor.fetchone()
    finally:
        cursor.close()
        connection.close()

    if user is None:
        session.clear()
        return redirect(url_for("login"))

    session["must_change_password"] = bool(
        user["must_change_password"]
    )

    if user["must_change_password"]:
        return redirect(url_for("change_password"))

    return None


# --------------------------------------------------
# CHANGE TEMPORARY PASSWORD
# --------------------------------------------------

@app.route("/change-password", methods=["GET", "POST"])
def change_password():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "student":
        return redirect(url_for("admin_dashboard"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT password, must_change_password
            FROM users
            WHERE id = %s
        """, (session["user_id"],))
        user = cursor.fetchone()
    finally:
        cursor.close()
        connection.close()

    if user is None:
        session.clear()
        return redirect(url_for("login"))

    if not user["must_change_password"]:
        session["must_change_password"] = False
        return redirect(url_for("dashboard"))

    if "password_change_csrf" not in session:
        session["password_change_csrf"] = secrets.token_urlsafe(32)

    error = None

    if request.method == "POST":
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")
        csrf_token = request.form.get("csrf_token", "")

        if not secrets.compare_digest(
            csrf_token, session["password_change_csrf"]
        ):
            error = "Invalid form submission. Please try again."

        elif len(new_password) < 12:
            error = "Password must contain at least 12 characters."

        elif new_password != confirm_password:
            error = "The passwords do not match."

        elif check_password_hash(user["password"], new_password):
            error = "Choose a different password."

        else:
            hashed_password = generate_password_hash(new_password)

            connection = get_db_connection()
            cursor = connection.cursor()

            try:
                cursor.execute("""
                    UPDATE users
                    SET password = %s,
                        must_change_password = 0
                    WHERE id = %s
                      AND must_change_password = 1
                """, (hashed_password, session["user_id"]))

                if cursor.rowcount != 1:
                    connection.rollback()
                    error = "Password could not be updated."
                else:
                    connection.commit()

            except mysql.connector.Error:
                connection.rollback()
                error = "Database error. Please try again."

            finally:
                cursor.close()
                connection.close()

            if error is None:
                session["must_change_password"] = False
                session.pop("password_change_csrf", None)
                flash("Your password has been changed successfully.")
                return redirect(url_for("dashboard"))

    return render_template(
        "change_password.html",
        error=error,
        csrf_token=session["password_change_csrf"]
    )


# --------------------------------------------------
# STUDENT DASHBOARD
# --------------------------------------------------

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "student":
        return redirect(url_for("admin_dashboard"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            COUNT(*) AS total_classes,
            SUM(
                CASE
                    WHEN attendance.status = 'Present' THEN 1
                    ELSE 0
                END
            ) AS classes_present
        FROM attendance
        JOIN students
            ON attendance.student_id = students.id
        WHERE students.user_id = %s
    """, (session["user_id"],))

    attendance_data = cursor.fetchone()
    total_classes = attendance_data["total_classes"] or 0
    classes_present = attendance_data["classes_present"] or 0

    if total_classes > 0:
        attendance_percentage = round(
            (classes_present / total_classes) * 100
        )
    else:
        attendance_percentage = 0

    cursor.execute("""
        SELECT COUNT(*) AS upcoming_assignments
        FROM assignments
        JOIN enrolments
            ON assignments.module_id = enrolments.module_id
        JOIN students
            ON enrolments.student_id = students.id
        WHERE students.user_id = %s
          AND assignments.deadline >= CURDATE()
          AND assignments.status != 'Completed'
    """, (session["user_id"],))

    assignment_data = cursor.fetchone()
    upcoming_assignments = (
        assignment_data["upcoming_assignments"] or 0
    )

    cursor.execute("""
        SELECT AVG(grades.grade) AS average_grade
        FROM grades
        JOIN students
            ON grades.student_id = students.id
        WHERE students.user_id = %s
    """, (session["user_id"],))

    grade_data = cursor.fetchone()

    if grade_data["average_grade"] is not None:
        average_grade = round(float(grade_data["average_grade"]))
    else:
        average_grade = 0

    cursor.close()
    connection.close()

    return render_template(
        "dashboard.html",
        attendance_percentage=attendance_percentage,
        upcoming_assignments=upcoming_assignments,
        average_grade=average_grade
    )


# --------------------------------------------------
# STUDENT ATTENDANCE
# --------------------------------------------------

@app.route("/attendance")
def attendance():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "student":
        return redirect(url_for("admin_dashboard"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            modules.module_name,
            modules.module_code,
            attendance.attendance_date,
            attendance.status
        FROM attendance
        JOIN students
            ON attendance.student_id = students.id
        JOIN modules
            ON attendance.module_id = modules.id
        WHERE students.user_id = %s
        ORDER BY attendance.attendance_date DESC
    """, (session["user_id"],))

    attendance_records = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "attendance.html",
        attendance_records=attendance_records
    )


# --------------------------------------------------
# STUDENT ASSIGNMENTS
# --------------------------------------------------

@app.route("/assignments")
def assignments():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "student":
        return redirect(url_for("admin_dashboard"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Show only assignments for enrolled modules
    cursor.execute("""
        SELECT
            assignments.id,
            modules.module_name,
            modules.module_code,
            assignments.title,
            assignments.description,
            assignments.deadline,
            assignments.status
        FROM assignments
        JOIN modules
            ON assignments.module_id = modules.id
        JOIN enrolments
            ON modules.id = enrolments.module_id
        JOIN students
            ON enrolments.student_id = students.id
        WHERE students.user_id = %s
        ORDER BY assignments.deadline ASC
    """, (session["user_id"],))

    assignment_records = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "assignments.html",
        assignment_records=assignment_records
    )


# --------------------------------------------------
# STUDENT GRADES
# --------------------------------------------------

@app.route("/grades")
def grades():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "student":
        return redirect(url_for("admin_dashboard"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            modules.module_name,
            modules.module_code,
            grades.assessment_name,
            grades.grade,
            grades.result
        FROM grades
        JOIN students
            ON grades.student_id = students.id
        JOIN modules
            ON grades.module_id = modules.id
        WHERE students.user_id = %s
        ORDER BY modules.module_name ASC
    """, (session["user_id"],))

    grade_records = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "grades.html",
        grade_records=grade_records
    )


# --------------------------------------------------
# STUDENT TIMETABLE
# --------------------------------------------------

@app.route("/timetable")
def timetable():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "student":
        return redirect(url_for("admin_dashboard"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            modules.module_name,
            modules.module_code,
            timetable.day_name,
            timetable.start_time,
            timetable.end_time,
            timetable.room,
            timetable.lecturer
        FROM timetable
        JOIN modules
            ON timetable.module_id = modules.id
        JOIN enrolments
            ON modules.id = enrolments.module_id
        JOIN students
            ON enrolments.student_id = students.id
        WHERE students.user_id = %s
        ORDER BY
            FIELD(
                timetable.day_name,
                'Monday',
                'Tuesday',
                'Wednesday',
                'Thursday',
                'Friday'
            ),
            timetable.start_time
    """, (session["user_id"],))

    timetable_records = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "timetable.html",
        timetable_records=timetable_records
    )


# --------------------------------------------------
# STUDENT MESSAGES
# --------------------------------------------------

@app.route("/messages")
def messages():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "student":
        return redirect(url_for("admin_dashboard"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            title,
            message,
            audience,
            announcement_date,
            status
        FROM announcements
        WHERE status = 'Active'
          AND audience IN ('Students', 'All Students')
        ORDER BY announcement_date DESC
    """)

    announcements = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "messages.html",
        announcements=announcements
    )


# --------------------------------------------------
# STUDENT PROFILE
# --------------------------------------------------

@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "student":
        return redirect(url_for("admin_dashboard"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            users.full_name,
            users.email,
            students.student_number,
            students.course,
            students.academic_year,
            students.study_mode
        FROM users
        JOIN students
            ON users.id = students.user_id
        WHERE users.id = %s
    """, (session["user_id"],))

    student = cursor.fetchone()

    cursor.execute("""
        SELECT
            COUNT(*) AS total_classes,
            SUM(
                CASE
                    WHEN attendance.status = 'Present' THEN 1
                    ELSE 0
                END
            ) AS classes_present
        FROM attendance
        JOIN students
            ON attendance.student_id = students.id
        WHERE students.user_id = %s
    """, (session["user_id"],))

    attendance_data = cursor.fetchone()
    total_classes = attendance_data["total_classes"] or 0
    classes_present = attendance_data["classes_present"] or 0

    if total_classes > 0:
        attendance_percentage = round(
            (classes_present / total_classes) * 100
        )
    else:
        attendance_percentage = 0

    cursor.execute("""
        SELECT AVG(grades.grade) AS average_grade
        FROM grades
        JOIN students
            ON grades.student_id = students.id
        WHERE students.user_id = %s
    """, (session["user_id"],))

    grade_data = cursor.fetchone()

    if grade_data["average_grade"] is not None:
        average_grade = round(float(grade_data["average_grade"]))
    else:
        average_grade = 0

    cursor.execute("""
        SELECT COUNT(*) AS current_modules
        FROM enrolments
        JOIN students
            ON enrolments.student_id = students.id
        WHERE students.user_id = %s
    """, (session["user_id"],))

    current_modules = cursor.fetchone()["current_modules"] or 0

    cursor.execute("""
        SELECT COUNT(*) AS assignments_due
        FROM assignments
        JOIN enrolments
            ON assignments.module_id = enrolments.module_id
        JOIN students
            ON enrolments.student_id = students.id
        WHERE students.user_id = %s
          AND assignments.deadline >= CURDATE()
          AND assignments.status != 'Completed'
    """, (session["user_id"],))

    assignments_due = cursor.fetchone()["assignments_due"] or 0

    cursor.close()
    connection.close()

    return render_template(
        "profile.html",
        student=student,
        attendance_percentage=attendance_percentage,
        average_grade=average_grade,
        current_modules=current_modules,
        assignments_due=assignments_due
    )


# --------------------------------------------------
# ADMIN DASHBOARD
# --------------------------------------------------

@app.route("/admin")
def admin_dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT COUNT(*) AS total_students
        FROM students
    """)
    total_students = cursor.fetchone()["total_students"]

    cursor.execute("""
        SELECT
            COUNT(*) AS total_records,
            SUM(
                CASE
                    WHEN status = 'Present' THEN 1
                    ELSE 0
                END
            ) AS present_records
        FROM attendance
    """)

    attendance_data = cursor.fetchone()
    total_records = attendance_data["total_records"] or 0
    present_records = attendance_data["present_records"] or 0

    if total_records > 0:
        average_attendance = round(
            (present_records / total_records) * 100
        )
    else:
        average_attendance = 0

    cursor.execute("""
        SELECT COUNT(*) AS total_assignments
        FROM assignments
    """)
    total_assignments = (
        cursor.fetchone()["total_assignments"] or 0
    )

    cursor.execute("""
        SELECT COUNT(*) AS total_announcements
        FROM announcements
    """)
    total_announcements = (
        cursor.fetchone()["total_announcements"] or 0
    )

    cursor.execute("""
        SELECT
            students.student_number,
            users.full_name,
            users.email,
            students.course
        FROM students
        JOIN users
            ON students.user_id = users.id
        ORDER BY students.id DESC
        LIMIT 5
    """)

    recent_students = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "admin_dashboard.html",
        total_students=total_students,
        average_attendance=average_attendance,
        total_assignments=total_assignments,
        total_announcements=total_announcements,
        recent_students=recent_students
    )


# --------------------------------------------------
# ADMIN STUDENTS
# --------------------------------------------------

@app.route("/admin/students")
def admin_students():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            students.id,
            students.student_number,
            users.full_name,
            users.email,
            students.course,
            students.academic_year,
            students.study_mode
        FROM students
        JOIN users
            ON students.user_id = users.id
        ORDER BY users.full_name ASC
    """)

    students = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "admin_students.html",
        students=students
    )


# --------------------------------------------------
# ADD STUDENT
# --------------------------------------------------

@app.route("/admin/students/add", methods=["POST"])
def add_student():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    full_name = request.form["full_name"]
    email = request.form["email"]
    student_number = request.form["student_number"]
    course = request.form["course"]
    academic_year = request.form["academic_year"]
    study_mode = request.form["study_mode"]

    temporary_password = secrets.token_urlsafe(12)
    hashed_password = generate_password_hash(temporary_password)

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO users
                (
                    full_name,
                    email,
                    password,
                    role,
                    must_change_password
                )
            VALUES
                (%s, %s, %s, 'student', 1)
        """, (
            full_name,
            email,
            hashed_password
        ))

        user_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO students
                (
                    user_id,
                    student_number,
                    course,
                    academic_year,
                    study_mode
                )
            VALUES
                (%s, %s, %s, %s, %s)
        """, (
            user_id,
            student_number,
            course,
            academic_year,
            study_mode
        ))

        connection.commit()

        flash(
            f"Student added successfully. "
            f"Temporary password: {temporary_password}"
        )

    except IntegrityError:
        connection.rollback()
        return "Email or Student ID already exists.", 400

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("admin_students"))


# --------------------------------------------------
# ADMIN ATTENDANCE
# --------------------------------------------------

@app.route("/admin/attendance")
def admin_attendance():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            students.student_number,
            users.full_name,
            modules.module_name,
            modules.module_code,
            attendance.attendance_date,
            attendance.status
        FROM attendance
        JOIN students
            ON attendance.student_id = students.id
        JOIN users
            ON students.user_id = users.id
        JOIN modules
            ON attendance.module_id = modules.id
        ORDER BY attendance.attendance_date DESC
    """)

    attendance_records = cursor.fetchall()

    cursor.execute("""
        SELECT
            students.id,
            students.student_number,
            users.full_name
        FROM students
        JOIN users
            ON students.user_id = users.id
        ORDER BY users.full_name ASC
    """)

    students = cursor.fetchall()

    cursor.execute("""
        SELECT id, module_name, module_code
        FROM modules
        ORDER BY module_name ASC
    """)

    modules = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "admin_attendance.html",
        attendance_records=attendance_records,
        students=students,
        modules=modules
    )


# --------------------------------------------------
# ADD ATTENDANCE
# --------------------------------------------------

@app.route("/admin/attendance/add", methods=["POST"])
def add_attendance():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    student_id = request.form["student_id"]
    module_id = request.form["module_id"]
    attendance_date = request.form["attendance_date"]
    status = request.form["status"]

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO attendance
                (
                    student_id,
                    module_id,
                    attendance_date,
                    status
                )
            VALUES (%s, %s, %s, %s)
        """, (
            student_id,
            module_id,
            attendance_date,
            status
        ))

        connection.commit()

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("admin_attendance"))


# --------------------------------------------------
# ADMIN GRADES
# --------------------------------------------------

@app.route("/admin/grades")
def admin_grades():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            students.student_number,
            users.full_name,
            modules.module_name,
            modules.module_code,
            grades.assessment_name,
            grades.grade,
            grades.result
        FROM grades
        JOIN students
            ON grades.student_id = students.id
        JOIN users
            ON students.user_id = users.id
        JOIN modules
            ON grades.module_id = modules.id
        ORDER BY users.full_name ASC
    """)

    grade_records = cursor.fetchall()

    cursor.execute("""
        SELECT
            students.id,
            students.student_number,
            users.full_name
        FROM students
        JOIN users
            ON students.user_id = users.id
        ORDER BY users.full_name ASC
    """)

    students = cursor.fetchall()

    cursor.execute("""
        SELECT id, module_name, module_code
        FROM modules
        ORDER BY module_name ASC
    """)

    modules = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "admin_grades.html",
        grade_records=grade_records,
        students=students,
        modules=modules
    )


# --------------------------------------------------
# ADD GRADE
# --------------------------------------------------

@app.route("/admin/grades/add", methods=["POST"])
def add_grade():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    student_id = request.form["student_id"]
    module_id = request.form["module_id"]
    assessment_name = request.form["assessment_name"]
    grade = request.form["grade"]
    result = request.form["result"]

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO grades
                (
                    student_id,
                    module_id,
                    assessment_name,
                    grade,
                    result
                )
            VALUES (%s, %s, %s, %s, %s)
        """, (
            student_id,
            module_id,
            assessment_name,
            grade,
            result
        ))

        connection.commit()

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("admin_grades"))


# --------------------------------------------------
# ADMIN ASSIGNMENTS
# --------------------------------------------------

@app.route("/admin/assignments")
def admin_assignments():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Get existing assignments
        cursor.execute("""
            SELECT
                assignments.id,
                modules.module_name,
                modules.module_code,
                assignments.title,
                assignments.description,
                assignments.deadline,
                assignments.status
            FROM assignments
            JOIN modules
                ON assignments.module_id = modules.id
            ORDER BY assignments.deadline ASC
        """)

        assignment_records = cursor.fetchall()

        # NEW: Get students enrolled in each
        # assignment's module
        cursor.execute("""
            SELECT DISTINCT
                assignments.id AS assignment_id,
                users.full_name,
                students.student_number
            FROM assignments
            JOIN enrolments
                ON assignments.module_id = enrolments.module_id
            JOIN students
                ON enrolments.student_id = students.id
            JOIN users
                ON students.user_id = users.id
            ORDER BY users.full_name ASC
        """)

        student_records = cursor.fetchall()

        # Group student names by assignment ID
        assignment_students = {}

        for record in student_records:
            assignment_id = record["assignment_id"]

            if assignment_id not in assignment_students:
                assignment_students[assignment_id] = []

            assignment_students[assignment_id].append(record)

        # Modules for Add Assignment form
        cursor.execute("""
            SELECT
                id,
                module_name,
                module_code
            FROM modules
            ORDER BY module_name ASC
        """)

        modules = cursor.fetchall()

    finally:
        cursor.close()
        connection.close()

    return render_template(
        "admin_assignments.html",
        assignment_records=assignment_records,
        modules=modules,
        assignment_students=assignment_students
    )


# --------------------------------------------------
# ADD ASSIGNMENT
# --------------------------------------------------

@app.route("/admin/assignments/add", methods=["POST"])
def add_assignment():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    module_id = request.form.get("module_id", "")
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    deadline = request.form.get("deadline", "")

    if not module_id.isdigit() or not title or not deadline:
        flash("Please complete the required assignment fields.")
        return redirect(url_for("admin_assignments"))

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO assignments
                (
                    module_id,
                    title,
                    description,
                    deadline,
                    status
                )
            VALUES
                (%s, %s, %s, %s, 'Not Started')
        """, (
            module_id,
            title,
            description,
            deadline
        ))

        connection.commit()
        flash("Assignment added successfully.")

    except mysql.connector.Error:
        connection.rollback()
        flash(
            "Could not add assignment. "
            "Check the details and try again."
        )

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("admin_assignments"))


# --------------------------------------------------
# ADMIN ANNOUNCEMENTS
# --------------------------------------------------

@app.route("/admin/announcements")
def admin_announcements():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            id,
            title,
            message,
            audience,
            announcement_date,
            status
        FROM announcements
        ORDER BY announcement_date DESC
    """)

    announcements = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "admin_announcements.html",
        announcements=announcements
    )


# --------------------------------------------------
# ADD ANNOUNCEMENT
# --------------------------------------------------

@app.route("/admin/announcements/add", methods=["POST"])
def add_announcement():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    title = request.form["title"]
    message = request.form["message"]
    audience = request.form["audience"]

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO announcements
                (
                    title,
                    message,
                    audience,
                    announcement_date,
                    status
                )
            VALUES
                (%s, %s, %s, CURDATE(), 'Active')
        """, (
            title,
            message,
            audience
        ))

        connection.commit()

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("admin_announcements"))


# --------------------------------------------------
# DELETE ANNOUNCEMENT
# --------------------------------------------------

@app.route(
    "/admin/announcements/delete/<int:announcement_id>",
    methods=["POST"]
)
def delete_announcement(announcement_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            DELETE FROM announcements
            WHERE id = %s
        """, (announcement_id,))

        connection.commit()

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("admin_announcements"))


# --------------------------------------------------
# LOGOUT
# --------------------------------------------------

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# --------------------------------------------------
# RUN APPLICATION
# --------------------------------------------------

if __name__ == "__main__":
    app.run(debug=False)