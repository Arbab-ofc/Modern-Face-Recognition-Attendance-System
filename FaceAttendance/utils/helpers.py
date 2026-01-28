"""Helper utilities for image processing, validation, and formatting."""
from __future__ import annotations

import re
import pickle
from datetime import datetime
from typing import Tuple

import cv2
import numpy as np
from bson import Binary
from PyQt6.QtGui import QImage


def numpy_to_binary(array: np.ndarray) -> Binary:
    """Convert numpy array to BSON Binary for MongoDB storage."""
    serialized = pickle.dumps(array, protocol=pickle.HIGHEST_PROTOCOL)
    return Binary(serialized)


def binary_to_numpy(binary_data: Binary) -> np.ndarray:
    """Convert BSON Binary back to numpy array."""
    return pickle.loads(binary_data)


def opencv_to_qimage(cv_img: np.ndarray) -> QImage:
    """Convert an OpenCV image (BGR or grayscale) to QImage."""
    if cv_img is None:
        return QImage()

    if len(cv_img.shape) == 2:
        height, width = cv_img.shape
        bytes_per_line = width
        return QImage(cv_img.data, width, height, bytes_per_line, QImage.Format.Format_Grayscale8).copy()

    rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    height, width, channels = rgb_image.shape
    bytes_per_line = channels * width
    return QImage(
        rgb_image.data,
        width,
        height,
        bytes_per_line,
        QImage.Format.Format_RGB888,
    ).copy()


def resize_frame_maintain_aspect(
    frame: np.ndarray, target_width: int, target_height: int
) -> np.ndarray:
    """Resize a frame while maintaining aspect ratio."""
    if frame is None:
        return frame

    height, width = frame.shape[:2]
    if width == 0 or height == 0:
        return frame

    target_ratio = target_width / target_height
    current_ratio = width / height

    if current_ratio > target_ratio:
        new_width = target_width
        new_height = int(target_width / current_ratio)
    else:
        new_height = target_height
        new_width = int(target_height * current_ratio)

    return cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)


def draw_face_box(
    frame: np.ndarray,
    location: Tuple[int, int, int, int],
    name: str,
    color: Tuple[int, int, int],
    thickness: int,
) -> np.ndarray:
    """Draw a modern face box with label and corner accents."""
    if frame is None:
        return frame

    top, right, bottom, left = location
    cv2.rectangle(frame, (left, top), (right, bottom), color, thickness)

    corner_length = max(12, int((right - left) * 0.15))
    cv2.line(frame, (left, top), (left + corner_length, top), color, thickness)
    cv2.line(frame, (left, top), (left, top + corner_length), color, thickness)
    cv2.line(frame, (right, top), (right - corner_length, top), color, thickness)
    cv2.line(frame, (right, top), (right, top + corner_length), color, thickness)
    cv2.line(frame, (left, bottom), (left + corner_length, bottom), color, thickness)
    cv2.line(frame, (left, bottom), (left, bottom - corner_length), color, thickness)
    cv2.line(frame, (right, bottom), (right - corner_length, bottom), color, thickness)
    cv2.line(frame, (right, bottom), (right, bottom - corner_length), color, thickness)

    label_padding = 8
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.6
    text_size, baseline = cv2.getTextSize(name, font, font_scale, 1)
    label_height = text_size[1] + baseline + label_padding * 2
    label_width = text_size[0] + label_padding * 2

    label_x1 = max(0, left)
    label_y1 = min(frame.shape[0] - label_height, bottom + 6)
    label_x2 = min(frame.shape[1], label_x1 + label_width)
    label_y2 = label_y1 + label_height

    overlay = frame.copy()
    cv2.rectangle(overlay, (label_x1, label_y1), (label_x2, label_y2), color, -1)
    cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)

    text_x = label_x1 + label_padding
    text_y = label_y2 - label_padding - baseline
    cv2.putText(frame, name, (text_x, text_y), font, font_scale, (255, 255, 255), 1, cv2.LINE_AA)

    return frame


def get_current_date() -> str:
    """Return current date in YYYY-MM-DD format."""
    return datetime.now().strftime("%Y-%m-%d")


def get_current_time() -> str:
    """Return current time in HH:MM:SS format."""
    return datetime.now().strftime("%H:%M:%S")


def get_display_date() -> str:
    """Return current date in Month DD, YYYY format."""
    return datetime.now().strftime("%B %d, %Y")


def get_display_time() -> str:
    """Return current time in HH:MM AM/PM format."""
    return datetime.now().strftime("%I:%M %p")


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
