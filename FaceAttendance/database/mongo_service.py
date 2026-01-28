"""MongoDB service layer with singleton connection management."""
from __future__ import annotations

import logging
from typing import List, Optional, Tuple

from pymongo import MongoClient
from pymongo.errors import (
    ConnectionFailure,
    DuplicateKeyError,
    PyMongoError,
    ServerSelectionTimeoutError,
)

from models.attendance import AttendanceFilter, AttendanceRecord
from models.student import Student
from utils.constants import DATABASE, MESSAGES
from utils.helpers import binary_to_numpy, get_current_date


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
        """Create database indexes for performance and integrity."""
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

    def disconnect(self) -> None:
        """Disconnect from MongoDB."""
        if self._client is not None:
            self._client.close()
        self._client = None
        self._db = None
        self._students_collection = None
        self._attendance_collection = None

    def is_connected(self) -> bool:
        """Check if the connection is alive."""
        if self._client is None:
            return False
        try:
            self._client.admin.command("ping")
            return True
        except PyMongoError:
            return False

    def add_student(self, student: Student) -> Tuple[bool, str]:
        """Add a new student to the database."""
        if self._students_collection is None:
            return False, MESSAGES.DATABASE_ERROR
        if self.student_exists(student.student_id):
            return False, MESSAGES.DUPLICATE_STUDENT
        try:
            self._students_collection.insert_one(student.to_document())
            return True, MESSAGES.STUDENT_REGISTERED
        except DuplicateKeyError:
            return False, MESSAGES.DUPLICATE_STUDENT
        except PyMongoError as exc:
            logger.error("Failed to add student: %s", exc)
            return False, MESSAGES.DATABASE_ERROR

    def get_student_by_id(self, student_id: str) -> Optional[Student]:
        """Fetch a student by ID."""
        if self._students_collection is None:
            return None
        try:
            doc = self._students_collection.find_one({"student_id": student_id})
            return Student.from_document(doc) if doc else None
        except PyMongoError as exc:
            logger.error("Failed to fetch student: %s", exc)
            return None

    def get_all_students(self) -> List[Student]:
        """Fetch all students."""
        if self._students_collection is None:
            return []
        try:
            return [Student.from_document(doc) for doc in self._students_collection.find()]
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

    def update_student(self, student: Student) -> Tuple[bool, str]:
        """Update an existing student."""
        if self._students_collection is None:
            return False, MESSAGES.DATABASE_ERROR
        try:
            result = self._students_collection.update_one(
                {"student_id": student.student_id}, {"$set": student.to_document()}
            )
            if result.matched_count == 0:
                return False, "Student not found."
            return True, "Student updated successfully."
        except DuplicateKeyError:
            return False, MESSAGES.DUPLICATE_STUDENT
        except PyMongoError as exc:
            logger.error("Failed to update student: %s", exc)
            return False, MESSAGES.DATABASE_ERROR

    def delete_student(self, student_id: str) -> Tuple[bool, str]:
        """Delete a student by ID."""
        if self._students_collection is None:
            return False, MESSAGES.DATABASE_ERROR
        try:
            result = self._students_collection.delete_one({"student_id": student_id})
            if result.deleted_count == 0:
                return False, "Student not found."
            return True, "Student deleted successfully."
        except PyMongoError as exc:
            logger.error("Failed to delete student: %s", exc)
            return False, MESSAGES.DATABASE_ERROR

    def get_student_count(self) -> int:
        """Return the number of students."""
        if self._students_collection is None:
            return 0
        try:
            return self._students_collection.count_documents({})
        except PyMongoError as exc:
            logger.error("Failed to count students: %s", exc)
            return 0

    def student_exists(self, student_id: str) -> bool:
        """Check if a student ID already exists."""
        if self._students_collection is None:
            return False
        try:
            return self._students_collection.count_documents({"student_id": student_id}) > 0
        except PyMongoError:
            return False

    def mark_attendance(self, record: AttendanceRecord) -> Tuple[bool, str]:
        """Insert a new attendance record if not already marked."""
        if self._attendance_collection is None:
            return False, MESSAGES.DATABASE_ERROR
        if self.has_attendance_today(record.student_id):
            return False, MESSAGES.DUPLICATE_ATTENDANCE
        try:
            self._attendance_collection.insert_one(record.to_document())
            return True, MESSAGES.ATTENDANCE_MARKED
        except DuplicateKeyError:
            return False, MESSAGES.DUPLICATE_ATTENDANCE
        except PyMongoError as exc:
            logger.error("Failed to mark attendance: %s", exc)
            return False, MESSAGES.DATABASE_ERROR

    def get_attendance_by_date(self, date_str: str) -> List[AttendanceRecord]:
        """Return attendance records for a specific date."""
        if self._attendance_collection is None:
            return []
        try:
            docs = self._attendance_collection.find({"date": date_str}).sort("time", -1)
            return [AttendanceRecord.from_document(doc) for doc in docs]
        except PyMongoError as exc:
            logger.error("Failed to fetch attendance by date: %s", exc)
            return []

    def get_attendance_by_filter(self, filter_obj: AttendanceFilter) -> List[AttendanceRecord]:
        """Return attendance records by filter."""
        if self._attendance_collection is None:
            return []
        try:
            docs = self._attendance_collection.find(filter_obj.build()).sort("date", -1)
            return [AttendanceRecord.from_document(doc) for doc in docs]
        except PyMongoError as exc:
            logger.error("Failed to fetch attendance by filter: %s", exc)
            return []

    def has_attendance_today(self, student_id: str) -> bool:
        """Check if attendance already exists for the given student today."""
        if self._attendance_collection is None:
            return False
        try:
            return (
                self._attendance_collection.count_documents(
                    {"student_id": student_id, "date": get_current_date()}
                )
                > 0
            )
        except PyMongoError:
            return False

    def get_today_attendance_count(self) -> int:
        """Return count of attendance records for today."""
        return len(self.get_attendance_by_date(get_current_date()))

    def get_attendance_by_date_range(self, start: str, end: str) -> List[AttendanceRecord]:
        """Return attendance records for a date range."""
        if self._attendance_collection is None:
            return []
        try:
            query = {"date": {"$gte": start, "$lte": end}}
            docs = self._attendance_collection.find(query).sort("date", -1)
            return [AttendanceRecord.from_document(doc) for doc in docs]
        except PyMongoError as exc:
            logger.error("Failed to fetch attendance by date range: %s", exc)
            return []

    def get_student_attendance_history(
        self, student_id: str, limit: int = 20
    ) -> List[AttendanceRecord]:
        """Return a student's recent attendance history."""
        if self._attendance_collection is None:
            return []
        try:
            docs = (
                self._attendance_collection.find({"student_id": student_id})
                .sort("date", -1)
                .limit(limit)
            )
            return [AttendanceRecord.from_document(doc) for doc in docs]
        except PyMongoError as exc:
            logger.error("Failed to fetch student attendance history: %s", exc)
            return []


def get_db_service() -> MongoDBService:
    """Return the singleton MongoDB service instance."""
    return MongoDBService()
