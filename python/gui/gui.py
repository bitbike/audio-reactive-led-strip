# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'control_app.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(958, 795)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout_3 = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.centralGridLayout = QtGui.QGridLayout()
        self.centralGridLayout.setObjectName(_fromUtf8("centralGridLayout"))
        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab_3 = QtGui.QWidget()
        self.tab_3.setObjectName(_fromUtf8("tab_3"))
        self.tabWidget.addTab(self.tab_3, _fromUtf8(""))
        self.visualizerTab = QtGui.QWidget()
        self.visualizerTab.setObjectName(_fromUtf8("visualizerTab"))
        self.gridLayout_2 = QtGui.QGridLayout(self.visualizerTab)
        self.gridLayout_2.setMargin(0)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.visualizerVLayout = QtGui.QVBoxLayout()
        self.visualizerVLayout.setObjectName(_fromUtf8("visualizerVLayout"))
        self.soundDeviceSelectBox = QtGui.QComboBox(self.visualizerTab)
        self.soundDeviceSelectBox.setObjectName(_fromUtf8("soundDeviceSelectBox"))
        self.visualizerVLayout.addWidget(self.soundDeviceSelectBox)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.visualizerStartBtn = QtGui.QPushButton(self.visualizerTab)
        self.visualizerStartBtn.setObjectName(_fromUtf8("visualizerStartBtn"))
        self.horizontalLayout.addWidget(self.visualizerStartBtn)
        self.visualizerStopBtn = QtGui.QPushButton(self.visualizerTab)
        self.visualizerStopBtn.setObjectName(_fromUtf8("visualizerStopBtn"))
        self.horizontalLayout.addWidget(self.visualizerStopBtn)
        self.visualizerVLayout.addLayout(self.horizontalLayout)
        self.gridLayout_2.addLayout(self.visualizerVLayout, 0, 0, 1, 1)
        self.tabWidget.addTab(self.visualizerTab, _fromUtf8(""))
        self.centralGridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)
        self.gridLayout_3.addLayout(self.centralGridLayout, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 958, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "LED Control", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("MainWindow", "Start", None))
        self.visualizerStartBtn.setText(_translate("MainWindow", "Start", None))
        self.visualizerStopBtn.setText(_translate("MainWindow", "Stop", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.visualizerTab), _translate("MainWindow", "Tab 2", None))

