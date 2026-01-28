"""Face detection and encoding utilities."""
from __future__ import annotations

from typing import List, Optional, Tuple

import cv2
import face_recognition
import numpy as np

from utils.constants import FACE_RECOGNITION


class FaceDetector:
    """Face detector and encoder wrapper."""

    def __init__(self, model: Optional[str] = None) -> None:
        self._model = model or FACE_RECOGNITION.MODEL
        self._scale_factor = FACE_RECOGNITION.SCALE_FACTOR
        self._min_face_size = FACE_RECOGNITION.MIN_FACE_SIZE

    def detect_faces(
        self, frame: np.ndarray, scale: bool = True
    ) -> List[Tuple[int, int, int, int]]:
        """Detect faces in a frame and return locations."""
        if frame is None:
            return []

        scale_factor = self._scale_factor if scale else 1.0
        if scale_factor != 1.0:
            small_frame = cv2.resize(
                frame, (0, 0), fx=scale_factor, fy=scale_factor
            )
        else:
            small_frame = frame

        rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        locations = face_recognition.face_locations(rgb_frame, model=self._model)

        if scale_factor != 1.0:
            scaled_locations = []
            for top, right, bottom, left in locations:
                scaled_locations.append(
                    (
                        int(top / scale_factor),
                        int(right / scale_factor),
                        int(bottom / scale_factor),
                        int(left / scale_factor),
                    )
                )
            locations = scaled_locations

        return [loc for loc in locations if self._is_valid_face_size(loc)]

    def _is_valid_face_size(self, location: Tuple[int, int, int, int]) -> bool:
        """Validate that face meets minimum size requirements."""
        top, right, bottom, left = location
        width = right - left
        height = bottom - top
        return width >= self._min_face_size and height >= self._min_face_size

    def get_face_encoding(
        self, frame: np.ndarray, location: Optional[Tuple[int, int, int, int]] = None
    ) -> Optional[np.ndarray]:
        """Get a face encoding from a frame."""
        if frame is None:
            return None

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        locations = [location] if location is not None else self.detect_faces(frame, scale=False)
        if not locations:
            return None

        encodings = face_recognition.face_encodings(
            rgb_frame, known_face_locations=locations, num_jitters=FACE_RECOGNITION.NUM_JITTERS
        )
        return encodings[0] if encodings else None

    def detect_and_encode(
        self, frame: np.ndarray
    ) -> List[Tuple[Tuple[int, int, int, int], np.ndarray]]:
        """Detect faces and return locations with encodings."""
        if frame is None:
            return []

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        locations = self.detect_faces(frame, scale=True)
        if not locations:
            return []

        encodings = face_recognition.face_encodings(
            rgb_frame, known_face_locations=locations, num_jitters=FACE_RECOGNITION.NUM_JITTERS
        )

        results = []
        for location, encoding in zip(locations, encodings):
            results.append((location, encoding))
        return results

    def set_scale_factor(self, factor: float) -> None:
        """Set the scale factor for detection."""
        self._scale_factor = max(0.1, min(1.0, factor))

    def set_model(self, model: str) -> None:
        """Set the detection model."""
        if model in {"hog", "cnn"}:
            self._model = model
