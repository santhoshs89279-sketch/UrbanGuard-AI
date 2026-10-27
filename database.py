
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent / "urbanguard.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def initialize_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                message TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS traffic_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                vehicle_count INTEGER NOT NULL
            )
        """)


def save_alert(alert_type, severity, message):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO alerts
            (timestamp, alert_type, severity, message)
            VALUES (?, ?, ?, ?)
            """,
            (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                alert_type,
                severity,
                message
            )
        )


def save_traffic_count(vehicle_count):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO traffic_history
            (timestamp, vehicle_count)
            VALUES (?, ?)
            """,
            (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                int(vehicle_count)
            )
        )


def get_alerts(limit=500):
    with get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT timestamp, alert_type, severity, message
            FROM alerts
            ORDER BY id DESC
            LIMIT ?
            """,
            (int(limit),)
        )
        rows = cursor.fetchall()

    return [
        {
            "Time": row[0],
            "Alert Type": row[1],
            "Severity": row[2],
            "Message": row[3]
        }
        for row in rows
    ]


def get_traffic_history(limit=1000):
    with get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT timestamp, vehicle_count
            FROM traffic_history
            ORDER BY id DESC
            LIMIT ?
            """,
            (int(limit),)
        )
        rows = cursor.fetchall()

    rows.reverse()

    return [
        {"Time": row[0], "Vehicle Count": row[1]}
        for row in rows
    ]


initialize_database()
