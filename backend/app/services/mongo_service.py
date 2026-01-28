"""MongoDB service layer for the web backend."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import List, Optional, Tuple

from pymongo import MongoClient
from pymongo.errors import (
    ConnectionFailure,
    DuplicateKeyError,
    PyMongoError,
    ServerSelectionTimeoutError,
)

from app.utils.constants import DATABASE
from app.utils.helpers import binary_to_numpy, get_current_date, get_current_time


logger = logging.getLogger(__name__)


class MongoDBService:
    """Singleton MongoDB service for database operations."""

    _instance: Optional["MongoDBService"] = None

    def __new__(cls) -> "MongoDBService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if hasattr(self, "_initialized") and self._initialized:
            return
        self._client: Optional[MongoClient] = None
        self._db = None
        self._students_collection = None
        self._attendance_collection = None
        self._initialized = True

    def connect(self) -> bool:
        """Connect to MongoDB and initialize collections."""
        try:
            self._client = MongoClient(
                DATABASE.URI,
                serverSelectionTimeoutMS=DATABASE.SERVER_SELECTION_TIMEOUT_MS,
                connectTimeoutMS=DATABASE.CONNECTION_TIMEOUT_MS,
            )
            self._client.admin.command("ping")
            self._db = self._client[DATABASE.DATABASE_NAME]
            self._students_collection = self._db[DATABASE.STUDENTS_COLLECTION]
            self._attendance_collection = self._db[DATABASE.ATTENDANCE_COLLECTION]
            self._create_indexes()
            return True
        except (ConnectionFailure, ServerSelectionTimeoutError) as exc:
            logger.error("Database connection failed: %s", exc)
            return False
        except PyMongoError as exc:
            logger.error("Unexpected database error: %s", exc)
            return False

    def _create_indexes(self) -> None:
        if self._students_collection is None or self._attendance_collection is None:
            return
        try:
            self._students_collection.create_index("student_id", unique=True)
            self._attendance_collection.create_index(
                [("student_id", 1), ("date", 1)], unique=True
            )
            self._attendance_collection.create_index("date")
        except PyMongoError as exc:
            logger.error("Failed to create indexes: %s", exc)

    def is_connected(self) -> bool:
        """Check if the connection is alive."""
        if self._client is None:
            return False
        try:
            self._client.admin.command("ping")
            return True
        except PyMongoError:
            return False

    def add_student(self, student_doc: dict) -> Tuple[bool, str]:
        """Add a new student document."""
        if self._students_collection is None:
            return False, "Database not connected."
        try:
            self._students_collection.insert_one(student_doc)
            return True, "Student registered successfully"
        except DuplicateKeyError:
            return False, "Student ID already exists in the system."
        except PyMongoError as exc:
            logger.error("Failed to add student: %s", exc)
            return False, "Database connection failed."

    def student_exists(self, student_id: str) -> bool:
        """Check if a student ID already exists."""
        if self._students_collection is None:
            return False
        try:
            return self._students_collection.count_documents({"student_id": student_id}) > 0
        except PyMongoError:
            return False

    def get_students(self) -> List[dict]:
        """Fetch all students."""
        if self._students_collection is None:
            return []
        try:
            return list(self._students_collection.find({}, {"face_encoding": 0}))
        except PyMongoError as exc:
            logger.error("Failed to fetch students: %s", exc)
            return []

    def get_all_face_encodings(self) -> List[Tuple[str, str, object]]:
        """Return all face encodings for recognition."""
        if self._students_collection is None:
            return []
        try:
            query = {"face_encoding": {"$exists": True}}
            results = []
            for doc in self._students_collection.find(query):
                encoding = binary_to_numpy(doc["face_encoding"])
                results.append((doc.get("student_id", ""), doc.get("name", ""), encoding))
            return results
        except PyMongoError as exc:
            logger.error("Failed to fetch face encodings: %s", exc)
            return []

    def mark_attendance(self, student_id: str, name: str, status: str = "present") -> Tuple[bool, str]:
        """Insert a new attendance record if not already marked."""
        if self._attendance_collection is None:
            return False, "Database not connected."

        date_str = get_current_date()
        time_str = get_current_time()
        record = {
            "student_id": student_id,
            "name": name,
            "date": date_str,
            "time": time_str,
            "status": status,
            "created_at": datetime.utcnow(),
        }
        try:
            self._attendance_collection.insert_one(record)
            return True, "Attendance marked successfully"
        except DuplicateKeyError:
            return False, "Attendance already marked for today."
        except PyMongoError as exc:
            logger.error("Failed to mark attendance: %s", exc)
            return False, "Database connection failed."

    def get_attendance_by_date(self, date_str: str) -> List[dict]:
        """Fetch attendance records by date."""
        if self._attendance_collection is None:
            return []
        try:
            return list(self._attendance_collection.find({"date": date_str}))
        except PyMongoError as exc:
            logger.error("Failed to fetch attendance: %s", exc)
            return []

    def get_attendance_by_range(self, start: str, end: str) -> List[dict]:
        """Fetch attendance records by date range."""
        if self._attendance_collection is None:
            return []
        try:
            query = {"date": {"$gte": start, "$lte": end}}
            return list(self._attendance_collection.find(query))
        except PyMongoError as exc:
            logger.error("Failed to fetch attendance range: %s", exc)
            return []

    def get_today_attendance_count(self) -> int:
        """Return count of today's attendance records."""
        if self._attendance_collection is None:
            return 0
        try:
            return self._attendance_collection.count_documents({"date": get_current_date()})
        except PyMongoError:
            return 0


_service_instance = MongoDBService()


def get_db_service() -> MongoDBService:
    """Return the singleton MongoDB service instance."""
    return _service_instance
