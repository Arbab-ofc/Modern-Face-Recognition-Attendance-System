"""Student registration view with face capture."""
from __future__ import annotations

from typing import Dict, Optional, Tuple

import numpy as np
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from database.mongo_service import get_db_service
from models.student import Student
from ui.components import CameraPreview, IconButton, NotificationToast, StatusIndicator
from utils.constants import COLORS, ICONS, MESSAGES
from utils.helpers import validate_name, validate_student_id
from vision.camera import CameraManager
from vision.face_detector import FaceDetector


class RegisterView(QWidget):
    """Register new students with face capture."""

    student_registered = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._db_service = get_db_service()
        self._camera_manager = CameraManager()
        self._face_detector = FaceDetector()

        self._camera_preview = CameraPreview()
        self._form_fields: Dict[str, QLineEdit] = {}
        self._captured_encoding: Optional[np.ndarray] = None
        self._capture_button = IconButton(ICONS.CAPTURE, "Capture")
        self._save_button = IconButton(ICONS.SAVE, "Save")
        self._status_label = QLabel("No face captured")
        self._face_status = StatusIndicator("No face", ICONS.WARNING, COLORS.WARNING)

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)

        layout.addWidget(self._create_camera_section(), 3)
        layout.addWidget(self._create_form_section(), 2)

    def _create_camera_section(self) -> QWidget:
        container = QFrame()
        container.setProperty("class", "card")
        layout = QVBoxLayout(container)
        layout.setSpacing(12)

        title = QLabel("Face Capture")
        title.setProperty("class", "subtitle")

        instructions = QLabel("Align the face within the frame and capture.")
        instructions.setProperty("class", "label")

        control_row = QHBoxLayout()
        control_row.addWidget(self._capture_button)
        control_row.addStretch()

        layout.addWidget(title)
        layout.addWidget(self._camera_preview, 1)
        layout.addLayout(control_row)
        layout.addWidget(instructions)

        return container

    def _create_form_section(self) -> QWidget:
        container = QFrame()
        container.setProperty("class", "card")
        layout = QVBoxLayout(container)
        layout.setSpacing(12)

        title = QLabel("Student Information")
        title.setProperty("class", "subtitle")

        student_id_input = QLineEdit()
        student_id_input.setPlaceholderText("Student ID")
        name_input = QLineEdit()
        name_input.setPlaceholderText("Full Name")

        self._form_fields["student_id"] = student_id_input
        self._form_fields["name"] = name_input

        self._save_button.setEnabled(False)
        clear_button = QPushButton("Clear")
        clear_button.setProperty("class", "btn-secondary")
        clear_button.clicked.connect(self._clear_form)

        layout.addWidget(title)
        layout.addWidget(student_id_input)
        layout.addWidget(name_input)
        layout.addWidget(self._face_status)
        layout.addWidget(self._status_label)
        layout.addWidget(self._save_button)
        layout.addWidget(clear_button)
        layout.addStretch()

        return container

    def _connect_signals(self) -> None:
        self._camera_manager.frame_ready.connect(self._update_preview)
        self._capture_button.clicked.connect(self._capture_face)
        self._save_button.clicked.connect(self._save_student)

    def _start_camera(self) -> None:
        self._camera_manager.start()

    def _stop_camera(self) -> None:
        self._camera_manager.stop()
        self._camera_preview.show_placeholder()

    def _update_preview(self, frame) -> None:
        locations = self._face_detector.detect_faces(frame, scale=True)
        names = ["Detected"] * len(locations)
        self._camera_preview.update_frame(frame, locations, names)

        if locations:
            self._face_status.update_status("Face detected", ICONS.SUCCESS, COLORS.SUCCESS)
        else:
            self._face_status.update_status("No face", ICONS.WARNING, COLORS.WARNING)

    def _capture_face(self) -> None:
        frame = self._camera_manager.get_current_frame()
        if frame is None:
            NotificationToast.show_toast(self, MESSAGES.CAMERA_ERROR, "error")
            return

        locations = self._face_detector.detect_faces(frame, scale=False)
        if not locations:
            NotificationToast.show_toast(self, MESSAGES.FACE_NOT_DETECTED, "warning")
            return

        encoding = self._face_detector.get_face_encoding(frame, locations[0])
        if encoding is None:
            NotificationToast.show_toast(self, MESSAGES.RECOGNITION_FAILED, "error")
            return

        self._captured_encoding = encoding
        self._status_label.setText("Face captured successfully")
        self._save_button.setEnabled(True)
        self._face_status.update_status("Captured", ICONS.SUCCESS, COLORS.SUCCESS)

    def _save_student(self) -> None:
        valid, message = self._validate_form()
        if not valid:
            NotificationToast.show_toast(self, message, "warning")
            return

        student = Student(
            student_id=self._form_fields["student_id"].text().strip(),
            name=self._form_fields["name"].text().strip(),
            face_encoding=self._captured_encoding,
        )
        success, response = self._db_service.add_student(student)
        if success:
            NotificationToast.show_toast(self, response, "success")
            self.student_registered.emit(student.student_id)
            self._clear_form()
        else:
            NotificationToast.show_toast(self, response, "error")

    def _validate_form(self) -> Tuple[bool, str]:
        student_id = self._form_fields["student_id"].text()
        name = self._form_fields["name"].text()
        valid_id, id_message = validate_student_id(student_id)
        if not valid_id:
            return False, id_message

        valid_name, name_message = validate_name(name)
        if not valid_name:
            return False, name_message

        if self._captured_encoding is None:
            return False, "Face capture is required."

        return True, ""

    def _clear_form(self) -> None:
        for field in self._form_fields.values():
            field.clear()
        self._captured_encoding = None
        self._save_button.setEnabled(False)
        self._status_label.setText("No face captured")
        self._face_status.update_status("No face", ICONS.WARNING, COLORS.WARNING)

    def showEvent(self, event) -> None:  # type: ignore[override]
        self._start_camera()
        super().showEvent(event)

    def hideEvent(self, event) -> None:  # type: ignore[override]
        self._stop_camera()
        super().hideEvent(event)
