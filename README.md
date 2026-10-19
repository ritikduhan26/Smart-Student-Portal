# Smart Student Portal for Managing Academic Activities and Communication

A web-based student portal that brings students' attendance, assignments, grades, timetable and announcements into one place, with a separate area for administrators to manage academic records.

**Project:** MSc Computer Science project, The University of Law  
**Candidate number:** 0412963  
**Supervisor:** Callum Altham  

---

## Features

### Student Area
- Dashboard showing attendance percentage, number of upcoming assignments and average grade.
- Pages for attendance, assignments, grades, timetable, announcements/messages and profile.
- Students can view their own academic records.
- Assignments and timetable entries are based on the modules a student is enrolled on.

### Administrator Area
- Create student accounts with a temporary password displayed once.
- Record attendance and grades.
- Add assignments and view students enrolled on the relevant module.
- Post and delete announcements.

### Security
- Passwords are stored as hashes using Werkzeug, not as plain text.
- Login sessions expire after 30 minutes.
- Protected routes check the user's role (student or administrator).
- New student accounts must change their temporary password before using the portal; the new password must be at least 12 characters.
- The change-password form includes a CSRF token.
- Database credentials and the Flask secret key are configured through a local `.env` file.
- SQL queries use parameterised values rather than building queries from user input.

> **Known security limitations:** This is a local prototype. It does not use HTTPS, does not limit failed login attempts, and CSRF protection is currently applied only to the change-password form. The application also connects to MySQL as `root`; a real deployment should use a dedicated database user with limited permissions.

---

## Technologies

| Area | Technology |
| :--- | :--- |
| **Backend** | Python, Flask |
| **Database** | MySQL via `mysql-connector-python` |
| **Frontend** | HTML (Jinja templates), CSS, JavaScript |
| **Icons** | Font Awesome via CDN (internet access is required for icons) |
| **Wireframes** | Figma |

---

## Project Structure

```text
student dashboard/
├── app.py
├── requirements.txt
├── README.md
├── student_portal.sql
├── .env.example
├── static/
│   ├── style.css
│   └── script.js
└── templates/
    ├── base.html
    ├── admin_base.html
    ├── login.html
    ├── change_password.html
    ├── dashboard.html
    ├── attendance.html
    ├── assignments.html
    ├── grades.html
    ├── timetable.html
    ├── messages.html
    ├── profile.html
    ├── admin_dashboard.html
    ├── admin_students.html
    ├── admin_attendance.html
    ├── admin_grades.html
    ├── admin_assignments.html
    └── admin_announcements.html
```

---

## Database Design

The database is named `student_portal` and contains nine linked tables:

| Table | Purpose |
| :--- | :--- |
| `users` | Login details, names and role (`student` or `admin`) |
| `students` | Student number, course, academic year and study mode; linked to `users` |
| `modules` | Module names and codes |
| `enrolments` | Links students to the modules they study |
| `attendance` | Attendance records, including student, module, date and status |
| `assignments` | Assignment details and deadlines, linked to a module |
| `grades` | Assessment names, grades and results for a student and module |
| `timetable` | Class day, start/end times, room and lecturer, linked to a module |
| `announcements` | Messages posted by administrators |

The `enrolments` table connects students to modules. Assignments and timetable entries can be associated with a student's modules through the relationship:

`logged-in user → student record → enrolments → modules → assignments/timetable`

---

## Setup

### Requirements
- Python 3.8 or newer.
- MySQL Server running locally.
- MySQL Workbench is recommended for managing and importing the database.

### 1. Install Python packages

Open a terminal in the project directory and run:

```bash
pip install -r requirements.txt
```

The project dependencies include Flask, `mysql-connector-python`, `python-dotenv` and Werkzeug. Check `requirements.txt` for the exact versions used.

### 2. Create and import the database

The included `student_portal.sql` export contains table definitions and sample records. It is intended for the `student_portal` database. It does not create the database schema itself.

1. Open MySQL Workbench and connect to your local MySQL Server.
2. Create the database:
   ```sql
   CREATE DATABASE student_portal;
   ```
3. Select the `student_portal` schema.
4. Open and execute `student_portal.sql` using MySQL Workbench, or use the Workbench data-import tools.
5. Refresh the schema and confirm that all nine tables exist.

> **Important:** The SQL file contains `DROP TABLE IF EXISTS` statements and inserts sample data. Import it only into a new or disposable test database, not a database containing records you need to keep. The dump includes example user accounts and password hashes; verify the accounts and use fictional data only.

### 3. Configure environment variables

Set the values for your local environment. For example:

```dotenv
MYSQL_PASSWORD=your_mysql_password
SECRET_KEY=replace_with_a_long_random_secret
```
The app connects to MySQL on localhost as root, using the student_portal database. These values are set in app.py.

A secret key can be generated with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 4. Check the administrator account

The supplied SQL already includes an example administrator row with the email `admin@portal.com`. Do not insert another row with that same email, because the `users.email` column is unique.

Before using the example account, verify that you know its corresponding password and that the account is suitable for your local test environment. The SQL dump contains a password hash, not the original password, so the password cannot be read from the dump. If you do not know the password, use the application's supported account setup process or create a new administrator with a unique email and a password hash generated using Werkzeug.

For example, to generate a hash locally:

```bash
python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('choose-a-strong-password'))"
```

Never store a plain-text password in the database. If you create a new administrator by SQL, use the correct columns and a unique email address.

### 5. Run the application

From the project directory, run:

```bash
python app.py
```

Then open this address in your browser:

```text
http://127.0.0.1:5000
```

Log in using a valid account configured in your local database.

---

## How to Use the Portal

1. Log in as an administrator.
2. Add a student and securely note the temporary password displayed by the application.
3. Add attendance, grades and assignments, and post an announcement.
4. Log out and log in using the new student's account.
5. Follow the prompt to set a new password of at least 12 characters.
6. Check that the student dashboard and pages show the appropriate student's records.

---

## Testing

The project report records 18 manual functional tests, all of which passed. The tests covered student and administrator login, incorrect passwords, dashboard values, access to a student's own records, enrolment-based assignments and timetable, student creation, attendance, grades, assignments, announcements, access control, logout, duplicate students, protected pages without login, session expiry and forced password change.

Testing was carried out by me on a local machine using fictional data. This does not replace independent testing or formal usability, accessibility, performance or security testing.

---

## Known Limitations

- Testing was performed by one person using fictional data; no formal usability, accessibility or load testing was conducted.
- The application runs locally and does not configure HTTPS.
- Failed login attempts are not rate-limited.
- CSRF protection is present on the change-password form but not on administrator forms.
- Administrators cannot edit or delete most existing records; announcements can be deleted.
- Students cannot submit assignments or message staff.
- The application connects to MySQL as `root`; a production deployment should use a dedicated database account with limited permissions.

---

## Future Work

Potential improvements include assignment submission, messaging and email reminders, administrator edit/delete functionality, usability testing with real students, automated tests and stronger security controls.

---

## Academic Project Note

This application is a prototype developed for an MSc Computer Science project. It is not intended for use with real student records or as a production university system without further development, testing and security review.
