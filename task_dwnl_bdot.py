from qgis.core import QgsApplication, QgsTask, QgsMessageLog, Qgis

import requests, os

MESSAGE_CATEGORY = "BDOT10k"


class DownloadBdotTask(QgsTask):
    """Subclass task for dwonloading BDOT10k"""

    def __init__(self, description, downloadPath, powiatyTerytList, iface):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.iface = iface
        self.downloadPath = downloadPath
        self.powiatyTerytList = powiatyTerytList

    def run(self):
        downloadPath=self.downloadPath
        powiatyTerytList=self.powiatyTerytList

        QgsMessageLog.logMessage(f"Rozpoczęto pobieranie BDOT10k dla: {powiatyTerytList}",
                                MESSAGE_CATEGORY, Qgis.Info)

        for teryt in powiatyTerytList:
                
            url = f'https://opendata.geoportal.gov.pl/bdot10k/schemat2021/{teryt[:2]}/{teryt}_GML.zip'

            r = requests.get(url)
            if r.status_code == 200:
                bdot_zip_path = os.path.join(downloadPath, f'bdot10k_{teryt}.zip')
                with open(bdot_zip_path, 'wb') as bdot_dwnl_file:
                    bdot_dwnl_file.write(r.content)
            else:
                QgsMessageLog.logMessage(f"Błąd. Połączenie z serwerem nie powiodło się. \
                                        Kod błędu: {r.status_code}",
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
            self.iface.messageBar().pushMessage("Błąd. Nie udało się pobrać paczek BDOT10k.")

    def cancel(self):
        QgsMessageLog.logMessage("Anulowano pobieranie.",
                                MESSAGE_CATEGORY, Qgis.Info)
        self.iface.messageBar().pushMessage("Stop", "Anulowano pobieranie",
                                            level=Qgis.Info)
        super().cancel()
