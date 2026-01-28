"""Camera manager using QTimer for frame capture."""
from __future__ import annotations

from typing import Optional, Tuple

import cv2
import numpy as np
from PyQt6.QtCore import QObject, QMutex, QMutexLocker, QTimer, pyqtSignal

from utils.constants import CAMERA


class CameraManager(QObject):
    """Camera manager with thread-safe frame access and Qt signals."""

    frame_ready = pyqtSignal(np.ndarray)
    camera_error = pyqtSignal(str)
    camera_started = pyqtSignal()
    camera_stopped = pyqtSignal()

    def __init__(self, camera_index: Optional[int] = None) -> None:
        super().__init__()
        self._camera_index = (
            CAMERA.DEFAULT_CAMERA_INDEX if camera_index is None else camera_index
        )
        self._capture: Optional[cv2.VideoCapture] = None
        self._timer: Optional[QTimer] = None
        self._is_running = False
        self._mutex = QMutex()
        self._current_frame: Optional[np.ndarray] = None

    def start(self) -> bool:
        """Start the camera capture loop."""
        with QMutexLocker(self._mutex):
            if self._is_running:
                return True

            self._capture = cv2.VideoCapture(self._camera_index)
            if not self._capture.isOpened():
                self._capture.release()
                self._capture = None
                self.camera_error.emit("Failed to open camera.")
                return False

            self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA.FRAME_WIDTH)
            self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA.FRAME_HEIGHT)
            self._capture.set(cv2.CAP_PROP_FPS, CAMERA.FPS)

            self._timer = QTimer(self)
            self._timer.timeout.connect(self._capture_frame)
            self._timer.start(CAMERA.CAPTURE_INTERVAL_MS)

            self._is_running = True
            self.camera_started.emit()
            return True

    def stop(self) -> None:
        """Stop the camera capture loop."""
        with QMutexLocker(self._mutex):
            if self._timer is not None:
                self._timer.stop()
                self._timer.deleteLater()
                self._timer = None

            if self._capture is not None:
                self._capture.release()
                self._capture = None

            self._current_frame = None
            if self._is_running:
                self._is_running = False
                self.camera_stopped.emit()

    def _capture_frame(self) -> None:
        """Capture a frame from the camera."""
        if self._capture is None:
            return

        ret, frame = self._capture.read()
        if not ret:
            self.camera_error.emit("Failed to read frame from camera.")
            return

        frame = cv2.flip(frame, 1)
        with QMutexLocker(self._mutex):
            self._current_frame = frame.copy()
        self.frame_ready.emit(frame)

    def get_current_frame(self) -> Optional[np.ndarray]:
        """Return the latest captured frame."""
        with QMutexLocker(self._mutex):
            if self._current_frame is None:
                return None
            return self._current_frame.copy()

    def is_running(self) -> bool:
        """Return whether the camera is running."""
        return self._is_running

    def get_frame_size(self) -> Tuple[int, int]:
        """Return configured frame size."""
        return CAMERA.FRAME_WIDTH, CAMERA.FRAME_HEIGHT

    def set_camera_index(self, index: int) -> None:
        """Switch the camera index, restarting if needed."""
        was_running = self._is_running
        if was_running:
            self.stop()
        self._camera_index = index
        if was_running:
            self.start()

    def __del__(self) -> None:
        """Ensure camera resources are released."""
        try:
            self.stop()
        except Exception:
            pass
