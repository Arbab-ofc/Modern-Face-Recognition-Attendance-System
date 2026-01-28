"""Main window with navigation and view management."""
from __future__ import annotations

from typing import Dict

import qtawesome as qta
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from database.mongo_service import get_db_service
from ui.attendance_view import AttendanceView
from ui.components import NavigationButton, StatusIndicator
from ui.dashboard import DashboardView
from ui.records_view import RecordsView
from ui.register_view import RegisterView
from utils.constants import APP_NAME, APP_VERSION, COLORS, ICONS, UI_DIMENSIONS
from utils.helpers import get_display_date, get_display_time


class MainWindow(QMainWindow):
    """Primary application window with sidebar navigation."""

    def __init__(self) -> None:
        super().__init__()
        self._db_service = get_db_service()
        self._sidebar = QFrame()
        self._content_stack = QStackedWidget()
        self._header = QFrame()
        self._footer = QFrame()
        self._nav_buttons: Dict[str, NavigationButton] = {}
        self._views: Dict[str, QWidget] = {}
        self._status_timer = QTimer(self)
        self._status_timer.setInterval(1000)
        self._status_timer.timeout.connect(self._update_status)

        self._initialize_database()
        self._setup_ui()
        self._load_stylesheet()
        self._status_timer.start()

    def _initialize_database(self) -> None:
        self._db_connected = self._db_service.connect()

    def _setup_ui(self) -> None:
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(UI_DIMENSIONS.MIN_WINDOW_WIDTH, UI_DIMENSIONS.MIN_WINDOW_HEIGHT)
        self.resize(UI_DIMENSIONS.DEFAULT_WINDOW_WIDTH, UI_DIMENSIONS.DEFAULT_WINDOW_HEIGHT)
        self.setWindowIcon(QIcon(qta.icon(ICONS.DASHBOARD).pixmap(32, 32)))

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self._create_sidebar()
        content_container = QVBoxLayout()
        content_container.setContentsMargins(0, 0, 0, 0)
        content_container.setSpacing(0)

        self._create_header()
        self._create_content_area()
        self._create_footer()

        content_container.addWidget(self._header)
        content_container.addWidget(self._content_stack, 1)
        content_container.addWidget(self._footer)

        main_layout.addWidget(self._sidebar)
        main_layout.addLayout(content_container, 1)

    def _create_sidebar(self) -> None:
        self._sidebar.setProperty("class", "sidebar")
        self._sidebar.setFixedWidth(UI_DIMENSIONS.SIDEBAR_WIDTH)
        layout = QVBoxLayout(self._sidebar)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        logo = QLabel(APP_NAME)
        logo.setStyleSheet("font-weight: 700; color: %s;" % COLORS.TEXT_PRIMARY)
        layout.addWidget(logo)

        self._nav_buttons["dashboard"] = NavigationButton("Dashboard", ICONS.DASHBOARD)
        self._nav_buttons["register"] = NavigationButton("Register", ICONS.REGISTER)
        self._nav_buttons["attendance"] = NavigationButton("Attendance", ICONS.ATTENDANCE)
        self._nav_buttons["records"] = NavigationButton("Records", ICONS.RECORDS)

        for name, button in self._nav_buttons.items():
            layout.addWidget(button)
            button.clicked.connect(lambda _, n=name: self._switch_view(n))

        layout.addStretch()
        settings_btn = NavigationButton("Settings", ICONS.SETTINGS)
        layout.addWidget(settings_btn)

    def _create_header(self) -> None:
        self._header.setProperty("class", "header")
        self._header.setFixedHeight(UI_DIMENSIONS.HEADER_HEIGHT)
        layout = QHBoxLayout(self._header)
        layout.setContentsMargins(20, 0, 20, 0)

        title = QLabel(APP_NAME)
        title.setProperty("class", "subtitle")

        self._db_status = StatusIndicator(
            "Database", ICONS.DATABASE, COLORS.TEXT_SECONDARY
        )

        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(self._db_status)

    def _create_content_area(self) -> None:
        self._views["dashboard"] = DashboardView()
        self._views["register"] = RegisterView()
        self._views["attendance"] = AttendanceView()
        self._views["records"] = RecordsView()

        self._views["dashboard"].navigate_to_register.connect(
            lambda: self._switch_view("register")
        )
        self._views["dashboard"].navigate_to_attendance.connect(
            lambda: self._switch_view("attendance")
        )
        self._views["dashboard"].navigate_to_records.connect(
            lambda: self._switch_view("records")
        )

        for view in self._views.values():
            self._content_stack.addWidget(view)

        self._switch_view("dashboard")

    def _create_footer(self) -> None:
        self._footer.setProperty("class", "footer")
        self._footer.setFixedHeight(UI_DIMENSIONS.FOOTER_HEIGHT)
        layout = QHBoxLayout(self._footer)
        layout.setContentsMargins(20, 0, 20, 0)

        self._camera_status = StatusIndicator(
            "Camera", ICONS.CAMERA_OFF, COLORS.WARNING
        )
        self._date_label = QLabel(get_display_date())
        self._time_label = QLabel(get_display_time())
        version_label = QLabel(f"v{APP_VERSION}")

        layout.addWidget(self._camera_status)
        layout.addStretch()
        layout.addWidget(self._date_label)
        layout.addWidget(self._time_label)
        layout.addStretch()
        layout.addWidget(version_label)

    def _switch_view(self, view_name: str) -> None:
        if view_name not in self._views:
            return

        for name, button in self._nav_buttons.items():
            button.setChecked(name == view_name)

        self._content_stack.setCurrentWidget(self._views[view_name])

    def _update_status(self) -> None:
        self._date_label.setText(get_display_date())
        self._time_label.setText(get_display_time())

        if self._db_service.is_connected():
            self._db_status.update_status("Database", ICONS.CONNECTED, COLORS.SUCCESS)
        else:
            self._db_status.update_status("Database", ICONS.DISCONNECTED, COLORS.ERROR)

    def _load_stylesheet(self) -> None:
        try:
            with open("FaceAttendance/ui/styles.qss", "r", encoding="utf-8") as file:
                self.setStyleSheet(file.read())
        except OSError:
            pass

    def closeEvent(self, event) -> None:  # type: ignore[override]
        try:
            self._db_service.disconnect()
        finally:
            event.accept()
