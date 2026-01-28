"""Face recognition and matching utilities."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

import face_recognition
import numpy as np

from database.mongo_service import get_db_service
from utils.constants import FACE_RECOGNITION


@dataclass
class RecognitionResult:
    """Result of a recognition attempt."""

    student_id: Optional[str]
    name: str
    confidence: float
    location: Tuple[int, int, int, int]
    is_match: bool

    @classmethod
    def unknown(cls, location: Tuple[int, int, int, int]) -> "RecognitionResult":
        """Create an unknown recognition result."""
        return cls(student_id=None, name="Unknown", confidence=0.0, location=location, is_match=False)


class FaceRecognizer:
    """Match face encodings against known database entries."""

    def __init__(self, tolerance: Optional[float] = None) -> None:
        self._tolerance = tolerance if tolerance is not None else FACE_RECOGNITION.TOLERANCE
        self._known_encodings: List[np.ndarray] = []
        self._known_ids: List[str] = []
        self._known_names: List[str] = []
        self._last_load_time: Optional[datetime] = None
        self._cache_duration = 60

    def load_known_faces(self) -> int:
        """Load known face encodings from the database."""
        service = get_db_service()
        records = service.get_all_face_encodings()

        self._known_encodings = []
        self._known_ids = []
        self._known_names = []

        for student_id, name, encoding in records:
            self._known_ids.append(student_id)
            self._known_names.append(name)
            self._known_encodings.append(encoding)

        self._last_load_time = datetime.utcnow()
        return len(self._known_encodings)

    def refresh_if_needed(self) -> None:
        """Reload known faces if cache duration has expired."""
        if self._last_load_time is None:
            self.load_known_faces()
            return

        if datetime.utcnow() - self._last_load_time > timedelta(seconds=self._cache_duration):
            self.load_known_faces()

    def recognize_face(
        self, encoding: np.ndarray, location: Tuple[int, int, int, int]
    ) -> RecognitionResult:
        """Recognize a single face encoding."""
        if not self._known_encodings:
            return RecognitionResult.unknown(location)

        distances = face_recognition.face_distance(self._known_encodings, encoding)
        if distances.size == 0:
            return RecognitionResult.unknown(location)

        best_index = int(np.argmin(distances))
        best_distance = float(distances[best_index])

        if best_distance < self._tolerance:
            confidence = max(0.0, min(1.0, 1.0 - best_distance))
            return RecognitionResult(
                student_id=self._known_ids[best_index],
                name=self._known_names[best_index],
                confidence=confidence,
                location=location,
                is_match=True,
            )

        return RecognitionResult.unknown(location)

    def recognize_faces_in_frame(
        self,
        frame: np.ndarray,
        face_locations: List[Tuple[int, int, int, int]],
        face_encodings: List[np.ndarray],
    ) -> List[RecognitionResult]:
        """Recognize all faces in a frame."""
        results = []
        for location, encoding in zip(face_locations, face_encodings):
            results.append(self.recognize_face(encoding, location))
        return results

    def add_known_face(self, student_id: str, name: str, encoding: np.ndarray) -> None:
        """Add a known face to the in-memory cache."""
        self._known_ids.append(student_id)
        self._known_names.append(name)
        self._known_encodings.append(encoding)

    def get_known_count(self) -> int:
        """Return the number of known faces."""
        return len(self._known_encodings)

    def clear_cache(self) -> None:
        """Clear cached face data."""
        self._known_encodings.clear()
        self._known_ids.clear()
        self._known_names.clear()
        self._last_load_time = None
