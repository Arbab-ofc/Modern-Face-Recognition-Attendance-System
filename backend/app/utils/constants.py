"""Application constants for the web backend."""
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
