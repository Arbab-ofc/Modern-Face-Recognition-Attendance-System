"""Reusable UI components for the application."""
from __future__ import annotations

from typing import Dict, Optional, Tuple

import qtawesome as qta
from PyQt6.QtCore import (
    QEasingCurve,
    QObject,
    QPoint,
    QPropertyAnimation,
    QTimer,
    Qt,
    pyqtSignal,
)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtWidgets import (
    QDateEdit,
    QDialog,
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from utils.constants import COLORS, ICONS
from utils.helpers import draw_face_box, opencv_to_qimage, resize_frame_maintain_aspect


class StatusIndicator(QWidget):
    """Status indicator with icon, label, and pulse animation."""

    def __init__(self, text: str, icon_name: str, color: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._icon_label = QLabel()
        self._text_label = QLabel(text)
        self._color = color

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        icon = qta.icon(icon_name, color=color)
        self._icon_label.setPixmap(icon.pixmap(14, 14))
        self._icon_label.setFixedSize(16, 16)

        self._text_label.setStyleSheet("color: %s;" % COLORS.TEXT_SECONDARY)

        layout.addWidget(self._icon_label)
        layout.addWidget(self._text_label)

        self._apply_pulse_animation()

    def _apply_pulse_animation(self) -> None:
        effect = QGraphicsOpacityEffect(self._icon_label)
        self._icon_label.setGraphicsEffect(effect)

        animation = QPropertyAnimation(effect, b"opacity", self)
        animation.setStartValue(0.4)
        animation.setEndValue(1.0)
        animation.setDuration(1200)
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        animation.setLoopCount(-1)
        animation.start()
        self._pulse_animation = animation

    def update_status(self, text: str, icon_name: str, color: str) -> None:
        """Update the indicator text and icon."""
        self._text_label.setText(text)
        icon = qta.icon(icon_name, color=color)
        self._icon_label.setPixmap(icon.pixmap(14, 14))
        self._color = color


class IconButton(QPushButton):
    """Icon-only button with hover animation."""

    def __init__(
        self,
        icon_name: str,
        tooltip: Optional[str] = None,
        size: int = 20,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._base_size = size
        self._icon_name = icon_name
        self._icon_color = COLORS.TEXT_PRIMARY
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(44, 44)
        self.setProperty("class", "btn-icon")

        self._set_icon(size)
        if tooltip:
            self.setToolTip(tooltip)

        self._hover_animation = QPropertyAnimation(self, b"iconSize", self)
        self._hover_animation.setDuration(150)
        self._hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def _set_icon(self, size: int) -> None:
        icon = qta.icon(self._icon_name, color=self._icon_color)
        self.setIcon(icon)
        self.setIconSize(icon.actualSize(QPixmap(size, size).size()))

    def enterEvent(self, event) -> None:  # type: ignore[override]
        self._hover_animation.stop()
        self._hover_animation.setStartValue(self.iconSize())
        self._hover_animation.setEndValue(QPixmap(self._base_size + 4, self._base_size + 4).size())
        self._hover_animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:  # type: ignore[override]
        self._hover_animation.stop()
        self._hover_animation.setStartValue(self.iconSize())
        self._hover_animation.setEndValue(QPixmap(self._base_size, self._base_size).size())
        self._hover_animation.start()
        super().leaveEvent(event)


class StatCard(QFrame):
    """Statistic card used on the dashboard."""

    def __init__(
        self,
        title: str,
        value: str,
        icon_name: str,
        accent_color: str,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setProperty("class", "card")
        self.setProperty("depth", True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)

        self._title_label = QLabel(title)
        self._title_label.setStyleSheet("color: %s;" % COLORS.TEXT_SECONDARY)
        self._value_label = QLabel(value)
        self._value_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))

        text_layout.addWidget(self._title_label)
        text_layout.addWidget(self._value_label)

        icon_label = QLabel()
        icon = qta.icon(icon_name, color=accent_color)
        icon_label.setPixmap(icon.pixmap(32, 32))
        icon_label.setFixedSize(40, 40)

        layout.addLayout(text_layout)
        layout.addStretch()
        layout.addWidget(icon_label)

        self._accent_color = accent_color
        self._apply_gradient()

    def _apply_gradient(self) -> None:
        self.setStyleSheet(
            "QFrame[depth='true'] {"
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(99,102,241,0.12), stop:1 rgba(30,41,59,1));"
            "border-radius: 20px;"
            "border: 1px solid rgba(255, 255, 255, 0.08);"
            "}"
        )

    def set_value(self, value: str) -> None:
        """Update the displayed value."""
        self._value_label.setText(value)


class CameraPreview(QLabel):
    """Camera preview widget with placeholder support."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setProperty("class", "camera-frame")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._last_frame = None

    def show_placeholder(self, text: str = "Camera inactive") -> None:
        """Show a placeholder message."""
        self.setText(text)
        self._last_frame = None

    def update_frame(self, frame, face_boxes=None, names=None) -> None:
        """Update preview with an OpenCV frame."""
        if frame is None:
            self.show_placeholder()
            return

        display_frame = frame.copy()
        if face_boxes and names:
            for location, name in zip(face_boxes, names):
                draw_face_box(display_frame, location, name, (99, 102, 241), 2)

        resized = resize_frame_maintain_aspect(
            display_frame, self.width(), self.height()
        )
        qimage = opencv_to_qimage(resized)
        if not qimage.isNull():
            self.setPixmap(QPixmap.fromImage(qimage))
            self._last_frame = resized


class NavigationButton(QPushButton):
    """Sidebar navigation button with icon and text."""

    def __init__(self, text: str, icon_name: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(text, parent)
        self.setProperty("class", "sidebar-item")
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        icon = qta.icon(icon_name, color=COLORS.TEXT_PRIMARY)
        self.setIcon(icon)
        self.setIconSize(QPixmap(18, 18).size())
        self.setStyleSheet("text-align: left; padding-left: 14px;")

        self._press_animation = QPropertyAnimation(self, b"iconSize", self)
        self._press_animation.setDuration(120)
        self._press_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        self._press_animation.stop()
        self._press_animation.setStartValue(self.iconSize())
        self._press_animation.setEndValue(QPixmap(20, 20).size())
        self._press_animation.start()
        super().mousePressEvent(event)


class SearchBar(QLineEdit):
    """Search bar with debounced text changed signal."""

    debounced_text_changed = pyqtSignal(str)

    def __init__(self, placeholder: str = "Search", parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setClearButtonEnabled(True)

        icon = qta.icon(ICONS.SEARCH, color=COLORS.TEXT_MUTED)
        self.addAction(icon, QLineEdit.ActionPosition.LeadingPosition)

        self._debounce_timer = QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(300)
        self.textChanged.connect(self._on_text_changed)
        self._debounce_timer.timeout.connect(self._emit_debounced)

    def _on_text_changed(self) -> None:
        self._debounce_timer.start()

    def _emit_debounced(self) -> None:
        self.debounced_text_changed.emit(self.text())


class DateRangePicker(QWidget):
    """Date range selector with quick buttons."""

    range_changed = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.start_date = QDateEdit()
        self.end_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.end_date.setCalendarPopup(True)

        self.today_btn = QPushButton("Today")
        self.week_btn = QPushButton("This Week")
        self.month_btn = QPushButton("This Month")

        for button in (self.today_btn, self.week_btn, self.month_btn):
            button.setProperty("class", "btn-secondary")

        layout.addWidget(self.start_date)
        layout.addWidget(self.end_date)
        layout.addWidget(self.today_btn)
        layout.addWidget(self.week_btn)
        layout.addWidget(self.month_btn)

        self.start_date.dateChanged.connect(self.range_changed)
        self.end_date.dateChanged.connect(self.range_changed)
        self.today_btn.clicked.connect(self._set_today)
        self.week_btn.clicked.connect(self._set_week)
        self.month_btn.clicked.connect(self._set_month)

    def _set_today(self) -> None:
        today = self.start_date.date().currentDate()
        self.start_date.setDate(today)
        self.end_date.setDate(today)
        self.range_changed.emit()

    def _set_week(self) -> None:
        today = self.start_date.date().currentDate()
        start = today.addDays(-today.dayOfWeek() + 1)
        end = start.addDays(6)
        self.start_date.setDate(start)
        self.end_date.setDate(end)
        self.range_changed.emit()

    def _set_month(self) -> None:
        today = self.start_date.date().currentDate()
        start = today.addDays(-today.day() + 1)
        end = start.addMonths(1).addDays(-1)
        self.start_date.setDate(start)
        self.end_date.setDate(end)
        self.range_changed.emit()


class LoadingOverlay(QWidget):
    """Semi-transparent loading overlay with busy indicator."""

    def __init__(self, message: str = "Loading", parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setStyleSheet("background: rgba(15, 23, 42, 0.6);")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._label = QLabel(message)
        self._label.setStyleSheet("color: %s;" % COLORS.TEXT_PRIMARY)
        self._progress = QProgressBar()
        self._progress.setRange(0, 0)
        self._progress.setFixedWidth(220)

        layout.addWidget(self._label)
        layout.addWidget(self._progress)

    def show_message(self, message: str) -> None:
        self._label.setText(message)
        self.show()


class ConfirmDialog(QDialog):
    """Confirmation dialog with custom styling."""

    def __init__(
        self,
        title: str,
        message: str,
        icon_name: str,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        header = QHBoxLayout()
        icon_label = QLabel()
        icon = qta.icon(icon_name, color=COLORS.TEXT_PRIMARY)
        icon_label.setPixmap(icon.pixmap(24, 24))
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))

        header.addWidget(icon_label)
        header.addWidget(title_label)
        header.addStretch()

        message_label = QLabel(message)
        message_label.setWordWrap(True)

        button_row = QHBoxLayout()
        confirm_btn = QPushButton("Confirm")
        cancel_btn = QPushButton("Cancel")
        confirm_btn.setProperty("class", "btn-primary")
        cancel_btn.setProperty("class", "btn-secondary")

        confirm_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

        button_row.addStretch()
        button_row.addWidget(cancel_btn)
        button_row.addWidget(confirm_btn)

        layout.addLayout(header)
        layout.addWidget(message_label)
        layout.addLayout(button_row)


class NotificationToast(QFrame):
    """Toast notification with auto-hide and queue support."""

    _queue: list = []
    _is_showing = False

    def __init__(
        self,
        message: str,
        icon_name: str,
        color: str,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setProperty("class", "card")
        self.setFixedHeight(52)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(12)

        icon_label = QLabel()
        icon = qta.icon(icon_name, color=color)
        icon_label.setPixmap(icon.pixmap(18, 18))

        text_label = QLabel(message)
        text_label.setStyleSheet("color: %s;" % COLORS.TEXT_PRIMARY)

        layout.addWidget(icon_label)
        layout.addWidget(text_label)

        self._animation = QPropertyAnimation(self, b"windowOpacity", self)
        self._animation.setDuration(200)
        self._animation.setStartValue(0.0)
        self._animation.setEndValue(1.0)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.setInterval(2500)
        self._hide_timer.timeout.connect(self._hide)

    @classmethod
    def show_toast(cls, parent: QWidget, message: str, level: str) -> None:
        """Queue and display toast notifications."""
        icon_map = {
            "success": (ICONS.SUCCESS, COLORS.SUCCESS),
            "error": (ICONS.ERROR, COLORS.ERROR),
            "warning": (ICONS.WARNING, COLORS.WARNING),
            "info": (ICONS.INFO, COLORS.INFO),
        }
        icon_name, color = icon_map.get(level, (ICONS.INFO, COLORS.INFO))
        cls._queue.append((parent, message, icon_name, color))
        if not cls._is_showing:
            cls._show_next()

    @classmethod
    def _show_next(cls) -> None:
        if not cls._queue:
            cls._is_showing = False
            return
        parent, message, icon_name, color = cls._queue.pop(0)
        toast = NotificationToast(message, icon_name, color, parent)
        parent.layout().addWidget(toast)
        cls._is_showing = True
        toast.show()
        toast._animation.start()
        toast._hide_timer.start()
        toast._hide_timer.timeout.connect(cls._show_next)

    def _hide(self) -> None:
        self.hide()
        self.deleteLater()


class DataTable(QTableWidget):
    """Enhanced table widget with empty state and pagination helpers."""

    page_changed = pyqtSignal(int)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
        self._page_size = 10
        self._current_page = 1
        self._total_records = 0

    def set_empty_message(self, message: str) -> None:
        """Display a single-row empty state message."""
        self.clearContents()
        if self.columnCount() == 0:
            self.setColumnCount(1)
        self.setRowCount(1)
        item = QTableWidgetItem(message)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setItem(0, 0, item)
        self.setSpan(0, 0, 1, self.columnCount())

    def set_pagination(self, current_page: int, page_size: int, total_records: int) -> None:
        """Update pagination metadata."""
        self._current_page = current_page
        self._page_size = page_size
        self._total_records = total_records
        self.page_changed.emit(current_page)

    def total_pages(self) -> int:
        """Return total number of pages."""
        if self._page_size == 0:
            return 0
        return max(1, (self._total_records + self._page_size - 1) // self._page_size)
