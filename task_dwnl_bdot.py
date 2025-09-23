import os, requests

from qgis.core import (Qgis, QgsApplication, QgsMessageLog,
                       QgsNetworkAccessManager, QgsTask)
from qgis.gui import QgisInterface
from qgis.utils import iface

from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtNetwork import QNetworkReply, QNetworkRequest

MESSAGE_CATEGORY = "BDOT10k"


class DownloadBdotTask(QgsTask):
    """Subclass task for dwonloading BDOT10k."""

    def __init__(self, description: str, downloadPath: str, oldSchema: bool,
                bdot10kDataFormat: str, powiatyTerytList: list):
        """Constructor."""

        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.downloadPath = downloadPath
        self.oldSchema = oldSchema
        self.bdot10kDataFormat = bdot10kDataFormat
        self.powiatyTerytList = powiatyTerytList
        self.networkManager = QgsNetworkAccessManager()

    def run(self) -> bool:
        """Downloads BDOT10k data based on the options
        selected in the plugin dialog."""

        QgsMessageLog.logMessage(
            f"Lokalizacja pobierania: {self.downloadPath}",
            MESSAGE_CATEGORY,
            Qgis.Info
        )

        QgsMessageLog.logMessage(
            "Rozpoczęto pobieranie paczek BDOT10k powiatów o numerach TERYT:" \
            f"{self.powiatyTerytList}",
            MESSAGE_CATEGORY,
            Qgis.Info
        )

        if self.oldSchema:
            if self.bdot10kDataFormat == 'SHP':
                url = 'https://opendata.geoportal.gov.pl/bdot10k/SHP/{}/{}_SHP.zip'
                bdot_zip = 'bdot10k_SHP_{}.zip'
            elif self.bdot10kDataFormat == 'GML':
                url = 'https://opendata.geoportal.gov.pl/bdot10k/{}/{}_GML.zip'
                bdot_zip = 'bdot10k_GML_{}.zip'
        else:
            if self.bdot10kDataFormat == 'GML':
                url = 'https://opendata.geoportal.gov.pl/bdot10k/schemat2021/{}/{}_GML.zip'
                bdot_zip = 'bdot10k_{}.zip'
            elif self.bdot10kDataFormat == 'GPKG':
                url = 'https://opendata.geoportal.gov.pl/bdot10k/schemat2021/GPKG/{}/{}_GPKG.zip'
                bdot_zip = 'bdot10k_GPKG_{}.zip'

        for teryt in self.powiatyTerytList:
            request = QNetworkRequest(QUrl(url.format(teryt[:2], teryt)))
            reply = self.networkManager.blockingGet(request)
            
            if reply.error() == QNetworkReply.NoError:
                content = reply.content()
                bdot_zip_path = os.path.join(self.downloadPath, bdot_zip.format(teryt))
                with open(bdot_zip_path, 'wb') as bdot_dwnl_file:
                    bdot_dwnl_file.write(content)
            else:
                QgsMessageLog.logMessage(
                    "Połączenie z serwerem nie powiodło się." \
                    f"Treść błędu: {reply.errorString()}",
                    MESSAGE_CATEGORY,
                    Qgis.Critical
                )
                return False

            if self.isCanceled():
                return False

        return True

    def finished(self, result):
        """Logs messages based on the task result value."""

        if result:
            QgsMessageLog.logMessage(
                "Pobrano paczki BDOT10k.",
                MESSAGE_CATEGORY,
                Qgis.Success
            )

            iface.messageBar().pushMessage(
                "Sukces", "Pobrano paczki BOT10k.",
                level=Qgis.Success,
                duration=10
            )
        else:
            if self.exception is None:
                QgsMessageLog.logMessage(
                    "Nie udało się pobrać paczek BDOT10k.",
                    MESSAGE_CATEGORY,
                    Qgis.Warning
                )
            else:
                QgsMessageLog.logMessage(
                    "Nie udało się pobrać paczek BDOT10k.\n" \
                    f"Treść błędu: {self.exception}",
                    MESSAGE_CATEGORY,
                    Qgis.Critical
                )
                raise self.exception

            iface.messageBar().pushMessage(
                "Błąd", "Nie udało się pobrać paczek BDOT10k.",
                level=Qgis.Critical,
                duration=10
            )

    def cancel(self):
        """Cancels the running task and logs an appropriate message."""

        QgsMessageLog.logMessage(
            "Anulowano pobieranie paczek BDOT10k.",
            MESSAGE_CATEGORY,
            Qgis.Info
        )

        iface.messageBar().pushMessage(
            "Stop", "Anulowano pobieranie paczek BDOT10k.",
            level=Qgis.Info
        )

        super().cancel()
