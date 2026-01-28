"""Dashboard view with statistics and recent activity."""
from __future__ import annotations

from typing import Dict

from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from database.mongo_service import get_db_service
from models.attendance import AttendanceSummary
from ui.components import DataTable, StatCard
from utils.constants import COLORS, ICONS
from utils.helpers import get_current_date, get_display_date


class DashboardView(QWidget):
    """Dashboard view showing high-level statistics."""

    navigate_to_register = pyqtSignal()
    navigate_to_attendance = pyqtSignal()
    navigate_to_records = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._db_service = get_db_service()
        self._stat_cards: Dict[str, StatCard] = {}
        self._recent_table = DataTable()
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setInterval(60000)
        self._refresh_timer.timeout.connect(self.refresh_data)

        self._setup_ui()
        self._refresh_timer.start()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        layout.addWidget(self._create_welcome_section())
        layout.addLayout(self._create_stats_section())
        layout.addWidget(self._create_quick_actions())
        layout.addWidget(self._create_recent_activity())

    def _create_welcome_section(self) -> QWidget:
        container = QFrame()
        container.setProperty("class", "card")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(4)

        title = QLabel("Welcome Back")
        title.setProperty("class", "title")
        date_label = QLabel(get_display_date())
        date_label.setProperty("class", "subtitle")
        subtitle = QLabel("System status is stable and monitoring attendance.")
        subtitle.setProperty("class", "label")

        layout.addWidget(title)
        layout.addWidget(date_label)
        layout.addWidget(subtitle)
        return container

    def _create_stats_section(self) -> QGridLayout:
        grid = QGridLayout()
        grid.setSpacing(16)

        self._stat_cards["total"] = StatCard(
            "Total Students", "0", ICONS.USERS, COLORS.PRIMARY
        )
        self._stat_cards["present"] = StatCard(
            "Present Today", "0", ICONS.SUCCESS, COLORS.SUCCESS
        )
        self._stat_cards["rate"] = StatCard(
            "Attendance Rate", "0%", ICONS.INFO, COLORS.INFO
        )
        self._stat_cards["absent"] = StatCard(
            "Pending", "0", ICONS.CLOCK, COLORS.WARNING
        )

        grid.addWidget(self._stat_cards["total"], 0, 0)
        grid.addWidget(self._stat_cards["present"], 0, 1)
        grid.addWidget(self._stat_cards["rate"], 1, 0)
        grid.addWidget(self._stat_cards["absent"], 1, 1)
        return grid

    def _create_quick_actions(self) -> QWidget:
        container = QFrame()
        container.setProperty("class", "card")
        layout = QHBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        register_btn = QPushButton("Register New Student")
        register_btn.setProperty("class", "btn-primary")
        register_btn.clicked.connect(self.navigate_to_register.emit)

        attendance_btn = QPushButton("Take Attendance")
        attendance_btn.setProperty("class", "btn-secondary")
        attendance_btn.clicked.connect(self.navigate_to_attendance.emit)

        records_btn = QPushButton("View Records")
        records_btn.setProperty("class", "btn-secondary")
        records_btn.clicked.connect(self.navigate_to_records.emit)

        layout.addWidget(register_btn)
        layout.addWidget(attendance_btn)
        layout.addWidget(records_btn)
        layout.addStretch()
        return container

    def _create_recent_activity(self) -> QWidget:
        container = QFrame()
        container.setProperty("class", "card")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("Recent Activity")
        title.setProperty("class", "subtitle")

        self._recent_table.setColumnCount(4)
        self._recent_table.setHorizontalHeaderLabels(
            ["Name", "Student ID", "Time", "Status"]
        )
        self._recent_table.setAlternatingRowColors(True)

        layout.addWidget(title)
        layout.addWidget(self._recent_table)
        return container

    def refresh_data(self) -> None:
        """Refresh dashboard statistics and recent activity."""
        total_students = self._db_service.get_student_count()
        today_records = self._db_service.get_attendance_by_date(get_current_date())
        summary = AttendanceSummary.calculate(total_students, today_records)

        self._stat_cards["total"].set_value(str(total_students))
        self._stat_cards["present"].set_value(str(summary.present_today))
        self._stat_cards["rate"].set_value(f"{summary.attendance_rate:.1f}%")
        self._stat_cards["absent"].set_value(str(summary.absent_today))

        self._populate_recent_activity(today_records[:10])

    def _populate_recent_activity(self, records) -> None:
        self._recent_table.setRowCount(0)
        if not records:
            self._recent_table.setRowCount(0)
            self._recent_table.set_empty_message("No attendance records yet.")
            return

        self._recent_table.setRowCount(len(records))
        for row, record in enumerate(records):
            self._recent_table.setItem(row, 0, QTableWidgetItem(record.name))
            self._recent_table.setItem(row, 1, QTableWidgetItem(record.student_id))
            self._recent_table.setItem(row, 2, QTableWidgetItem(record.time))
            self._recent_table.setItem(row, 3, QTableWidgetItem(record.status.value))

    def showEvent(self, event) -> None:  # type: ignore[override]
        self.refresh_data()
        super().showEvent(event)
