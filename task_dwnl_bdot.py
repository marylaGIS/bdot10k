import requests, os
from qgis.core import (QgsApplication, QgsTask, QgsMessageLog, Qgis, 
    QgsNetworkAccessManager)
from PyQt5.QtCore import QUrl
from PyQt5.QtNetwork import QNetworkRequest

MESSAGE_CATEGORY = "BDOT10k"


class DownloadBdotTask(QgsTask):
    """Subclass task for dwonloading BDOT10k"""

    def __init__(self, description, downloadPath, oldSchema,
                bdot10kDataFormat, powiatyTerytList, iface):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.iface = iface
        self.downloadPath = downloadPath
        self.oldSchema = oldSchema
        self.bdot10kDataFormat = bdot10kDataFormat
        self.powiatyTerytList = powiatyTerytList
        self.network_manager = QgsNetworkAccessManager()

    def run(self):
        QgsMessageLog.logMessage(f"Rozpoczęto pobieranie BDOT10k dla: {self.powiatyTerytList}",
                                MESSAGE_CATEGORY, Qgis.Info)

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
            reply = self.network_manager.blockingGet(request)
            
            if reply.error() == 0:  # QNetworkReply.NoError
                content = reply.content()
                bdot_zip_path = os.path.join(self.downloadPath, bdot_zip.format(teryt))
                with open(bdot_zip_path, 'wb') as bdot_dwnl_file:
                    bdot_dwnl_file.write(content)
            else:
                QgsMessageLog.logMessage("Błąd. Połączenie z serwerem nie powiodło się. " +
                                        f"Treść błędu: {reply.errorString()}",
                                        MESSAGE_CATEGORY, Qgis.Critical)
                return False
            
            if self.isCanceled():
                return False

        # QgsTask must return boolean
        return True

    def finished(self, result):
        if result:
            QgsMessageLog.logMessage("Sukces. Pobrano paczki BDOT10k.",
                                    MESSAGE_CATEGORY, Qgis.Success)
            self.iface.messageBar().pushMessage("Sukces", "Pobrano paczki BOT10k",
                                                level=Qgis.Success, duration=10)
        else:
            if self.exception is None:
                QgsMessageLog.logMessage("Błąd. Nie otrzymano wyników.",
                                        MESSAGE_CATEGORY, Qgis.Warning)
            else:
                QgsMessageLog.logMessage("Błąd. Nie udało się pobrać paczek BDOT10k. \n{exception}"
                                        .format(exception=self.exception),
                                        MESSAGE_CATEGORY, Qgis.Critical)
                raise self.exception
            self.iface.messageBar().pushMessage("Błąd. Nie udało się pobrać paczek BDOT10k.",
                                                level=Qgis.Critical, duration=10)

    def cancel(self):
        QgsMessageLog.logMessage("Anulowano pobieranie.",
                                MESSAGE_CATEGORY, Qgis.Info)
        self.iface.messageBar().pushMessage("Stop", "Anulowano pobieranie paczek BDOT10k",
                                            level=Qgis.Info)
        super().cancel()
