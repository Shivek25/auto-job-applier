import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

class Database:
    def __init__(self, db_path: Path | str = "storage/applications.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT UNIQUE NOT NULL,
                platform TEXT NOT NULL,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                location TEXT,
                job_url TEXT,
                match_score INTEGER,
                status TEXT NOT NULL, -- PENDING, SUBMITTED, FAILED, SKIPPED, NEEDS_REVIEW
                resume_path TEXT,
                screenshot_path TEXT,
                error_message TEXT,
                applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """)
            conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_job_id ON applications(job_id);
            """)
            conn.commit()

    def is_already_applied(self, job_id: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM applications WHERE job_id = ? AND status IN ('SUBMITTED', 'PENDING')",
                (job_id,)
            )
            return cursor.fetchone() is not None

    def add_application(
        self,
        job_id: str,
        platform: str,
        title: str,
        company: str,
        location: str,
        job_url: str,
        match_score: int,
        status: str = "PENDING",
        error_message: Optional[str] = None
    ) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO applications (
                job_id, platform, title, company, location, job_url, match_score, status, error_message, applied_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job_id, platform, title, company, location, job_url, match_score, status, error_message, datetime.now().isoformat()
            ))
            conn.commit()
            return cursor.lastrowid

    def update_status(
        self,
        job_id: str,
        status: str,
        resume_path: Optional[str] = None,
        screenshot_path: Optional[str] = None,
        error_message: Optional[str] = None
    ):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE applications
            SET status = ?,
                resume_path = COALESCE(?, resume_path),
                screenshot_path = COALESCE(?, screenshot_path),
                error_message = ?,
                applied_at = CURRENT_TIMESTAMP
            WHERE job_id = ?
            """, (status, resume_path, screenshot_path, error_message, job_id))
            if cursor.rowcount == 0:
                cursor.execute("""
                INSERT OR REPLACE INTO applications (
                    job_id, platform, title, company, location, job_url, match_score, status, resume_path, screenshot_path, error_message, applied_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (job_id, "unknown", "Unknown Title", "Unknown Company", "", "", 0, status, resume_path, screenshot_path, error_message))
            conn.commit()

    def get_application(self, job_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM applications WHERE job_id = ?", (job_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_all_applications(self, limit: int = 100, status: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if status and status.upper() != "ALL":
                cursor.execute(
                    "SELECT * FROM applications WHERE status = ? ORDER BY applied_at DESC LIMIT ?",
                    (status.upper(), limit)
                )
            else:
                cursor.execute(
                    "SELECT * FROM applications ORDER BY applied_at DESC LIMIT ?",
                    (limit,)
                )
            return [dict(row) for row in cursor.fetchall()]

    def get_stats(self) -> Dict[str, int]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'SUBMITTED' THEN 1 ELSE 0 END) as submitted,
                SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) as failed,
                SUM(CASE WHEN status = 'SKIPPED' THEN 1 ELSE 0 END) as skipped,
                SUM(CASE WHEN DATE(applied_at) = DATE('now') AND status = 'SUBMITTED' THEN 1 ELSE 0 END) as today_submitted
            FROM applications
            """)
            row = cursor.fetchone()
            return {
                "total": row["total"] or 0,
                "total_submitted": row["submitted"] or 0,
                "total_failed": row["failed"] or 0,
                "total_skipped": row["skipped"] or 0,
                "today_submitted": row["today_submitted"] or 0
            }
