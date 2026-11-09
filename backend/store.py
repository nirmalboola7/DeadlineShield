
import os
import threading
from datetime import datetime, timezone

import mysql.connector

from config import BASE_DIR

_lock = threading.RLock()

# JSON collection name -> MySQL table and primary key
TABLES = {
    "users": ("users", "user_id"),
    "activities": ("activities", "activity_id"),
    "subjects": ("subjects", "subject_id"),
    "files": ("uploaded_files", "file_id"),
    "questions": ("revision_questions", "question_id"),
    "logs": ("activity_logs", "log_id"),
    "completion_awards": ("completion_awards", "award_id"),
}

# Columns allowed in each MySQL table
COLUMNS = {
    "users": [
        "user_id", "name", "email", "password_hash",
        "college", "department", "created_at"
    ],
    "activities": [
        "activity_id", "user_id", "title", "description",
        "activity_type", "subject", "due_date", "priority",
        "status", "created_at", "completed_at"
    ],
    "subjects": [
        "subject_id", "user_id", "name", "created_at"
    ],
    "files": [
        "file_id", "user_id", "file_name", "stored_name",
        "file_type", "uploaded_at"
    ],
    "questions": [
        "question_id", "user_id", "file_id", "subject",
        "question", "answer", "priority", "created_at"
    ],
    "logs": [
        "log_id", "user_id", "action", "details", "created_at"
    ],
    "completion_awards": [
        "award_id", "activity_id", "user_id",
        "activity_type", "points", "awarded_at"
    ],
}

DATETIME_COLUMNS = {
    "created_at",
    "due_date",
    "completed_at",
    "uploaded_at",
    "awarded_at"
}

_DEFAULT = {
    "users": [],
    "activities": [],
    "subjects": [],
    "files": [],
    "questions": [],
    "logs": [],
    "completion_awards": []
}


def get_connection():
    """Create a secure connection to the TiDB Cloud database."""

    ca_path = os.path.join(
        BASE_DIR,
        "certs",
        "tidb-ca.pem"
    )

    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "4000")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME", "learnova_db"),
        ssl_ca=ca_path,
        ssl_verify_cert=True,
        ssl_verify_identity=True,
        autocommit=False
    )



def get_user_by_id(user_id):
    """Fetch only one user by their primary key."""

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT * FROM users WHERE user_id = %s LIMIT 1",
            (user_id,)
        )
        return cursor.fetchone()

    finally:
        cursor.close()
        connection.close()


def to_mysql_datetime(value):
    """Convert ISO date strings into MySQL DATETIME values."""

    if value is None or isinstance(value, datetime):
        if isinstance(value, datetime) and value.tzinfo is not None:
            return value.astimezone(timezone.utc).replace(tzinfo=None)
        return value

    if isinstance(value, str):
        parsed = datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )

        if parsed.tzinfo is not None:
            parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)

        return parsed

    return value


def to_json_datetime(value):
    """Convert MySQL date/time values into ISO strings."""

    if isinstance(value, datetime):
        return value.isoformat()

    if hasattr(value, "isoformat"):
        return value.isoformat()

    return value


def read_db():
    """Read all LEARNOVA records from MySQL."""

    with _lock:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            data = {
                key: []
                for key in _DEFAULT
            }

            for key, (table, primary_key) in TABLES.items():
                cursor.execute(f"SELECT * FROM `{table}`")
                records = cursor.fetchall()

                for record in records:
                    for column in DATETIME_COLUMNS:
                        if column in record:
                            record[column] = to_json_datetime(
                                record[column]
                            )

                    data[key].append(record)

            return data

        finally:
            cursor.close()
            connection.close()


def write_db(data):
    """
    Synchronize application data with MySQL.

    Existing records are updated, new records are inserted,
    and records removed from supplied data are deleted.
    """

    with _lock:
        connection = get_connection()
        cursor = connection.cursor()

        try:
            connection.start_transaction()

            for key in TABLES:
                if key not in data or not isinstance(data[key], list):
                    raise ValueError(
                        f"Invalid or missing database collection: {key}"
                    )

            # Delete child records before parent records.
            delete_order = [
                "questions",
                "completion_awards",
                "activities",
                "subjects",
                "files",
                "logs",
                "users"
            ]

            for key in delete_order:
                table, primary_key = TABLES[key]

                ids = [
                    int(record[primary_key])
                    for record in data[key]
                    if record.get(primary_key) is not None
                ]

                if ids:
                    placeholders = ", ".join(["%s"] * len(ids))

                    cursor.execute(
                        f"DELETE FROM `{table}` "
                        f"WHERE `{primary_key}` NOT IN ({placeholders})",
                        ids
                    )
                else:
                    cursor.execute(f"DELETE FROM `{table}`")

            # Insert and update records.
            for key, (table, primary_key) in TABLES.items():

                for record in data[key]:

                    columns = [
                        column
                        for column in COLUMNS[key]
                        if column in record
                    ]

                    if primary_key not in columns:
                        raise ValueError(
                            f"Missing primary key {primary_key} in {key}"
                        )

                    values = []

                    for column in columns:
                        value = record[column]

                        if column in DATETIME_COLUMNS:
                            value = to_mysql_datetime(value)

                        values.append(value)

                    column_sql = ", ".join(
                        f"`{column}`" for column in columns
                    )

                    placeholders = ", ".join(
                        ["%s"] * len(columns)
                    )

                    update_columns = [
                        column for column in columns
                        if column != primary_key
                    ]

                    if update_columns:
                        update_sql = ", ".join(
                            f"`{column}` = VALUES(`{column}`)"
                            for column in update_columns
                        )

                        sql = (
                            f"INSERT INTO `{table}` ({column_sql}) "
                            f"VALUES ({placeholders}) "
                            f"ON DUPLICATE KEY UPDATE {update_sql}"
                        )
                    else:
                        sql = (
                            f"INSERT IGNORE INTO `{table}` "
                            f"({column_sql}) VALUES ({placeholders})"
                        )

                    cursor.execute(sql, values)

            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()


def next_id(items, key):
    """Generate the next ID from an existing collection."""

    return max(
        (int(item.get(key, 0)) for item in items),
        default=0
    ) + 1
