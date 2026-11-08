import json
from pathlib import Path
from datetime import datetime, timezone

import mysql.connector
from dotenv import load_dotenv
import os

# Load MySQL settings from .env
load_dotenv(Path(__file__).resolve().parent / ".env")

# Existing JSON database
JSON_FILE = Path(__file__).resolve().parent / "data" / "db.json"

# Convert JSON date strings into MySQL-compatible datetime values
def convert_datetime(value):
    if value is None or not isinstance(value, str):
        return value

    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))

        if parsed.tzinfo is not None:
            parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)

        return parsed
    except ValueError:
        raise ValueError(f"Could not convert date value: {value}")


# JSON collection -> MySQL table -> allowed columns
TABLES = [
    ("users", "users", [
        "user_id", "name", "email", "password_hash",
        "college", "department", "created_at"
    ]),
    ("activities", "activities", [
        "activity_id", "user_id", "title", "description",
        "activity_type", "subject", "due_date", "priority",
        "status", "created_at", "completed_at"
    ]),
    ("subjects", "subjects", [
        "subject_id", "user_id", "name", "created_at"
    ]),
    ("files", "uploaded_files", [
        "file_id", "user_id", "file_name", "stored_name",
        "file_type", "uploaded_at"
    ]),
    ("questions", "revision_questions", [
        "question_id", "user_id", "file_id", "subject",
        "question", "answer", "priority", "created_at"
    ]),
    ("logs", "activity_logs", [
        "log_id", "user_id", "action", "details", "created_at"
    ]),
    ("completion_awards", "completion_awards", [
        "award_id", "activity_id", "user_id",
        "activity_type", "points", "awarded_at"
    ])
]

DATETIME_COLUMNS = {
    "created_at", "due_date", "completed_at",
    "uploaded_at", "awarded_at"
}


def main():
    if not JSON_FILE.exists():
        raise FileNotFoundError("Existing db.json file was not found.")

    with open(JSON_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

    cursor = connection.cursor()

    try:
        print("\nStarting LEARNOVA JSON to MySQL migration...\n")

        for json_key, table_name, allowed_columns in TABLES:
            records = data.get(json_key, [])

            if not records:
                print(f"{table_name}: 0 records to migrate")
                continue

            migrated = 0

            for record in records:
                columns = [
                    column for column in allowed_columns
                    if column in record
                ]

                if not columns:
                    continue

                values = []

                for column in columns:
                    value = record[column]

                    if column in DATETIME_COLUMNS:
                        value = convert_datetime(value)

                    values.append(value)

                column_sql = ", ".join(f"`{c}`" for c in columns)
                placeholders = ", ".join(["%s"] * len(columns))

                sql = (
                    f"INSERT IGNORE INTO `{table_name}` "
                    f"({column_sql}) VALUES ({placeholders})"
                )

                cursor.execute(sql, values)

                if cursor.rowcount > 0:
                    migrated += 1

            print(f"{table_name}: {migrated} records copied")

        connection.commit()
        print("\nSUCCESS: Migration completed!")

    except Exception:
        connection.rollback()
        print("\nMigration failed. Changes were rolled back.")
        raise

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    main()