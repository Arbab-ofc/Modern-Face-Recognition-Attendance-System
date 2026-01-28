"""Utility helpers for the web backend."""
from __future__ import annotations

import io
import pickle
import re
from datetime import datetime
from typing import Tuple

import cv2
import numpy as np
from bson import Binary
from PIL import Image


def numpy_to_binary(array: np.ndarray) -> Binary:
    """Convert numpy array to BSON Binary for MongoDB storage."""
    serialized = pickle.dumps(array, protocol=pickle.HIGHEST_PROTOCOL)
    return Binary(serialized)


def binary_to_numpy(binary_data: Binary) -> np.ndarray:
    """Convert BSON Binary back to numpy array."""
    return pickle.loads(binary_data)


def image_bytes_to_bgr(image_bytes: bytes) -> np.ndarray:
    """Convert raw image bytes to an OpenCV BGR image."""
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    np_image = np.array(image)
    return cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR)


def get_current_date() -> str:
    """Return current date in YYYY-MM-DD format."""
    return datetime.now().strftime("%Y-%m-%d")


def get_current_time() -> str:
    """Return current time in HH:MM:SS format."""
    return datetime.now().strftime("%H:%M:%S")


def validate_student_id(student_id: str) -> Tuple[bool, str]:
    """Validate student ID format and length."""
    if not student_id or not student_id.strip():
        return False, "Student ID is required."

    cleaned = student_id.strip()
    if not 3 <= len(cleaned) <= 20:
        return False, "Student ID must be between 3 and 20 characters."

    if not re.fullmatch(r"[A-Za-z0-9_-]+", cleaned):
        return False, "Student ID may contain only letters, numbers, hyphens, and underscores."

    return True, ""


def validate_name(name: str) -> Tuple[bool, str]:
    """Validate student name format and length."""
    if not name or not name.strip():
        return False, "Name is required."

    cleaned = name.strip()
    if not 2 <= len(cleaned) <= 100:
        return False, "Name must be between 2 and 100 characters."

    if not re.fullmatch(r"[A-Za-z\-' ]+", cleaned):
        return False, "Name may contain only letters, spaces, hyphens, and apostrophes."

    return True, ""
