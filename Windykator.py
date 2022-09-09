import sys
import pyodbc
import Start, Payments, Config, License
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QDialog, QApplication, QTableWidgetItem, QCheckBox, QWidget, QHBoxLayout, QColorDialog, QFontDialog
from PyQt5.QtCore import Qt
import os

def main():
    if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    app = QApplication(sys.argv)
    widget = QtWidgets.QStackedWidget()

    mainwindow = Start.MainWindow(app, widget) #0
    config = Config.Config(widget, mainwindow) #2
    payments = Payments.Payments(widget, mainwindow, config) #1
    license = License.License(widget, mainwindow) #3
    mainwindow.get_payments(payments)

    widget.addWidget(mainwindow)
    widget.addWidget(payments)
    widget.addWidget(config)
    widget.addWidget(license)

    widget.setFixedWidth(800)
    widget.setFixedHeight(500)
    widget.show()

    try:
        sys.exit(app.exec_())
    except:
        print("")

if __name__ == "__main__":
	main()




