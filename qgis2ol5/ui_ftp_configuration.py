# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_ftp_configuration.ui'
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

class Ui_FtpConfiguration(object):
    def setupUi(self, FtpConfiguration):
        FtpConfiguration.setObjectName(_fromUtf8("FtpConfiguration"))
        FtpConfiguration.resize(349, 198)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/qgis2ol5/icons/qgis2ol5.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        FtpConfiguration.setWindowIcon(icon)
        self.gridLayout = QtGui.QGridLayout(FtpConfiguration)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.hostLineEdit = QtGui.QLineEdit(FtpConfiguration)
        self.hostLineEdit.setObjectName(_fromUtf8("hostLineEdit"))
        self.gridLayout.addWidget(self.hostLineEdit, 0, 1, 1, 1)
        self.usernameLineEdit = QtGui.QLineEdit(FtpConfiguration)
        self.usernameLineEdit.setObjectName(_fromUtf8("usernameLineEdit"))
        self.gridLayout.addWidget(self.usernameLineEdit, 3, 1, 1, 1)
        self.label_2 = QtGui.QLabel(FtpConfiguration)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 1)
        self.label = QtGui.QLabel(FtpConfiguration)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_3 = QtGui.QLabel(FtpConfiguration)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)
        self.portSpinBox = QtGui.QSpinBox(FtpConfiguration)
        self.portSpinBox.setMaximum(65535)
        self.portSpinBox.setProperty("value", 21)
        self.portSpinBox.setObjectName(_fromUtf8("portSpinBox"))
        self.gridLayout.addWidget(self.portSpinBox, 1, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(FtpConfiguration)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 2)
        self.folderLineEdit = QtGui.QLineEdit(FtpConfiguration)
        self.folderLineEdit.setObjectName(_fromUtf8("folderLineEdit"))
        self.gridLayout.addWidget(self.folderLineEdit, 2, 1, 1, 1)
        self.label_4 = QtGui.QLabel(FtpConfiguration)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 2, 0, 1, 1)

        self.retranslateUi(FtpConfiguration)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), FtpConfiguration.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), FtpConfiguration.reject)
        QtCore.QMetaObject.connectSlotsByName(FtpConfiguration)
        FtpConfiguration.setTabOrder(self.hostLineEdit, self.portSpinBox)
        FtpConfiguration.setTabOrder(self.portSpinBox, self.folderLineEdit)
        FtpConfiguration.setTabOrder(self.folderLineEdit, self.usernameLineEdit)

    def retranslateUi(self, FtpConfiguration):
        FtpConfiguration.setWindowTitle(_translate("FtpConfiguration", "FTP Settings", None))
        self.label_2.setText(_translate("FtpConfiguration", "Username", None))
        self.label.setText(_translate("FtpConfiguration", "Host", None))
        self.label_3.setText(_translate("FtpConfiguration", "Port", None))
        self.label_4.setText(_translate("FtpConfiguration", "Remote folder", None))

import resources_rc
