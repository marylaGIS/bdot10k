"""
This file contains functions used across different modules.
"""

import os

from qgis.PyQt.QtWidgets import QMessageBox


def check_dwnl_path(downloadPath: str) -> bool:
    """Checks whether the given path is provided and exists.

    :return: True if the path is valid, False otherwise.
    """

    if not downloadPath:
        QMessageBox.critical(None, "Błąd", "Wskaż lokalizację pobierania.")
        return False
    if not os.path.exists(downloadPath):
        QMessageBox.critical(None, "Błąd", "Podana lokalizacja nie istnieje.")
        return False
    return True
