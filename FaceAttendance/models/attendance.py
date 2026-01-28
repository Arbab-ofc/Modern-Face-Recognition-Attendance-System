"""Attendance models and helpers."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from bson import ObjectId

from utils.helpers import get_current_date, get_current_time


class AttendanceStatus(str, Enum):
    """Attendance status values."""

    PRESENT = "present"
    LATE = "late"
    ABSENT = "absent"
    EXCUSED = "excused"


@dataclass
class AttendanceRecord:
    """Attendance record model for MongoDB."""

    student_id: str
    name: str
    date: str
    time: str
    status: AttendanceStatus
    _id: Optional[ObjectId] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_document(self) -> Dict:
        """Convert the record to a MongoDB document."""
        document = {
            "student_id": self.student_id,
            "name": self.name,
            "date": self.date,
            "time": self.time,
            "status": self.status.value,
            "created_at": self.created_at,
        }
        if self._id is not None:
            document["_id"] = self._id
        return document

    @classmethod
    def from_document(cls, doc: Dict) -> "AttendanceRecord":
        """Create an AttendanceRecord instance from a document."""
        return cls(
            student_id=doc.get("student_id", ""),
            name=doc.get("name", ""),
            date=doc.get("date", ""),
            time=doc.get("time", ""),
            status=AttendanceStatus(doc.get("status", AttendanceStatus.PRESENT.value)),
            _id=doc.get("_id"),
            created_at=doc.get("created_at", datetime.utcnow()),
        )

    @classmethod
    def create_present(cls, student_id: str, name: str) -> "AttendanceRecord":
        """Factory method for present status."""
        return cls(
            student_id=student_id,
            name=name,
            date=get_current_date(),
            time=get_current_time(),
            status=AttendanceStatus.PRESENT,
        )

    def is_today(self) -> bool:
        """Check if the record is for today."""
        return self.date == get_current_date()


@dataclass
class AttendanceSummary:
    """Summary statistics for attendance."""

    total_students: int
    present_today: int
    absent_today: int
    late_today: int
    attendance_rate: float

    @classmethod
    def calculate(
        cls, total_students: int, attendance_records: List[AttendanceRecord]
    ) -> "AttendanceSummary":
        """Calculate summary data from attendance records."""
        present_today = sum(
            1 for record in attendance_records if record.status == AttendanceStatus.PRESENT
        )
        late_today = sum(
            1 for record in attendance_records if record.status == AttendanceStatus.LATE
        )
        absent_today = max(total_students - (present_today + late_today), 0)
        if total_students > 0:
            attendance_rate = ((present_today + late_today) / total_students) * 100
        else:
            attendance_rate = 0.0
        return cls(
            total_students=total_students,
            present_today=present_today,
            absent_today=absent_today,
            late_today=late_today,
            attendance_rate=attendance_rate,
        )


class AttendanceFilter:
    """Filter builder for attendance queries."""

    def __init__(self) -> None:
        self._query: Dict = {}

    def by_date(self, date_str: str) -> "AttendanceFilter":
        """Filter by a specific date."""
        self._query["date"] = date_str
        return self

    def by_date_range(self, start: str, end: str) -> "AttendanceFilter":
        """Filter by a date range."""
        self._query["date"] = {"$gte": start, "$lte": end}
        return self

    def by_student(self, student_id: str) -> "AttendanceFilter":
        """Filter by student ID."""
        self._query["student_id"] = student_id
        return self

    def by_status(self, status: AttendanceStatus) -> "AttendanceFilter":
        """Filter by status."""
        self._query["status"] = status.value
        return self

    def build(self) -> Dict:
        """Return the built query."""
        return dict(self._query)

    def clear(self) -> "AttendanceFilter":
        """Clear all filters."""
        self._query.clear()
        return self
