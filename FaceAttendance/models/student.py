"""Student data model and builder."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional

import numpy as np
from bson import ObjectId

from utils.constants import FACE_RECOGNITION
from utils.helpers import (
    binary_to_numpy,
    numpy_to_binary,
    validate_name,
    validate_student_id,
)


@dataclass
class Student:
    """Student model for MongoDB persistence."""

    student_id: str
    name: str
    face_encoding: Optional[np.ndarray] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    _id: Optional[ObjectId] = None

    def __post_init__(self) -> None:
        """Validate model fields after initialization."""
        valid_id, id_message = validate_student_id(self.student_id)
        if not valid_id:
            raise ValueError(id_message)

        valid_name, name_message = validate_name(self.name)
        if not valid_name:
            raise ValueError(name_message)

        if self.face_encoding is not None:
            if not isinstance(self.face_encoding, np.ndarray):
                raise ValueError("Face encoding must be a numpy array.")
            if self.face_encoding.size != FACE_RECOGNITION.ENCODING_SIZE:
                raise ValueError("Face encoding has invalid size.")

    def to_document(self) -> Dict:
        """Convert the model to a MongoDB document."""
        document = {
            "student_id": self.student_id,
            "name": self.name,
            "created_at": self.created_at,
        }
        if self.face_encoding is not None:
            document["face_encoding"] = numpy_to_binary(self.face_encoding)
        if self._id is not None:
            document["_id"] = self._id
        return document

    @classmethod
    def from_document(cls, doc: Dict) -> "Student":
        """Create a Student instance from a MongoDB document."""
        face_encoding = None
        if doc.get("face_encoding") is not None:
            face_encoding = binary_to_numpy(doc["face_encoding"])
        return cls(
            student_id=doc.get("student_id", ""),
            name=doc.get("name", ""),
            face_encoding=face_encoding,
            created_at=doc.get("created_at", datetime.utcnow()),
            _id=doc.get("_id"),
        )

    def has_face_encoding(self) -> bool:
        """Check if a valid face encoding exists."""
        return (
            self.face_encoding is not None
            and isinstance(self.face_encoding, np.ndarray)
            and self.face_encoding.size == FACE_RECOGNITION.ENCODING_SIZE
        )


class StudentBuilder:
    """Fluent builder for the Student model."""

    def __init__(self) -> None:
        self._student_id: Optional[str] = None
        self._name: Optional[str] = None
        self._face_encoding: Optional[np.ndarray] = None

    def with_id(self, student_id: str) -> "StudentBuilder":
        """Set the student ID."""
        self._student_id = student_id
        return self

    def with_name(self, name: str) -> "StudentBuilder":
        """Set the student name."""
        self._name = name
        return self

    def with_face_encoding(self, encoding: np.ndarray) -> "StudentBuilder":
        """Set the face encoding."""
        self._face_encoding = encoding
        return self

    def build(self) -> Student:
        """Build a Student instance."""
        if self._student_id is None or self._name is None:
            raise ValueError("Student ID and name are required.")
        return Student(
            student_id=self._student_id,
            name=self._name,
            face_encoding=self._face_encoding,
        )
