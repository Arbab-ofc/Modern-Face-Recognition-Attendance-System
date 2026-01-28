"""Pydantic schemas for API requests and responses."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class StudentResponse(BaseModel):
    """Student response schema."""

    student_id: str
    name: str
    created_at: datetime


class AttendanceRecordResponse(BaseModel):
    """Attendance record response schema."""

    student_id: str
    name: str
    date: str
    time: str
    status: str
    created_at: datetime


class RecognitionFace(BaseModel):
    """Recognition result for a face in an image."""

    student_id: Optional[str] = None
    name: str
    confidence: float
    location: List[int]
    is_match: bool


class RecognitionResponse(BaseModel):
    """Recognition response payload."""

    results: List[RecognitionFace]


class StatusResponse(BaseModel):
    """Standard status response."""

    success: bool
    message: str
