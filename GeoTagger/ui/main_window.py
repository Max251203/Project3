# -*- coding: utf-8 -*-

################################################################################
# Form generated from reading UI file 'main_window.ui'
##
# Created by: Qt User Interface Compiler version 6.8.3
##
# WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
                            QMetaObject, QObject, QPoint, QRect,
                            QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
                           QFont, QFontDatabase, QGradient, QIcon,
                           QImage, QKeySequence, QLinearGradient, QPainter,
                           QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFormLayout, QFrame, QGroupBox,
                               QHBoxLayout, QHeaderView, QLabel, QLineEdit,
                               QMainWindow, QPushButton, QSizePolicy, QSpacerItem,
                               QTabWidget, QTableWidget, QTableWidgetItem, QTextEdit,
                               QVBoxLayout, QWidget)
import ui.resources_rc


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(900, 600)
        icon = QIcon()
        icon.addFile(u":/icons/app_icon.png", QSize(),
                     QIcon.Mode.Normal, QIcon.State.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.topPanel = QFrame(self.centralwidget)
        self.topPanel.setObjectName(u"topPanel")
        self.topPanel.setFrameShape(QFrame.StyledPanel)
        self.horizontalLayoutTopInfo = QHBoxLayout(self.topPanel)
        self.horizontalLayoutTopInfo.setSpacing(8)
        self.horizontalLayoutTopInfo.setObjectName(u"horizontalLayoutTopInfo")
        self.horizontalLayoutTopInfo.setContentsMargins(10, 5, 10, 5)
        self.btnSelectFolder = QPushButton(self.topPanel)
        self.btnSelectFolder.setObjectName(u"btnSelectFolder")
        icon1 = QIcon()
        icon1.addFile(u":/icons/folder.png", QSize(),
                      QIcon.Mode.Normal, QIcon.State.Off)
        self.btnSelectFolder.setIcon(icon1)

        self.horizontalLayoutTopInfo.addWidget(self.btnSelectFolder)

        self.btnLoadGPX = QPushButton(self.topPanel)
        self.btnLoadGPX.setObjectName(u"btnLoadGPX")
        icon2 = QIcon()
        icon2.addFile(u":/icons/gpx_file.png", QSize(),
                      QIcon.Mode.Normal, QIcon.State.Off)
        self.btnLoadGPX.setIcon(icon2)

        self.horizontalLayoutTopInfo.addWidget(self.btnLoadGPX)

        self.editTimeCorrection = QLineEdit(self.topPanel)
        self.editTimeCorrection.setObjectName(u"editTimeCorrection")
        self.editTimeCorrection.setMinimumHeight(32)

        self.horizontalLayoutTopInfo.addWidget(self.editTimeCorrection)

        self.btnStart = QPushButton(self.topPanel)
        self.btnStart.setObjectName(u"btnStart")
        icon3 = QIcon()
        icon3.addFile(u":/icons/run.png", QSize(),
                      QIcon.Mode.Normal, QIcon.State.Off)
        self.btnStart.setIcon(icon3)

        self.horizontalLayoutTopInfo.addWidget(self.btnStart)

        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayoutTopInfo.addItem(self.horizontalSpacer)

        self.statusLabel = QLabel(self.topPanel)
        self.statusLabel.setObjectName(u"statusLabel")
        self.statusLabel.setMinimumWidth(200)

        self.horizontalLayoutTopInfo.addWidget(self.statusLabel)

        self.verticalLayout.addWidget(self.topPanel)

        self.trackInfoGroup = QGroupBox(self.centralwidget)
        self.trackInfoGroup.setObjectName(u"trackInfoGroup")
        self.formLayout = QFormLayout(self.trackInfoGroup)
        self.formLayout.setObjectName(u"formLayout")
        self.lblStartUTCLabel = QLabel(self.trackInfoGroup)
        self.lblStartUTCLabel.setObjectName(u"lblStartUTCLabel")

        self.formLayout.setWidget(
            0, QFormLayout.LabelRole, self.lblStartUTCLabel)

        self.lblStartUTC = QLabel(self.trackInfoGroup)
        self.lblStartUTC.setObjectName(u"lblStartUTC")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.lblStartUTC)

        self.lblEndUTCLabel = QLabel(self.trackInfoGroup)
        self.lblEndUTCLabel.setObjectName(u"lblEndUTCLabel")

        self.formLayout.setWidget(
            1, QFormLayout.LabelRole, self.lblEndUTCLabel)

        self.lblEndUTC = QLabel(self.trackInfoGroup)
        self.lblEndUTC.setObjectName(u"lblEndUTC")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.lblEndUTC)

        self.lblStartLocalLabel = QLabel(self.trackInfoGroup)
        self.lblStartLocalLabel.setObjectName(u"lblStartLocalLabel")

        self.formLayout.setWidget(
            2, QFormLayout.LabelRole, self.lblStartLocalLabel)

        self.lblStartLocal = QLabel(self.trackInfoGroup)
        self.lblStartLocal.setObjectName(u"lblStartLocal")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.lblStartLocal)

        self.verticalLayout.addWidget(self.trackInfoGroup)

        self.tabWidgetMain = QTabWidget(self.centralwidget)
        self.tabWidgetMain.setObjectName(u"tabWidgetMain")
        self.tabWidgetMain.setIconSize(QSize(24, 24))
        self.tabFiles = QWidget()
        self.tabFiles.setObjectName(u"tabFiles")
        self.verticalLayoutFiles = QVBoxLayout(self.tabFiles)
        self.verticalLayoutFiles.setObjectName(u"verticalLayoutFiles")
        self.tableFiles = QTableWidget(self.tabFiles)
        if (self.tableFiles.columnCount() < 3):
            self.tableFiles.setColumnCount(3)
        __qtablewidgetitem = QTableWidgetItem()
        self.tableFiles.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tableFiles.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tableFiles.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        self.tableFiles.setObjectName(u"tableFiles")

        self.verticalLayoutFiles.addWidget(self.tableFiles)

        icon4 = QIcon()
        icon4.addFile(u":/icons/files.png", QSize(),
                      QIcon.Mode.Normal, QIcon.State.Off)
        self.tabWidgetMain.addTab(self.tabFiles, icon4, "")
        self.tabLogs = QWidget()
        self.tabLogs.setObjectName(u"tabLogs")
        self.verticalLayoutLogs = QVBoxLayout(self.tabLogs)
        self.verticalLayoutLogs.setObjectName(u"verticalLayoutLogs")
        self.textEditLogs = QTextEdit(self.tabLogs)
        self.textEditLogs.setObjectName(u"textEditLogs")
        self.textEditLogs.setReadOnly(True)

        self.verticalLayoutLogs.addWidget(self.textEditLogs)

        self.horizontalLayoutClearLogs = QHBoxLayout()
        self.horizontalLayoutClearLogs.setObjectName(
            u"horizontalLayoutClearLogs")
        self.horizontalSpacer_Logs = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayoutClearLogs.addItem(self.horizontalSpacer_Logs)

        self.btnClearLogs = QPushButton(self.tabLogs)
        self.btnClearLogs.setObjectName(u"btnClearLogs")
        icon5 = QIcon()
        icon5.addFile(u":/icons/clear.png", QSize(),
                      QIcon.Mode.Normal, QIcon.State.Off)
        self.btnClearLogs.setIcon(icon5)

        self.horizontalLayoutClearLogs.addWidget(self.btnClearLogs)

        self.verticalLayoutLogs.addLayout(self.horizontalLayoutClearLogs)

        icon6 = QIcon()
        icon6.addFile(u":/icons/log.png", QSize(),
                      QIcon.Mode.Normal, QIcon.State.Off)
        self.tabWidgetMain.addTab(self.tabLogs, icon6, "")
        self.tabSettings = QWidget()
        self.tabSettings.setObjectName(u"tabSettings")
        self.verticalLayoutSettings = QVBoxLayout(self.tabSettings)
        self.verticalLayoutSettings.setObjectName(u"verticalLayoutSettings")
        icon7 = QIcon()
        icon7.addFile(u":/icons/settings.png", QSize(),
                      QIcon.Mode.Normal, QIcon.State.Off)
        self.tabWidgetMain.addTab(self.tabSettings, icon7, "")

        self.verticalLayout.addWidget(self.tabWidgetMain)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.tabWidgetMain.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate(
            "MainWindow", u"GeoTagger", None))
        self.btnSelectFolder.setText(QCoreApplication.translate(
            "MainWindow", u"\u0412\u044b\u0431\u0440\u0430\u0442\u044c \u043f\u0430\u043f\u043a\u0443", None))
        self.btnLoadGPX.setText(QCoreApplication.translate(
            "MainWindow", u"\u0417\u0430\u0433\u0440\u0443\u0437\u0438\u0442\u044c GPX", None))
        self.editTimeCorrection.setPlaceholderText(QCoreApplication.translate(
            "MainWindow", u"\u041f\u043e\u043f\u0440\u0430\u0432\u043a\u0430 \u0432\u0440\u0435\u043c\u0435\u043d\u0438 (\u00b1\u0447:\u043c\u043c)", None))
        self.btnStart.setText(QCoreApplication.translate(
            "MainWindow", u"\u0417\u0430\u043f\u0443\u0441\u043a", None))
        self.statusLabel.setText("")
        self.trackInfoGroup.setTitle(QCoreApplication.translate(
            "MainWindow", u"\u0418\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0438\u044f \u043e \u0442\u0440\u0435\u043a\u0435", None))
        self.lblStartUTCLabel.setText(QCoreApplication.translate(
            "MainWindow", u"\u041d\u0430\u0447\u0430\u043b\u043e \u0442\u0440\u0435\u043a\u0430 (UTC):", None))
        self.lblStartUTC.setText(
            QCoreApplication.translate("MainWindow", u"-", None))
        self.lblEndUTCLabel.setText(QCoreApplication.translate(
            "MainWindow", u"\u041a\u043e\u043d\u0435\u0446 \u0442\u0440\u0435\u043a\u0430 (UTC):", None))
        self.lblEndUTC.setText(
            QCoreApplication.translate("MainWindow", u"-", None))
        self.lblStartLocalLabel.setText(QCoreApplication.translate(
            "MainWindow", u"\u041c\u0435\u0441\u0442\u043d\u043e\u0435 \u0432\u0440\u0435\u043c\u044f \u0441\u0442\u0430\u0440\u0442\u0430:", None))
        self.lblStartLocal.setText(
            QCoreApplication.translate("MainWindow", u"-", None))
        ___qtablewidgetitem = self.tableFiles.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate(
            "MainWindow", u"\u0424\u0430\u0439\u043b", None))
        ___qtablewidgetitem1 = self.tableFiles.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate(
            "MainWindow", u"\u0412\u0440\u0435\u043c\u044f \u0441\u044a\u0451\u043c\u043a\u0438", None))
        ___qtablewidgetitem2 = self.tableFiles.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate(
            "MainWindow", u"\u041a\u043e\u043e\u0440\u0434\u0438\u043d\u0430\u0442\u044b", None))
        self.tabWidgetMain.setTabText(self.tabWidgetMain.indexOf(
            self.tabFiles), QCoreApplication.translate("MainWindow", u"\u0424\u0430\u0439\u043b\u044b", None))
        self.textEditLogs.setPlaceholderText(QCoreApplication.translate(
            "MainWindow", u"\u0417\u0434\u0435\u0441\u044c \u043e\u0442\u043e\u0431\u0440\u0430\u0436\u0430\u044e\u0442\u0441\u044f \u043b\u043e\u0433\u0438 \u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u044f...", None))
        self.btnClearLogs.setText(QCoreApplication.translate(
            "MainWindow", u"\u041e\u0447\u0438\u0441\u0442\u0438\u0442\u044c \u043b\u043e\u0433\u0438", None))
        self.tabWidgetMain.setTabText(self.tabWidgetMain.indexOf(
            self.tabLogs), QCoreApplication.translate("MainWindow", u"\u041b\u043e\u0433\u0438", None))
        self.tabWidgetMain.setTabText(self.tabWidgetMain.indexOf(self.tabSettings), QCoreApplication.translate(
            "MainWindow", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438", None))
    # retranslateUi
