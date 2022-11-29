# -*- coding: utf-8 -*-
"""
/***************************************************************************
 BDOT10k
                                 A QGIS plugin
 This plugin operates on BDOT10k.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2022-01-06
        git sha              : $Format:%H$
        copyright            : (C) 2022 by marylaGIS
        email                : maryla.qgis@gmail.com
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog, QMessageBox, QCheckBox

from qgis.core import Qgis, QgsMessageLog, QgsApplication

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialogs
from .bdot10k_dialog_base import BDOT10kDialogBase
# Import the code for the tasks
from .task_dwnl_bdot import DownloadBdotTask

import os

class BDOT10k:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'BDOT10k_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&BDOT10k plugin')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('BDOT10k', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/bdot10k/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Pobierz paczki .zip BDOT10k'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&BDOT10k plugin'),
                action)
            self.iface.removeToolBarIcon(action)  

    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = BDOT10kDialogBase()
            self.dlg.download_btn.clicked.connect(self.download_bdot10k_zip)
        
        # show the dialog
        self.dlg.show()

        self.dlg.clear_cb.clicked.connect(self.clear_checkboxes)
    
    def download_bdot10k_zip(self):
        downloadPath = self.dlg.dwnl_path.filePath()

        # check which data type has been selected
        if self.dlg.rbtnSHP.isChecked():
            bdot10kDataFormat = 'SHP'
        elif self.dlg.rbtnGML.isChecked():
            bdot10kDataFormat = 'GML'
        
        # create a list with all checked checkboxes
        qcbList = self.dlg.findChildren(QCheckBox)
        checkBoxList = []
        for qcb in qcbList:
            if qcb.isChecked():
                checkBoxList.append(qcb.objectName()[-4:])

        # use separate funciotn for checking if dwnl path is correct
        if self.check_dwnl_path(downloadPath) == True and len(checkBoxList) >= 1:
            QgsMessageLog.logMessage(f'Lokalizacja pobierania: {downloadPath}', 'BDOT10k', level=Qgis.MessageLevel.Info)
            QgsMessageLog.logMessage('Pobieranie paczek dla powiatów: ' + str(sorted(checkBoxList)), 'BDOT10k', level=Qgis.MessageLevel.Info)

            # use QgsTask class for downloading BDOT10k in the background
            task = DownloadBdotTask(
                description="Pobieranie paczek BDOT10k",
                downloadPath=downloadPath,
                bdot10kDataFormat=bdot10kDataFormat,
                checkBoxList=checkBoxList,
                iface=self.iface
            )

            QgsApplication.taskManager().addTask(task)

        elif len(checkBoxList) == 0:
            QMessageBox.critical(self.dlg, "Błąd", "Wybierz powiat(y) do pobrania BDTO10k.")
        else:
            return False

    def check_dwnl_path(self, downloadPath):
        if not downloadPath:
            QMessageBox.critical(self.dlg, "Błąd", "Wskaż lokalizację pobierania.")
            return False
        elif not os.path.exists(downloadPath):
            QMessageBox.critical(self.dlg, "Błąd", "Podana lokalizacja nie istnieje.")
            return False
        else:
            return True

    def clear_checkboxes(self):
        qcbList = self.dlg.findChildren(QCheckBox)
        for qcb in qcbList:
            qcb.setChecked(False)