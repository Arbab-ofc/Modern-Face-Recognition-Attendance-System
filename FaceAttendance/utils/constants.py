"""Application-wide constants and configuration objects."""
from dataclasses import dataclass


APP_NAME = "Face Recognition Attendance System"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Arbab"


@dataclass(frozen=True)
class DatabaseConfig:
    """MongoDB configuration settings."""

    URI: str
    DATABASE_NAME: str
    STUDENTS_COLLECTION: str
    ATTENDANCE_COLLECTION: str
    CONNECTION_TIMEOUT_MS: int
    SERVER_SELECTION_TIMEOUT_MS: int


DATABASE = DatabaseConfig(
    URI=(
        "mongodb+srv://arbab2201156ec_db_user:jZHzoDglYiXECwKz@"
        "modernfaceattendancesys.vyj17qz.mongodb.net/?appName=ModernFaceAttendanceSystem"
    ),
    DATABASE_NAME="face_attendance",
    STUDENTS_COLLECTION="students",
    ATTENDANCE_COLLECTION="attendance",
    CONNECTION_TIMEOUT_MS=5000,
    SERVER_SELECTION_TIMEOUT_MS=5000,
)


@dataclass(frozen=True)
class CameraConfig:
    """Camera capture configuration."""

    DEFAULT_CAMERA_INDEX: int
    FRAME_WIDTH: int
    FRAME_HEIGHT: int
    FPS: int
    CAPTURE_INTERVAL_MS: int
    RECOGNITION_INTERVAL_MS: int


CAMERA = CameraConfig(
    DEFAULT_CAMERA_INDEX=0,
    FRAME_WIDTH=640,
    FRAME_HEIGHT=480,
    FPS=30,
    CAPTURE_INTERVAL_MS=33,
    RECOGNITION_INTERVAL_MS=500,
)


@dataclass(frozen=True)
class FaceRecognitionConfig:
    """Face recognition configuration."""

    TOLERANCE: float
    MODEL: str
    NUM_JITTERS: int
    ENCODING_SIZE: int
    MIN_FACE_SIZE: int
    SCALE_FACTOR: float


FACE_RECOGNITION = FaceRecognitionConfig(
    TOLERANCE=0.5,
    MODEL="hog",
    NUM_JITTERS=1,
    ENCODING_SIZE=128,
    MIN_FACE_SIZE=50,
    SCALE_FACTOR=0.25,
)


@dataclass(frozen=True)
class UIDimensions:
    """UI sizing and spacing constants."""

    MIN_WINDOW_WIDTH: int
    MIN_WINDOW_HEIGHT: int
    DEFAULT_WINDOW_WIDTH: int
    DEFAULT_WINDOW_HEIGHT: int
    HEADER_HEIGHT: int
    FOOTER_HEIGHT: int
    SIDEBAR_WIDTH: int
    SIDEBAR_COLLAPSED_WIDTH: int
    CONTENT_MARGIN: int
    WIDGET_SPACING: int
    BUTTON_HEIGHT: int
    INPUT_HEIGHT: int
    CARD_RADIUS: int
    BUTTON_RADIUS: int
    INPUT_RADIUS: int


UI_DIMENSIONS = UIDimensions(
    MIN_WINDOW_WIDTH=900,
    MIN_WINDOW_HEIGHT=650,
    DEFAULT_WINDOW_WIDTH=1280,
    DEFAULT_WINDOW_HEIGHT=800,
    HEADER_HEIGHT=65,
    FOOTER_HEIGHT=45,
    SIDEBAR_WIDTH=240,
    SIDEBAR_COLLAPSED_WIDTH=70,
    CONTENT_MARGIN=24,
    WIDGET_SPACING=16,
    BUTTON_HEIGHT=48,
    INPUT_HEIGHT=44,
    CARD_RADIUS=20,
    BUTTON_RADIUS=12,
    INPUT_RADIUS=10,
)


@dataclass(frozen=True)
class ColorPalette:
    """Color palette for the modern dark theme."""

    PRIMARY: str
    PRIMARY_HOVER: str
    PRIMARY_DARK: str
    BG_DARK: str
    BG_MEDIUM: str
    BG_LIGHT: str
    BG_CARD: str
    GLASS_BG: str
    GLASS_BORDER: str
    GLASS_SHADOW: str
    TEXT_PRIMARY: str
    TEXT_SECONDARY: str
    TEXT_MUTED: str
    SUCCESS: str
    SUCCESS_BG: str
    WARNING: str
    WARNING_BG: str
    ERROR: str
    ERROR_BG: str
    INFO: str
    INFO_BG: str


COLORS = ColorPalette(
    PRIMARY="#6366F1",
    PRIMARY_HOVER="#818CF8",
    PRIMARY_DARK="#4F46E5",
    BG_DARK="#0F172A",
    BG_MEDIUM="#1E293B",
    BG_LIGHT="#334155",
    BG_CARD="#1E293B",
    GLASS_BG="rgba(255, 255, 255, 0.03)",
    GLASS_BORDER="rgba(255, 255, 255, 0.08)",
    GLASS_SHADOW="rgba(0, 0, 0, 0.5)",
    TEXT_PRIMARY="#F8FAFC",
    TEXT_SECONDARY="#94A3B8",
    TEXT_MUTED="#64748B",
    SUCCESS="#10B981",
    SUCCESS_BG="rgba(16, 185, 129, 0.15)",
    WARNING="#F59E0B",
    WARNING_BG="rgba(245, 158, 11, 0.15)",
    ERROR="#EF4444",
    ERROR_BG="rgba(239, 68, 68, 0.15)",
    INFO="#3B82F6",
    INFO_BG="rgba(59, 130, 246, 0.15)",
)


@dataclass(frozen=True)
class IconNames:
    """QtAwesome icon names."""

    DASHBOARD: str
    REGISTER: str
    ATTENDANCE: str
    RECORDS: str
    SETTINGS: str
    CAPTURE: str
    SAVE: str
    DELETE: str
    SEARCH: str
    FILTER: str
    REFRESH: str
    EXPORT: str
    SUCCESS: str
    WARNING: str
    ERROR: str
    INFO: str
    CAMERA_ON: str
    CAMERA_OFF: str
    DATABASE: str
    CONNECTED: str
    DISCONNECTED: str
    USER: str
    USERS: str
    CALENDAR: str
    CLOCK: str
    MENU: str
    CLOSE: str


ICONS = IconNames(
    DASHBOARD="fa5s.th-large",
    REGISTER="fa5s.user-plus",
    ATTENDANCE="fa5s.camera",
    RECORDS="fa5s.clipboard-list",
    SETTINGS="fa5s.cog",
    CAPTURE="fa5s.camera",
    SAVE="fa5s.save",
    DELETE="fa5s.trash-alt",
    SEARCH="fa5s.search",
    FILTER="fa5s.filter",
    REFRESH="fa5s.sync-alt",
    EXPORT="fa5s.file-export",
    SUCCESS="fa5s.check-circle",
    WARNING="fa5s.exclamation-triangle",
    ERROR="fa5s.times-circle",
    INFO="fa5s.info-circle",
    CAMERA_ON="fa5s.video",
    CAMERA_OFF="fa5s.video-slash",
    DATABASE="fa5s.database",
    CONNECTED="fa5s.plug",
    DISCONNECTED="fa5s.unlink",
    USER="fa5s.user",
    USERS="fa5s.users",
    CALENDAR="fa5s.calendar-alt",
    CLOCK="fa5s.clock",
    MENU="fa5s.bars",
    CLOSE="fa5s.times",
)


@dataclass(frozen=True)
class MessageStrings:
    """User-facing message strings."""

    STUDENT_REGISTERED: str
    ATTENDANCE_MARKED: str
    CAMERA_ERROR: str
    DATABASE_ERROR: str
    FACE_NOT_DETECTED: str
    DUPLICATE_STUDENT: str
    DUPLICATE_ATTENDANCE: str
    RECOGNITION_FAILED: str


MESSAGES = MessageStrings(
    STUDENT_REGISTERED="Student registered successfully",
    ATTENDANCE_MARKED="Attendance marked successfully",
    CAMERA_ERROR="Failed to access camera. Please check connection.",
    DATABASE_ERROR="Database connection failed. Please check network.",
    FACE_NOT_DETECTED="No face detected. Please position your face in the frame.",
    DUPLICATE_STUDENT="Student ID already exists in the system.",
    DUPLICATE_ATTENDANCE="Attendance already marked for today.",
    RECOGNITION_FAILED="Face not recognized. Please register first.",
)
