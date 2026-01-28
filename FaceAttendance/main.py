"""Application entry point."""
from __future__ import annotations

import logging
import sys
import traceback

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QMessageBox

from database.mongo_service import get_db_service
from ui.main_window import MainWindow
from utils.constants import APP_NAME, APP_VERSION


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def _handle_exception(exc_type, exc_value, exc_traceback) -> None:
    logging.error("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))
    message = "An unexpected error occurred. Please check logs for details."
    try:
        QMessageBox.critical(None, "Application Error", message)
    except Exception:
        pass


def main() -> int:
    _configure_logging()
    sys.excepthook = _handle_exception

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("Arbab")
    app.setFont(QFont("Segoe UI", 10))

    window = MainWindow()
    window.show()

    exit_code = 0
    try:
        exit_code = app.exec()
    except Exception:
        traceback.print_exc()
    finally:
        get_db_service().disconnect()

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
