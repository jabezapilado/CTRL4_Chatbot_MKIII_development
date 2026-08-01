from __future__ import annotations

import json
from datetime import date, datetime, time, timedelta
from typing import Any

from typing import Final

import mysql.connector
from werkzeug.security import generate_password_hash

from .config import Config


config = Config()

ALLOWED_ACCOUNT_ROLES: Final[frozenset[str]] = frozenset({
    "student",
    "staff",
    "admin",
})

ALLOWED_ACCOUNT_STATUSES: Final[frozenset[str]] = frozenset({
    "active",
    "disabled",
})

ALLOWED_GENDERS: Final[frozenset[str]] = frozenset({
    "Male",
    "Female",
    "Prefer not to say",
    "Other",
})

ALLOWED_ACCOUNT_UPDATE_FIELDS: Final[frozenset[str]] = frozenset({
    "full_name",
    "email",
    "gender",
    "program",
    "assigned_programs",
    "office",
    "support_statement",
    "consultation_rooms",
    "consultation_schedules",
    "status",
})
ACCOUNT_JSON_FIELDS: Final[frozenset[str]] = frozenset({
    "assigned_programs",
    "consultation_rooms",
    "consultation_schedules",
})


def _connection_kwargs(database: str | None = None) -> dict[str, Any]:
    kwargs: dict[str, Any] = {
        "host": config.DB_HOST,
        "port": config.DB_PORT,
        "user": config.DB_USER,
        "password": config.DB_PASSWORD,
        "autocommit": False,
    }
    if database:
        kwargs["database"] = database

    ssl_options: dict[str, Any] = {}
    if config.DB_SSL_CA:
        ssl_options["ca"] = config.DB_SSL_CA
        ssl_options["verify_cert"] = config.DB_SSL_VERIFY_CERT
    if ssl_options:
        kwargs["ssl_ca"] = ssl_options.get("ca")
        kwargs["ssl_verify_cert"] = ssl_options.get("verify_cert", False)

    return kwargs


def _server_connection():
    return mysql.connector.connect(**_connection_kwargs())


def _database_connection():
    return mysql.connector.connect(**_connection_kwargs(config.DB_NAME))

def current_time() -> datetime:
    return datetime.now().replace(microsecond=0)


def _json_safe_value(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, time):
        return value.isoformat()
    if isinstance(value, timedelta):
        total_seconds = int(value.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return value


def _json_safe_row(row: dict[str, Any]) -> dict[str, Any]:
    return {key: _json_safe_value(value) for key, value in row.items()}


def _json_column_value(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return json.dumps(value)
    return value


def _seed_accounts() -> list[tuple[Any, ...]]:
    accounts = [
        {
            "email": config.SEED_STUDENT_EMAIL,
            "full_name": config.SEED_STUDENT_NAME,
            "student_number": config.SEED_STUDENT_NUMBER,
            "staff_number": None,
            "password": config.SEED_STUDENT_PASSWORD,
            "role": "student",
            "program": config.SEED_STUDENT_PROGRAM,
            "gender": config.SEED_STUDENT_GENDER,
        },
        {
            "email": config.SEED_STUDENT2_EMAIL,
            "full_name": config.SEED_STUDENT2_NAME,
            "student_number": config.SEED_STUDENT2_NUMBER,
            "staff_number": None,
            "password": config.SEED_STUDENT2_PASSWORD,
            "role": "student",
            "program": config.SEED_STUDENT2_PROGRAM,
            "gender": config.SEED_STUDENT2_GENDER,
        },
        {
            "email": config.SEED_STAFF_EMAIL,
            "full_name": config.SEED_STAFF_NAME,
            "student_number": None,
            "staff_number": config.SEED_STAFF_NUMBER,
            "password": config.SEED_STAFF_PASSWORD,
            "role": "staff",
            "program": None,  
            "gender": config.SEED_STAFF_GENDER,
        },
        {
            "email": config.SEED_STAFF2_EMAIL,
            "full_name": config.SEED_STAFF2_NAME,
            "student_number": None,
            "staff_number": config.SEED_STAFF2_NUMBER,
            "password": config.SEED_STAFF2_PASSWORD,
            "role": "staff",
            "program": None,
            "gender": config.SEED_STAFF2_GENDER,
        },
        {
            "email": config.SEED_ADMIN_EMAIL,
            "full_name": config.SEED_ADMIN_NAME,
            "student_number": None,
            "staff_number": None,
            "password": config.SEED_ADMIN_PASSWORD,
            "role": "admin",
            "program": None,
            "gender": config.SEED_ADMIN_GENDER,
        },
    ]

    # Seed row order matches the accounts table schema.
    rows: list[tuple[Any, ...]] = []
    for account in accounts:
        email = str(account["email"]).strip().lower()
        password = str(account["password"])
        full_name = str(account["full_name"]).strip()
        student_number = account.get("student_number")
        staff_number = account.get("staff_number")
        gender = account.get("gender")
        program = account.get("program", None)
        # All counselor fields initialized to None
        assigned_programs = None
        office = None
        support_statement = None
        consultation_rooms = None
        consultation_schedules = None
        role = str(account["role"]).strip().lower()

        if not email or not password or not full_name:
            continue

        rows.append(
            (
                email,
                generate_password_hash(password),
                full_name,
                student_number,
                staff_number,
                gender,
                program,
                assigned_programs,
                office,
                support_statement,
                consultation_rooms,
                consultation_schedules,
                role,
                "active",
                current_time(),
            )
        )

    return rows

def seed_database() -> None:
    initialize_database()

    seed_rows = _seed_accounts()

    if not seed_rows:
        return

    with _database_connection() as connection:
        with connection.cursor() as cursor:
            cursor.executemany(
                """
                INSERT IGNORE INTO accounts (
                    email,
                    password_hash,
                    full_name,
                    student_number,
                    staff_number,
                    gender,
                    program,
                    assigned_programs,
                    office,
                    support_statement,
                    consultation_rooms,
                    consultation_schedules,
                    role,
                    status,
                    created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                seed_rows,
            )
            cursor.execute(
                """
                INSERT INTO settings (setting_key, setting_value, updated_at)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    setting_value = VALUES(setting_value),
                    updated_at = VALUES(updated_at)
                """,
                (
                    "currentAdmissionYear",
                    "2024",
                    current_time(),
                ),
            )
        connection.commit()


# --- Automatic account number generation ---
def generate_next_student_number() -> str:
    initialize_database()

    admission_year = str(load_settings().get("currentAdmissionYear", "2024"))

    with _database_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT student_number
                FROM accounts
                WHERE student_number LIKE %s
                ORDER BY student_number DESC
                LIMIT 1
                """,
                (f"{admission_year}-%",),
            )
            row = cursor.fetchone()

    if not row or not row[0]:
        return f"{admission_year}-00001"

    last = int(str(row[0]).split("-")[1]) + 1
    return f"{admission_year}-{last:05d}"


def generate_next_staff_number() -> str:
    initialize_database()

    with _database_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT staff_number
                FROM accounts
                WHERE staff_number IS NOT NULL
                ORDER BY staff_number DESC
                LIMIT 1
                """
            )
            row = cursor.fetchone()

    if not row or not row[0]:
        return "STF-0001"

    last = int(str(row[0]).replace("STF-", "")) + 1
    return f"STF-{last:04d}"


def initialize_database() -> None:
    with _server_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{config.DB_NAME}` CHARACTER SET {config.DB_CHARSET} COLLATE {config.DB_CHARSET}_unicode_ci"
            )
        connection.commit()

    with _database_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS accounts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    full_name VARCHAR(255) NOT NULL,
                    student_number VARCHAR(20) NULL UNIQUE,
                    staff_number VARCHAR(20) NULL UNIQUE,
                    gender ENUM(
                        'Male',
                        'Female',
                        'Prefer not to say',
                        'Other'
                    ) NULL,
                    program VARCHAR(100) NULL,
                    assigned_programs JSON NULL,
                    office VARCHAR(255) NULL,
                    support_statement TEXT NULL,
                    consultation_rooms JSON NULL,
                    consultation_schedules JSON NULL,
                    role ENUM(
                        'student',
                        'staff',
                        'admin'
                    ) NOT NULL DEFAULT 'student',
                    status ENUM(
                        'active',
                        'disabled'
                    ) NOT NULL DEFAULT 'active',
                    created_at DATETIME NOT NULL
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS inquiries (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    account_id INT NULL,
                    inquiry_type VARCHAR(100) NOT NULL,
                    emotion_result VARCHAR(100) NOT NULL,
                    escalated TINYINT(1) NOT NULL DEFAULT 0,
                    appointment_recommended TINYINT(1) NOT NULL DEFAULT 0,
                    created_at DATETIME NOT NULL,
                    FOREIGN KEY (account_id)
                    REFERENCES accounts(id)
                    ON DELETE SET NULL
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS conversation_summaries (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    account_id INT NULL,
                    primary_concern VARCHAR(255) NOT NULL,
                    conversation_type VARCHAR(100) NOT NULL,
                    emotion_results VARCHAR(255) NOT NULL,
                    flagged_status TINYINT(1) NOT NULL DEFAULT 0,
                    appointment_recommendation VARCHAR(255) NOT NULL,
                    recommendations TEXT NULL,
                    suggested_intervention TEXT NULL,
                    language_used VARCHAR(50) NOT NULL,
                    total_messages INT NOT NULL,
                    summary TEXT NOT NULL,
                    created_at DATETIME NOT NULL,
                    FOREIGN KEY (account_id)
                    REFERENCES accounts(id)
                    ON DELETE SET NULL
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS escalations (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    account_id INT NULL,
                    summary_id INT NULL,
                    status VARCHAR(50) NOT NULL DEFAULT 'pending',
                    intervention_notes TEXT NULL,
                    created_at DATETIME NOT NULL,
                    resolved_at DATETIME NULL,
                    FOREIGN KEY (account_id)
                    REFERENCES accounts(id)
                    ON DELETE SET NULL,
                    FOREIGN KEY (summary_id)
                    REFERENCES conversation_summaries(id)
                    ON DELETE SET NULL
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS appointments (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    account_id INT NOT NULL,
                    contact_number VARCHAR(20) NOT NULL,
                    appointment_category VARCHAR(100) NOT NULL,
                    appointment_mode VARCHAR(50) NOT NULL,
                    preferred_date DATE NOT NULL,
                    preferred_time_slot VARCHAR(20) NOT NULL,
                    reason TEXT NOT NULL,
                    status ENUM(
                        'pending',
                        'approved',
                        'done',
                        'did_not_attend',
                        'cancelled'
                    ) NOT NULL DEFAULT 'pending',
                    counselor_notes TEXT NULL,
                    appointment_source ENUM(
                        'chatbot',
                        'walk_in',
                        'hotline',
                        'messenger',
                        'email',
                        'staff_manual'
                    ) NOT NULL,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL,
                    FOREIGN KEY (account_id)
                    REFERENCES accounts(id)
                    ON DELETE RESTRICT
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS settings (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    setting_key VARCHAR(100) NOT NULL UNIQUE,
                    setting_value TEXT NOT NULL,
                    updated_at DATETIME NOT NULL
                )
                """
            )
        connection.commit()


def save_inquiry(payload: dict[str, Any]) -> int:
    initialize_database()
    with _database_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO inquiries (
                    account_id,
                    inquiry_type,
                    emotion_result,
                    escalated,
                    appointment_recommended,
                    created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    payload.get("account_id"),
                    payload["inquiry_type"],
                    payload["emotion_result"],
                    1 if payload.get("escalated") else 0,
                    1 if payload.get("appointment_recommended") else 0,
                    payload.get("created_at", current_time()),
                ),
            )
            inquiry_id = cursor.lastrowid
        connection.commit()
        return int(inquiry_id)

def save_escalation(payload: dict[str, Any]) -> int:
    initialize_database()
    with _database_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO escalations (
                    account_id,
                    summary_id,
                    status,
                    intervention_notes,
                    created_at,
                    resolved_at
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    payload.get("account_id"),
                    payload.get("summary_id"),
                    payload.get("status", "pending"),
                    payload.get("intervention_notes"),
                    payload.get("created_at", current_time()),
                    payload.get("resolved_at"),
                ),
            )
            escalation_id = cursor.lastrowid
        connection.commit()
        return int(escalation_id)


def save_appointment(payload: dict[str, Any]) -> int:
    initialize_database()
    with _database_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO appointments (
                    account_id,
                    contact_number,
                    appointment_category,
                    appointment_mode,
                    preferred_date,
                    preferred_time_slot,
                    reason,
                    status,
                    counselor_notes,
                    appointment_source,
                    created_at,
                    updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    payload["account_id"],
                    payload["contact_number"],
                    payload["appointment_category"],
                    payload["appointment_mode"],
                    payload["preferred_date"],
                    payload["preferred_time_slot"],
                    payload["reason"],
                    payload.get("status", "pending"),
                    payload.get("counselor_notes"),
                    payload["appointment_source"],
                    payload.get("created_at", current_time()),
                    payload.get("updated_at", current_time()),
                ),
            )
            appointment_id = cursor.lastrowid
        connection.commit()
        return int(appointment_id)

def has_appointment_conflict(
    preferred_date: str,
    preferred_time_slot: str,
) -> bool:
    initialize_database()

    with _database_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id
                FROM appointments
                WHERE preferred_date = %s
                AND preferred_time_slot = %s
                AND status IN ('pending', 'approved')
                LIMIT 1
                """,
                (
                    preferred_date,
                    preferred_time_slot,
                ),
            )

            row = cursor.fetchone()

    return row is not None

def save_conversation_summary(payload: dict[str, Any]) -> int:
    initialize_database()

    with _database_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO conversation_summaries (
                    account_id,
                    primary_concern,
                    conversation_type,
                    emotion_results,
                    flagged_status,
                    appointment_recommendation,
                    recommendations,
                    suggested_intervention,
                    language_used,
                    total_messages,
                    summary,
                    created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    payload.get("account_id"),
                    payload["primary_concern"],
                    payload["conversation_type"],
                    payload["emotion_results"],
                    1 if payload.get("flagged_status") else 0,
                    payload["appointment_recommendation"],
                    payload.get("recommendations"),
                    payload.get("suggested_intervention"),
                    payload["language_used"],
                    payload["total_messages"],
                    payload["summary"],
                    payload.get("created_at", current_time()),
                ),
            )

            summary_id = cursor.lastrowid

        connection.commit()

    return int(summary_id)

def list_conversation_summaries() -> list[dict[str, Any]]:
    initialize_database()

    return fetch_rows(
        """
        SELECT *
        FROM conversation_summaries
        ORDER BY created_at DESC
        """
    )

def fetch_account_by_email(email: str) -> dict[str, Any] | None:
    initialize_database()
    with _database_connection() as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(
                """
                SELECT id,
                student_number,
                staff_number,
                gender,
                program,
                assigned_programs,
                office,
                support_statement,
                consultation_rooms,
                consultation_schedules,
                email,
                password_hash,
                full_name,
                role,
                status,
                created_at
                FROM accounts WHERE email = %s LIMIT 1
                """,
                (email,),
            )
            row = cursor.fetchone()
    return row

def fetch_account_by_student_number(student_number: str) -> dict[str, Any] | None:
    initialize_database()

    with _database_connection() as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(
                """
                SELECT id,
                student_number,
                staff_number,
                gender,
                program,
                assigned_programs,
                office,
                support_statement,
                consultation_rooms,
                consultation_schedules,
                email,
                full_name,
                role,
                status,
                created_at
                FROM accounts
                WHERE student_number = %s
                LIMIT 1
                """,
                (student_number,),
            )
            row = cursor.fetchone()

    return row

def fetch_account_by_staff_number(staff_number: str) -> dict[str, Any] | None:
    initialize_database()

    with _database_connection() as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(
                """
                SELECT id,
                student_number,
                staff_number,
                gender,
                program,
                assigned_programs,
                office,
                support_statement,
                consultation_rooms,
                consultation_schedules,
                email,
                full_name,
                role,
                status,
                created_at
                FROM accounts
                WHERE staff_number = %s
                LIMIT 1
                """,
                (staff_number,),
            )
            row = cursor.fetchone()

    return row

def fetch_account_by_id(
    account_id: int,
    *,
    role: str | None = None,
) -> dict[str, Any] | None:
    initialize_database()

    role_filter = ""
    params: list[Any] = [account_id]

    if role:
        role = role.strip().lower()
        if role not in ALLOWED_ACCOUNT_ROLES:
            raise ValueError("Invalid account role.")
        role_filter = " AND role = %s"
        params.append(role)

    with _database_connection() as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(
                f"""
                SELECT id,
                student_number,
                staff_number,
                gender,
                program,
                assigned_programs,
                office,
                support_statement,
                consultation_rooms,
                consultation_schedules,
                email,
                full_name,
                role,
                status,
                created_at
                FROM accounts
                WHERE id = %s{role_filter}
                LIMIT 1
                """,
                tuple(params),
            )
            row = cursor.fetchone()

    return row


def list_accounts(
    *,
    role: str | None = None,
    status: str | None = None,
    query: str | None = None,
) -> list[dict[str, Any]]:
    initialize_database()

    filters: list[str] = []
    params: list[Any] = []

    if role:
        role = role.strip().lower()
        if role not in ALLOWED_ACCOUNT_ROLES:
            raise ValueError("Invalid account role.")
        filters.append("role = %s")
        params.append(role)

    if status:
        status = status.strip().lower()
        if status not in ALLOWED_ACCOUNT_STATUSES:
            raise ValueError("Invalid account status.")
        filters.append("status = %s")
        params.append(status)

    if query:
        search_value = f"%{query.strip()}%"
        filters.append(
            """
            (
                (
                    role = 'student'
                    AND (
                        full_name LIKE %s
                        OR email LIKE %s
                        OR student_number LIKE %s
                    )
                )
                OR (
                    role = 'staff'
                    AND (
                        full_name LIKE %s
                        OR email LIKE %s
                        OR staff_number LIKE %s
                    )
                )
            )
            """
        )
        params.extend([
            search_value,
            search_value,
            search_value,
            search_value,
            search_value,
            search_value,
        ])

    where_clause = ""
    if filters:
        where_clause = "WHERE " + " AND ".join(filters)

    with _database_connection() as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(
                f"""
                SELECT id,
                student_number,
                staff_number,
                gender,
                program,
                assigned_programs,
                office,
                support_statement,
                consultation_rooms,
                consultation_schedules,
                email,
                full_name,
                role,
                status,
                created_at
                FROM accounts
                {where_clause}
                ORDER BY id ASC
                """,
                tuple(params),
            )
            rows = cursor.fetchall()
    return rows


def update_account_fields(
    account_id: int,
    updates: dict[str, Any],
    *,
    role: str | None = None,
) -> dict[str, Any] | None:
    initialize_database()

    if not updates:
        raise ValueError("No account fields to update.")

    invalid_fields = set(updates) - ALLOWED_ACCOUNT_UPDATE_FIELDS
    if invalid_fields:
        raise ValueError("Invalid account update field.")

    role_filter = ""
    params = [
        _json_column_value(value) if field in ACCOUNT_JSON_FIELDS else value
        for field, value in updates.items()
    ]
    params.append(account_id)

    if role:
        role = role.strip().lower()
        if role not in ALLOWED_ACCOUNT_ROLES:
            raise ValueError("Invalid account role.")
        role_filter = " AND role = %s"
        params.append(role)

    assignments = ", ".join(f"{field} = %s" for field in updates)

    with _database_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                UPDATE accounts
                SET {assignments}
                WHERE id = %s{role_filter}
                """,
                tuple(params),
            )

        connection.commit()

    return fetch_account_by_id(account_id, role=role)


def search_student_accounts(query: str) -> list[dict[str, Any]]:
    initialize_database()

    search = f"%{query.strip()}%"

    with _database_connection() as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    full_name,
                    student_number,
                    program,
                    email
                FROM accounts
                WHERE role = 'student'
                  AND status = 'active'
                  AND (
                        full_name LIKE %s
                     OR student_number LIKE %s
                  )
                ORDER BY full_name ASC
                LIMIT 10
                """,
                (search, search),
            )

            rows = cursor.fetchall()

    return [_json_safe_row(row) for row in rows]


# --- Helper: Get staff assigned to a program ---

def get_staff_by_program(program: str) -> dict[str, Any] | None:
    initialize_database()

    with _database_connection() as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(
                """
                SELECT id,
                       staff_number,
                       full_name,
                       email,
                       assigned_programs,
                       office,
                       support_statement,
                       consultation_rooms,
                       consultation_schedules,
                       status
                FROM accounts
                WHERE role = 'staff'
                  AND status = 'active'
                ORDER BY id ASC
                """
            )
            staff_rows = cursor.fetchall()

    for staff in staff_rows:
        assigned = staff.get("assigned_programs")

        if not assigned:
            continue

        if isinstance(assigned, bytes):
            assigned = assigned.decode("utf-8")

        if isinstance(assigned, str):
            try:
                assigned = json.loads(assigned)
            except json.JSONDecodeError:
                continue

        if (
            isinstance(assigned, list)
            and program.strip().lower()
            in {str(p).strip().lower() for p in assigned}
        ):
            return staff

    return None

def get_student_by_id(
    student_id: int,
) -> dict[str, Any] | None:
    rows = fetch_rows(
        """
        SELECT
            id,
            program
        FROM accounts
        WHERE id = %s
          AND role = 'student'
          AND status = 'active'
        LIMIT 1
        """,
        (student_id,),
    )

    return rows[0] if rows else None

# --- Helper: List staff appointments by assigned programs ---
def list_staff_appointments(staff_id: int) -> list[dict[str, Any]]:
    initialize_database()

    with _database_connection() as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(
                """
                SELECT assigned_programs
                FROM accounts
                WHERE id = %s
                  AND role = 'staff'
                  AND status = 'active'
                LIMIT 1
                """,
                (staff_id,),
            )
            staff = cursor.fetchone()

    if not staff:
        return []

    assigned_programs = staff.get("assigned_programs")

    if not assigned_programs:
        return []

    if isinstance(assigned_programs, str):
        try:
            assigned_programs = json.loads(assigned_programs)
        except json.JSONDecodeError:
            return []

    if not isinstance(assigned_programs, list):
        return []

    placeholders = ", ".join(["%s"] * len(assigned_programs))

    return fetch_rows(
        f"""
        SELECT
            appointments.*,
            accounts.full_name,
            accounts.email,
            accounts.student_number,
            accounts.program
        FROM appointments
        INNER JOIN accounts
            ON appointments.account_id = accounts.id
        WHERE accounts.program IN ({placeholders})
        ORDER BY appointments.preferred_date DESC,
                 appointments.preferred_time_slot DESC,
                 appointments.created_at DESC
        """,
        tuple(assigned_programs),
    )

def list_student_appointments(
    student_id: int,
) -> list[dict[str, Any]]:
    return fetch_rows(
        """
        SELECT
            *
        FROM appointments
        WHERE account_id = %s
        ORDER BY id DESC
        """,
        (student_id,),
    )

def get_dashboard_stats() -> dict[str, Any]:
    initialize_database()

    with _database_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM appointments
                WHERE preferred_date = CURDATE()
                """
            )
            appointments_today = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM appointments
                WHERE status = 'pending'
                """
            )
            pending_appointments = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM appointments
                WHERE status = 'done'
                  AND preferred_date = CURDATE()
                """
            )
            completed_today = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM escalations
                WHERE status = 'pending'
                """
            )
            active_escalations = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM conversation_summaries
                """
            )
            conversation_summaries = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM accounts
                WHERE role = 'student'
                """
            )
            total_students = cursor.fetchone()[0]

    return {
        "appointments_today": appointments_today,
        "pending_appointments": pending_appointments,
        "completed_today": completed_today,
        "active_escalations": active_escalations,
        "conversation_summaries": conversation_summaries,
        "total_students": total_students,
    }

def create_account(
    *,
    full_name: str,
    email: str,
    
    # password_hash must already be generated using
    # werkzeug.security.generate_password_hash().
    # Plaintext passwords must never be passed here.
    password_hash: str, 
    
    role: str,
    student_number: str | None = None,
    staff_number: str | None = None,
    gender: str | None = None,
    program: str | None = None,
    assigned_programs: Any | None = None,
    office: str | None = None,
    support_statement: str | None = None,
    consultation_rooms: Any | None = None,
    consultation_schedules: Any | None = None,
) -> dict[str, Any]:
    initialize_database()
    
    email = email.strip().lower()
    full_name = full_name.strip()
    role = role.strip().lower()
    gender = gender.strip() if gender else None
    program = program.strip() if program else None
    office = office.strip() if office else None
    support_statement = support_statement.strip() if support_statement else None

    # Automatic account number generation
    if role == "student":
        student_number = generate_next_student_number()
        staff_number = None
    elif role == "staff":
        staff_number = generate_next_staff_number()
        student_number = None
    else:
        student_number = None
        staff_number = None

    if role != "staff":
        assigned_programs = None
        office = None
        support_statement = None
        consultation_rooms = None
        consultation_schedules = None

    if role == "admin":
        program = None

    if role not in ALLOWED_ACCOUNT_ROLES:
        raise ValueError("Invalid account role.")
    
    # No longer require manual entry of student_number or staff_number.
    if role == "student" and not program:
        raise ValueError("Program is required for students.")

    if role == "student" and program not in config.PROGRAMS:
        raise ValueError("Invalid program.")
    
    # No longer require manual staff_number.
    if fetch_account_by_email(email):
        raise ValueError("An account with this email already exists.")
    
    if (
        student_number
        and fetch_account_by_student_number(student_number)
    ):
        raise ValueError("Student number already exists.")
    
    if (
        staff_number
        and fetch_account_by_staff_number(staff_number)
    ):
        raise ValueError("Staff number already exists.")

    if gender and gender not in ALLOWED_GENDERS:
        raise ValueError("Invalid gender.")

    with _database_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO accounts (
                    full_name,
                    student_number,
                    staff_number,
                    gender,
                    program,
                    assigned_programs,
                    office,
                    support_statement,
                    consultation_rooms,
                    consultation_schedules,
                    email,
                    password_hash,
                    role,
                    status,
                    created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'active', %s)
                """,
                (
                    full_name,
                    student_number,
                    staff_number,
                    gender,
                    program,
                    _json_column_value(assigned_programs),
                    office,
                    support_statement,
                    _json_column_value(consultation_rooms),
                    _json_column_value(consultation_schedules),
                    email,
                    password_hash,
                    role,
                    current_time(),
                ),
            )

            account_id = cursor.lastrowid

        connection.commit()

    return {
        "id": account_id,
        "student_number": student_number,
        "staff_number": staff_number,
    }

def load_settings() -> dict[str, Any]:
    initialize_database()
    with _database_connection() as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT setting_key, setting_value FROM settings")
            rows = cursor.fetchall()

    settings = {
        "officeHours": "Monday to Friday, 8:00 AM - 5:00 PM",
        "officeEmail": "guidance@hau.edu.ph",
        "contactNumber": "(045) 123-4567",
        "officeLocation": "SOC Guidance Office, Holy Angel University",
        "autoFlag": True,
        "showSupport": False,
        "escalationMessage": "Your concern may need further attention from Guidance Office personnel. Please wait for proper assistance or contact the office directly if urgent.",
        "categories": [
            "Guidance Appointment",
            "Counseling Services",
            "Office Schedule",
            "Requirements and Procedures",
            "Emotional Support Concerns",
            "General Inquiry",
            "Unknown Inquiry",
        ],
        "faqs": [
            {
                "title": "Office Hours",
                "question": "What are your office hours?",
                "answer": "The SOC Guidance Office is open from Monday to Friday, 8:00 AM to 5:00 PM.",
            },
            {
                "title": "Book Appointment",
                "question": "How can I book an appointment?",
                "answer": "You may book an appointment by selecting the Book Appointment option and submitting your preferred date and reason for appointment.",
            },
            {
                "title": "Counseling Services",
                "question": "Can I speak with a counselor?",
                "answer": "Yes, you may request counseling assistance through the chatbot or visit the SOC Guidance Office during office hours.",
            },
        ],
    }

    for row in rows:
        key = row["setting_key"]
        value = row["setting_value"]
        if key in {"autoFlag", "showSupport"}:
            settings[key] = str(value).lower() in {"1", "true", "yes", "on"}
        elif key in {"categories", "faqs"}:
            try:
                settings[key] = json.loads(value)
            except json.JSONDecodeError:
                pass
        else:
            settings[key] = value

    return settings


def save_settings(settings: dict[str, Any]) -> None:
    initialize_database()
    with _database_connection() as connection:
        with connection.cursor() as cursor:
            for key, value in settings.items():
                cursor.execute(
                    """
                    INSERT INTO settings (setting_key, setting_value, updated_at)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE setting_value = VALUES(setting_value), updated_at = VALUES(updated_at)
                    """,
                    (key, json.dumps(value) if isinstance(value, (dict, list)) else str(value), current_time()),
                )
        connection.commit()


def fetch_rows(query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    initialize_database()
    with _database_connection() as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
    return [_json_safe_row(row) for row in rows]

def get_appointment_by_id(
    appointment_id: int,
) -> dict[str, Any] | None:
    initialize_database()

    with _database_connection() as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(
                """
                SELECT *
                FROM appointments
                WHERE id = %s
                LIMIT 1
                """,
                (appointment_id,),
            )

            row = cursor.fetchone()

    return _json_safe_row(row) if row else None

def update_appointment_status(appointment_id: int, status: str,) -> None:
    initialize_database()
    
    allowed_statuses = {
        "pending",
        "approved",
        "done",
        "did_not_attend",
        "cancelled",
    }

    if status not in allowed_statuses:
        raise ValueError("Invalid appointment status.")
    
    with _database_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE appointments
                SET
                    status = %s,
                    updated_at = %s
                WHERE id = %s
                """,
                (
                    status,
                    current_time(),
                    appointment_id,
                )
            )
        connection.commit()
                
def update_counselor_notes(
    appointment_id: int,
    notes: str,
):
    initialize_database()

    with _database_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE appointments
                SET
                    counselor_notes = %s,
                    updated_at = %s
                WHERE id = %s
                """,
                (
                    notes,
                    current_time(),
                    appointment_id,
                ),
            )
        connection.commit()
