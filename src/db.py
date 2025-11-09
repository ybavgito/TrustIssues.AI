"""
SQLite-backed persistence layer for TrustIssues.AI.
Keeps track of vendor submissions, processing state, and approvals.
"""
from __future__ import annotations

import sqlite3
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

DATA_DIR = Path("data")
DB_PATH = DATA_DIR / "app.db"


def _get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(exist_ok=True, parents=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                submission_id TEXT UNIQUE,
                session_id TEXT,
                original_filename TEXT,
                pdf_path TEXT,
                submitted_by TEXT,
                vendor_name TEXT,
                status TEXT,
                risk_score INTEGER,
                risk_level TEXT,
                submitted_at TEXT,
                processed_at TEXT,
                updated_at TEXT
            )
            """
        )
        # Ensure submitted_by column exists for older databases
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(submissions)")}
        if "submitted_by" not in columns:
            conn.execute("ALTER TABLE submissions ADD COLUMN submitted_by TEXT")
        conn.commit()


def _utc_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def record_submission(original_filename: str, pdf_path: str, submitted_by: Optional[str] = None) -> str:
    """Create a submission record when a vendor uploads a document."""
    submission_id = str(uuid.uuid4())
    now = _utc_now()
    with _get_connection() as conn:
        conn.execute(
            """
            INSERT INTO submissions (
                submission_id,
                original_filename,
                pdf_path,
                status,
                submitted_by,
                submitted_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (submission_id, original_filename, pdf_path, "uploaded", submitted_by, now, now),
        )
        conn.commit()
    return submission_id


def get_submission_by_pdf(pdf_path: str) -> Optional[sqlite3.Row]:
    with _get_connection() as conn:
        cur = conn.execute(
            """
            SELECT *
            FROM submissions
            WHERE pdf_path = ?
            ORDER BY submitted_at DESC
            LIMIT 1
            """,
            (pdf_path,),
        )
        return cur.fetchone()


def update_after_processing(pdf_path: str, session_id: str, vendor_name: Optional[str],
                            risk_score: Optional[int], risk_level: Optional[str]) -> None:
    """Update submission after AI processing completes."""
    row = get_submission_by_pdf(pdf_path)
    if not row:
        # If the PDF is a test file we didn't record, skip persistence.
        return

    status = "pending_review"
    now = _utc_now()
    with _get_connection() as conn:
        conn.execute(
            """
            UPDATE submissions
            SET
                session_id = ?,
                vendor_name = COALESCE(?, vendor_name),
                risk_score = ?,
                risk_level = ?,
                status = ?,
                processed_at = ?,
                updated_at = ?
            WHERE pdf_path = ?
            """,
            (
                session_id,
                vendor_name,
                risk_score,
                risk_level,
                status,
                now,
                now,
                pdf_path,
            ),
        )
        conn.commit()


def mark_submission_status(submission_id: str, status: str) -> None:
    with _get_connection() as conn:
        conn.execute(
            """
            UPDATE submissions
            SET status = ?, updated_at = ?
            WHERE submission_id = ?
            """,
            (status, _utc_now(), submission_id),
        )
        conn.commit()


def get_pending_submissions() -> List[Dict[str, Any]]:
    """Get submissions that need admin attention (uploaded or pending_review)."""
    with _get_connection() as conn:
        cur = conn.execute(
            """
            SELECT *
            FROM submissions
            WHERE status IN ('uploaded', 'pending_review')
            ORDER BY (processed_at IS NULL) DESC, submitted_at DESC
            """
        )
        return [dict(row) for row in cur.fetchall()]


def get_stats() -> Dict[str, Any]:
    with _get_connection() as conn:
        cur = conn.execute(
            """
            SELECT
                COUNT(*) AS total,
                SUM(status = 'pending_review') AS pending_review,
                SUM(status = 'approved') AS approved,
                SUM(status = 'rejected') AS rejected,
                AVG(CASE WHEN risk_score IS NOT NULL THEN risk_score END) AS avg_risk
            FROM submissions
            """
        )
        row = cur.fetchone()
        return {
            "total": row["total"] or 0,
            "pending_review": row["pending_review"] or 0,
            "approved": row["approved"] or 0,
            "rejected": row["rejected"] or 0,
            "avg_risk": round(row["avg_risk"], 1) if row["avg_risk"] is not None else None,
        }


def get_recent_submissions(limit: int = 6, submitted_by: Optional[str] = None) -> List[Dict[str, Any]]:
    with _get_connection() as conn:
        if submitted_by:
            cur = conn.execute(
                """
                SELECT *
                FROM submissions
                WHERE submitted_by = ?
                ORDER BY submitted_at DESC
                LIMIT ?
                """,
                (submitted_by, limit),
            )
            return [dict(row) for row in cur.fetchall()]
        cur = conn.execute(
            """
            SELECT *
            FROM submissions
            ORDER BY submitted_at DESC
            LIMIT ?
            """,
            (limit,),
        )
        return [dict(row) for row in cur.fetchall()]


# Initialize database on import
init_db()


