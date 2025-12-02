from qgis.PyQt.QtCore import pyqtSlot

from qgis.core import QgsTask


class DialogMixin:
    """A mixin class providing shared utility methods
    for dialog components."""

    def on_gbOldSchema_toggled(self):
        """Enables or disables a group of radio buttons
        based on the toggle state."""

        if self.gbOldSchema.isChecked():
            self.rbtnGML.setDisabled(True)
            self.rbtnGPKG.setDisabled(True)
        else:
            self.rbtnGML.setDisabled(False)
            self.rbtnGPKG.setDisabled(False)

    def get_bdot10k_data_options(self) -> tuple:
        """Retrieves the parameters selected in the dialog window.

        :returns: A tuple containing:
            - A boolean indicating whether the old schema is selected.
            - A string representing the selected BDOT10k data format.
        """

        if self.gbOldSchema.isChecked():
            oldSchema = True
            if self.rbtnSHPold.isChecked():
                bdot10kDataFormat = 'SHP'
            elif self.rbtnGMLold.isChecked():
                bdot10kDataFormat = 'GML'
        else:
            oldSchema = False
            if self.rbtnGML.isChecked():
                bdot10kDataFormat = 'GML'
            elif self.rbtnGPKG.isChecked():
                bdot10kDataFormat = 'GPKG'

        return oldSchema, bdot10kDataFormat

    def switch_buttons(self, taskId: int, status: int):
        """Switches visibility of the download and cancel buttons
        after the current download task status has changed.

        :param taskId: The ID of the BDOT10k data download task.
        :param status: The status reported by the task.
        """

        if taskId == self.taskIdDwnl and status in (
            QgsTask.Complete,
            QgsTask.Terminated,
            QgsTask.CancelWithoutPrompt,
        ):
            self.btnCancelDwnl.hide()
            self.btnDwnl.show()

    @pyqtSlot()
    def on_btnCancelDwnl_clicked(self):
        self.taskDwnl.cancel()
        self.btnCancelDwnl.setEnabled(False)
        self.btnCancelDwnl.setToolTip('Pobieranie jest w trakcie anulowania')
