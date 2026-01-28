"""Records view for attendance history and filtering."""
from __future__ import annotations

import csv
from typing import List

from PyQt6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QTableWidgetItem,
)

from database.mongo_service import get_db_service
from models.attendance import AttendanceFilter, AttendanceRecord, AttendanceStatus
from ui.components import DataTable, DateRangePicker, IconButton, NotificationToast, SearchBar
from utils.constants import ICONS
from utils.helpers import get_current_date


class RecordsView(QWidget):
    """Attendance records view with filtering and export."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._db_service = get_db_service()
        self._records_table = DataTable()
        self._current_filter = AttendanceFilter()
        self._current_records: List[AttendanceRecord] = []

        self._setup_ui()
        self._load_initial_data()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        layout.addWidget(self._create_filter_section())
        layout.addWidget(self._create_table_section())
        layout.addWidget(self._create_footer_section())

    def _create_filter_section(self) -> QWidget:
        container = QFrame()
        container.setProperty("class", "card")
        layout = QHBoxLayout(container)
        layout.setSpacing(12)

        self._date_picker = DateRangePicker()
        self._search_bar = SearchBar("Search by Student ID")
        self._status_filter = QComboBox()
        self._status_filter.addItems(["All", "Present", "Late", "Absent", "Excused"])

        apply_btn = QPushButton("Apply")
        apply_btn.setProperty("class", "btn-primary")
        apply_btn.clicked.connect(self._apply_filters)

        clear_btn = QPushButton("Clear")
        clear_btn.setProperty("class", "btn-secondary")
        clear_btn.clicked.connect(self._clear_filters)

        layout.addWidget(self._date_picker)
        layout.addWidget(self._search_bar)
        layout.addWidget(self._status_filter)
        layout.addWidget(apply_btn)
        layout.addWidget(clear_btn)
        return container

    def _create_table_section(self) -> QWidget:
        container = QFrame()
        container.setProperty("class", "card")
        layout = QVBoxLayout(container)
        layout.setSpacing(8)

        self._records_table.setColumnCount(5)
        self._records_table.setHorizontalHeaderLabels(
            ["Date", "Time", "Student ID", "Name", "Status"]
        )

        layout.addWidget(self._records_table)
        return container

    def _create_footer_section(self) -> QWidget:
        container = QFrame()
        container.setProperty("class", "card")
        layout = QHBoxLayout(container)
        layout.setSpacing(12)

        self._record_count_label = QLabel("0 records")
        self._export_button = IconButton(ICONS.EXPORT, "Export")
        self._export_button.clicked.connect(self._export_records)

        layout.addWidget(self._record_count_label)
        layout.addStretch()
        layout.addWidget(self._export_button)
        return container

    def _load_initial_data(self) -> None:
        self._current_records = self._db_service.get_attendance_by_date(get_current_date())
        self._populate_table(self._current_records)

    def _apply_filters(self) -> None:
        self._current_filter.clear()
        start_date = self._date_picker.start_date.date().toString("yyyy-MM-dd")
        end_date = self._date_picker.end_date.date().toString("yyyy-MM-dd")
        if start_date and end_date:
            self._current_filter.by_date_range(start_date, end_date)

        search_text = self._search_bar.text().strip()
        if search_text:
            self._current_filter.by_student(search_text)

        status_text = self._status_filter.currentText().lower()
        if status_text != "all":
            self._current_filter.by_status(AttendanceStatus(status_text))

        self._current_records = self._db_service.get_attendance_by_filter(self._current_filter)
        self._populate_table(self._current_records)

    def _clear_filters(self) -> None:
        self._search_bar.clear()
        self._status_filter.setCurrentIndex(0)
        self._current_filter.clear()
        self._load_initial_data()

    def _populate_table(self, records: List[AttendanceRecord]) -> None:
        self._records_table.setRowCount(0)
        if not records:
            self._records_table.set_empty_message("No records found.")
            self._record_count_label.setText("0 records")
            return

        self._records_table.setRowCount(len(records))
        for row, record in enumerate(records):
            self._records_table.setItem(row, 0, QTableWidgetItem(record.date))
            self._records_table.setItem(row, 1, QTableWidgetItem(record.time))
            self._records_table.setItem(row, 2, QTableWidgetItem(record.student_id))
            self._records_table.setItem(row, 3, QTableWidgetItem(record.name))
            self._records_table.setItem(row, 4, QTableWidgetItem(record.status.value))

        self._record_count_label.setText(f"{len(records)} records")

    def _export_records(self) -> None:
        if not self._current_records:
            NotificationToast.show_toast(self, "No records to export.", "warning")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Attendance", "attendance.csv", "CSV Files (*.csv)"
        )
        if not filename:
            return

        try:
            with open(filename, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Date", "Time", "Student ID", "Name", "Status"])
                for record in self._current_records:
                    writer.writerow(
                        [record.date, record.time, record.student_id, record.name, record.status.value]
                    )
            NotificationToast.show_toast(self, "Records exported successfully.", "success")
        except OSError:
            NotificationToast.show_toast(self, "Failed to export records.", "error")

    def showEvent(self, event) -> None:  # type: ignore[override]
        self._load_initial_data()
        super().showEvent(event)
