"""Face detection and recognition service."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

import cv2
import face_recognition
import numpy as np

from backend.app.services.mongo_service import get_db_service
from backend.app.utils.constants import FACE_RECOGNITION


@dataclass
class RecognitionResult:
    """Recognition result for a single face."""

    student_id: Optional[str]
    name: str
    confidence: float
    location: Tuple[int, int, int, int]
    is_match: bool


class FaceRecognitionService:
    """Service for detecting and matching faces."""

    def __init__(self) -> None:
        self._tolerance = FACE_RECOGNITION.TOLERANCE
        self._known_encodings: List[np.ndarray] = []
        self._known_ids: List[str] = []
        self._known_names: List[str] = []

    def load_known_faces(self) -> int:
        """Load face encodings from the database."""
        service = get_db_service()
        records = service.get_all_face_encodings()
        self._known_encodings = []
        self._known_ids = []
        self._known_names = []
        for student_id, name, encoding in records:
            self._known_encodings.append(encoding)
            self._known_ids.append(student_id)
            self._known_names.append(name)
        return len(self._known_encodings)

    def detect_faces(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Detect faces in the frame."""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        locations = face_recognition.face_locations(rgb_frame, model=FACE_RECOGNITION.MODEL)
        return locations

    def encode_faces(
        self, frame: np.ndarray, locations: List[Tuple[int, int, int, int]]
    ) -> List[np.ndarray]:
        """Encode faces at the provided locations."""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return face_recognition.face_encodings(
            rgb_frame, known_face_locations=locations, num_jitters=FACE_RECOGNITION.NUM_JITTERS
        )

    def recognize_faces(
        self, frame: np.ndarray
    ) -> List[RecognitionResult]:
        """Detect and recognize faces in a frame."""
        if not self._known_encodings:
            self.load_known_faces()

        locations = self.detect_faces(frame)
        if not locations:
            return []

        encodings = self.encode_faces(frame, locations)
        results: List[RecognitionResult] = []

        for location, encoding in zip(locations, encodings):
            results.append(self._match_face(encoding, location))
        return results

    def _match_face(
        self, encoding: np.ndarray, location: Tuple[int, int, int, int]
    ) -> RecognitionResult:
        if not self._known_encodings:
            return RecognitionResult(None, "Unknown", 0.0, location, False)

        distances = face_recognition.face_distance(self._known_encodings, encoding)
        best_index = int(np.argmin(distances)) if distances.size > 0 else -1

        if best_index >= 0 and distances[best_index] < self._tolerance:
            confidence = max(0.0, min(1.0, 1.0 - float(distances[best_index])))
            return RecognitionResult(
                self._known_ids[best_index],
                self._known_names[best_index],
                confidence,
                location,
                True,
            )

        return RecognitionResult(None, "Unknown", 0.0, location, False)
