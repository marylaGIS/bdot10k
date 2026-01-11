"""QGIS Task for layer intersection processing in the background.
https://gis.stackexchange.com/a/430368/173206"""

import os

from qgis import processing
from qgis.core import Qgis, QgsMessageLog, QgsTask, QgsVectorLayer
from qgis.utils import iface

from qgis.PyQt.QtCore import pyqtSignal


MESSAGE_CATEGORY = "BDOT10k"


class SelectTask(QgsTask):
    """Subclass task for searching counties."""

    result = pyqtSignal(list)

    def __init__(self, description: str,
                 selectionLayer: QgsVectorLayer):
        """Constructor."""

        super().__init__(description, QgsTask.Flag.CanCancel)
        self.exception = None
        self.plugin_dir = os.path.dirname(__file__)
        self.selectionLayer = selectionLayer
        self.powiatySelected = None
        self.powiatySelectedList = None

    def run(self) -> bool:
        """Select counties based on the intersection
        with the layer selected in the dialog."""

        try:
            powiatyLayer = QgsVectorLayer(
                os.path.join(self.plugin_dir, "powiaty.gpkg"),
                "powiaty",
                "ogr"
            )

            self.powiatySelected = processing.run(
                "native:selectbylocation",
                {
                    'INPUT': powiatyLayer,
                    'PREDICATE': [0],
                    'INTERSECT': self.selectionLayer,
                    'METHOD': 0
                }
            )['OUTPUT']

            self.powiatySelectedList = [
                f'{ft["teryt"]} {ft["nazwa"]}'
                for ft in self.powiatySelected.selectedFeatures()
            ]

            self.powiatySelectedList.sort(key=lambda x: x.split()[0])

            if self.isCanceled():
                return False

        except Exception as e:
            QgsMessageLog.logMessage(
                "Nie udało się wyselekcjonować powiatów.\n"
                f"Treść błędu: {e}",
                MESSAGE_CATEGORY,
                Qgis.Critical
            )
            return False

        return True

    def finished(self, result):
        """Logs messages based on the task result value."""

        if result:
            QgsMessageLog.logMessage(
                "Wyselekcjonowano powiaty.",
                MESSAGE_CATEGORY,
                Qgis.MessageLevel.Success
            )

            self.result.emit(self.powiatySelectedList)

        else:
            if self.exception is None:
                QgsMessageLog.logMessage(
                    "Nie udało się wyselekcjonować powiatów.",
                    MESSAGE_CATEGORY,
                    Qgis.MessageLevel.Warning
                )
            else:
                QgsMessageLog.logMessage(
                    "Nie udało się wyselekcjonować powiatów.\n"
                    f"Treść błędu: {self.exception}",
                    MESSAGE_CATEGORY,
                    Qgis.MessageLevel.Critical
                )
                raise self.exception

            iface.messageBar().pushMessage(
                "Błąd", "Nie udało się wyselekcjonować powiatów.",
                level=Qgis.MessageLevel.Critical,
                duration=10
            )

    def cancel(self):
        """Cancels the running task and logs an appropriate message."""

        QgsMessageLog.logMessage(
            "Anulowano wyszukiwanie powiatów.",
            MESSAGE_CATEGORY,
            Qgis.MessageLevel.Info
        )

        iface.messageBar().pushMessage(
            "Stop", "Anulowano wyszukiwanie powiatów.",
            level=Qgis.MessageLevel.Info
        )

        super().cancel()
