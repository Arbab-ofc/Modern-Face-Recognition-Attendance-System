"""UI package exports."""
from ui.main_window import MainWindow
from ui.dashboard import DashboardView
from ui.register_view import RegisterView
from ui.attendance_view import AttendanceView
from ui.records_view import RecordsView
from ui.components import (
    StatusIndicator,
    IconButton,
    StatCard,
    CameraPreview,
    NavigationButton,
    SearchBar,
    DateRangePicker,
    LoadingOverlay,
    ConfirmDialog,
    NotificationToast,
    DataTable,
)

__all__ = [
    "MainWindow",
    "DashboardView",
    "RegisterView",
    "AttendanceView",
    "RecordsView",
    "StatusIndicator",
    "IconButton",
    "StatCard",
    "CameraPreview",
    "NavigationButton",
    "SearchBar",
    "DateRangePicker",
    "LoadingOverlay",
    "ConfirmDialog",
    "NotificationToast",
    "DataTable",
]
