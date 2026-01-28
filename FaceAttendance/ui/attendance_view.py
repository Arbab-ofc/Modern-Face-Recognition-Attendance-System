"""Attendance view for real-time face recognition."""
from __future__ import annotations

from typing import List, Optional, Set

import numpy as np
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from database.mongo_service import get_db_service
from models.attendance import AttendanceRecord
from ui.components import CameraPreview, NotificationToast, StatusIndicator
from utils.constants import COLORS, ICONS, MESSAGES
from utils.helpers import get_display_date
from vision.camera import CameraManager
from vision.face_detector import FaceDetector
from vision.face_recognizer import FaceRecognizer


class AttendanceView(QWidget):
    """Live attendance recognition view."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._db_service = get_db_service()
        self._camera_manager = CameraManager()
        self._face_detector = FaceDetector()
        self._face_recognizer = FaceRecognizer()
        self._camera_preview = CameraPreview()
        self._attendance_log = QListWidget()
        self._recognition_timer = QTimer(self)
        self._recognition_timer.setInterval(500)
        self._recognition_timer.timeout.connect(self._process_recognition)

        self._marked_today: Set[str] = set()
        self._current_frame: Optional[np.ndarray] = None
        self._is_recognizing = False

        self._setup_ui()
        self._camera_manager.frame_ready.connect(self._on_frame_ready)

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)

        layout.addWidget(self._create_camera_section(), 3)
        layout.addWidget(self._create_attendance_panel(), 2)

    def _create_camera_section(self) -> QWidget:
        container = QFrame()
        container.setProperty("class", "card")
        layout = QVBoxLayout(container)
        layout.setSpacing(12)

        title = QLabel("Live Recognition")
        title.setProperty("class", "subtitle")

        self._camera_status = StatusIndicator("Camera Idle", ICONS.CAMERA_OFF, COLORS.WARNING)
        self._toggle_button = QPushButton("Start Recognition")
        self._toggle_button.setProperty("class", "btn-primary")
        self._toggle_button.clicked.connect(self._toggle_recognition)

        layout.addWidget(title)
        layout.addWidget(self._camera_preview, 1)
        layout.addWidget(self._camera_status)
        layout.addWidget(self._toggle_button)
        return container

    def _create_attendance_panel(self) -> QWidget:
        container = QFrame()
        container.setProperty("class", "card")
        layout = QVBoxLayout(container)
        layout.setSpacing(12)

        title = QLabel("Today's Attendance")
        title.setProperty("class", "subtitle")
        date_label = QLabel(get_display_date())
        date_label.setProperty("class", "label")

        self._count_label = QLabel("Present: 0 / Total: 0")
        self._count_label.setProperty("class", "value")

        clear_btn = QPushButton("Clear Log")
        clear_btn.setProperty("class", "btn-secondary")
        clear_btn.clicked.connect(self._attendance_log.clear)

        layout.addWidget(title)
        layout.addWidget(date_label)
        layout.addWidget(self._count_label)
        layout.addWidget(self._attendance_log, 1)
        layout.addWidget(clear_btn)
        return container

    def _toggle_recognition(self) -> None:
        if self._is_recognizing:
            self._stop_recognition()
        else:
            self._start_recognition()

    def _start_recognition(self) -> None:
        if self._camera_manager.start():
            self._is_recognizing = True
            self._toggle_button.setText("Stop Recognition")
            self._camera_status.update_status("Camera Active", ICONS.CAMERA_ON, COLORS.SUCCESS)
            self._face_recognizer.load_known_faces()
            self._recognition_timer.start()

    def _stop_recognition(self) -> None:
        self._is_recognizing = False
        self._toggle_button.setText("Start Recognition")
        self._camera_status.update_status("Camera Idle", ICONS.CAMERA_OFF, COLORS.WARNING)
        self._recognition_timer.stop()
        self._camera_manager.stop()
        self._camera_preview.show_placeholder()

    def _on_frame_ready(self, frame: np.ndarray) -> None:
        self._current_frame = frame
        self._camera_preview.update_frame(frame)

    def _process_recognition(self) -> None:
        frame = self._current_frame
        if frame is None:
            return

        results = self._face_detector.detect_and_encode(frame)
        if not results:
            return

        locations = [item[0] for item in results]
        encodings = [item[1] for item in results]
        recognized = self._face_recognizer.recognize_faces_in_frame(
            frame, locations, encodings
        )

        names = []
        for result in recognized:
            if result.is_match and result.student_id:
                names.append(result.name)
                if result.student_id not in self._marked_today:
                    self._mark_attendance(result.student_id, result.name)
                    self._marked_today.add(result.student_id)
            else:
                names.append("Unknown")

        self._camera_preview.update_frame(frame, locations, names)
        self._update_stats()

    def _mark_attendance(self, student_id: str, name: str) -> None:
        record = AttendanceRecord.create_present(student_id, name)
        success, message = self._db_service.mark_attendance(record)
        level = "success" if success else "warning"
        NotificationToast.show_toast(self, message, level)
        if success:
            self._add_to_log(name, record.time, record.status.value)

    def _add_to_log(self, name: str, time: str, status: str) -> None:
        item = QListWidgetItem(f"{time} - {name} ({status})")
        self._attendance_log.insertItem(0, item)

    def _refresh_known_faces(self) -> None:
        self._face_recognizer.load_known_faces()

    def _update_stats(self) -> None:
        total_students = self._db_service.get_student_count()
        present_today = self._db_service.get_today_attendance_count()
        self._count_label.setText(f"Present: {present_today} / Total: {total_students}")

    def showEvent(self, event) -> None:  # type: ignore[override]
        self._marked_today.clear()
        self._refresh_known_faces()
        self._start_recognition()
        super().showEvent(event)

    def hideEvent(self, event) -> None:  # type: ignore[override]
        self._stop_recognition()
        super().hideEvent(event)
