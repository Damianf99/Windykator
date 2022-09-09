import pyodbc
import sys
from PyQt5.uic import loadUi 
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QDialog, QApplication, QVBoxLayout, QTableWidgetItem, QTableWidget, QWidget, QMessageBox, QCheckBox, QListWidgetItem
from PyQt5.QtGui import QIcon, QPixmap
from screeninfo import get_monitors

class MainWindow(QDialog):
	def __init__(self, app, widget):
		super(MainWindow, self).__init__()
		loadUi("MainWindow.ui", self)
		self.app = app
		self.widget = widget
		self.generated = 0
		self.logged = 0
		self.passwdEdit.setEchoMode(QtWidgets.QLineEdit.Password)
		self.loginButton.clicked.connect(self.login)
		self.quitButton.clicked.connect(self.quit)
		self.getbaseButton.clicked.connect(self.get_base)
		self.getParametersButton.clicked.connect(self.get_params)
		self.licenseButton.clicked.connect(self.go_to_license)
		self.enter_saved_data()
		self.payments = ""

	def get_payments(self, payments):
		self.payments = payments

	def enter_saved_data(self):
		with open('Data/Config.txt', 'r',encoding='utf-8') as f:
			line = f.readline()
			if line != "":
				line = line[:-1]
				self.serwerEdit.setText(line)
				line = f.readline()
				self.userEdit.setText(line)

	def login(self, from_get_database = False):
		global cursor
		global cnxn
		server = self.serwerEdit.text()
		database = self.comboBox.currentText() 
		username = self.userEdit.text() 
		password = self.passwdEdit.text()

		try:
			cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
		except:
			msg = QMessageBox()
			msg.setText("Nie można połączyć z bazą danych!")
			msg.setIcon(QMessageBox.Critical)
			x = msg.exec_()
			return

		if from_get_database == True:
			return

		cursor = cnxn.cursor()
		try:
			cursor.execute('CREATE TABLE pd__Licencje (License varchar(255));')
			cursor.execute('INSERT INTO pd__Licencje (License) VALUES (NULL);')
			cnxn.commit()
		except:
			pass
		cursor.execute('Select License from pd__Licencje')
		license = [n for n in cursor]
		if len(license) == 0 or license[0][0] != "1":
			msg = QMessageBox()
			msg.setText("Brak licencji!")
			msg.setIcon(QMessageBox.Critical)
			x = msg.exec_()
			return
		msg = QMessageBox()
		msg.setText("Poprawnie zalogowano do bazy")
		x = msg.exec_()
		self.generated = 0
		self.logged = 1
		self.serwerEdit.setText("")
		self.userEdit.setText("")
		self.passwdEdit.setText("")
		self.widget.setFixedWidth(900)
		self.widget.setFixedHeight(700)
		for m in get_monitors():
			width = int((((((str(m))[7:]).split(","))[2]).split("="))[1])
		self.widget.setGeometry(int(width/6),30,900,700)
		self.payments.fill_comboBoxes()
		self.widget.setCurrentIndex(1)

	def get_base(self):
		global cursor
		global cnxn
		server = self.serwerEdit.text()
		database = "master"
		username = self.userEdit.text() 
		password = self.passwdEdit.text()
		if len(server) == 0 or len(username) == 0:
			msg = QMessageBox()
			msg.setText("Brak nazwy serwera lub nazwy użytkownika!")
			msg.setIcon(QMessageBox.Critical)
			x = msg.exec_()
			return
		try:
			cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
		except:
			msg = QMessageBox()
			msg.setText("Nie można połączyć z bazą danych!")
			msg.setIcon(QMessageBox.Critical)
			x = msg.exec_()
			return
		cursor = cnxn.cursor()
		cursor.execute('Select * from sysdatabases')
		databases = []
		prohibited_names = ['master', 'tempdb', 'model', 'msdb']
		self.comboBox.clear()
		self.comboBox.addItem("Wybierz z listy...")
		for n in cursor:
			if n[0] not in prohibited_names:
				databases.append(n[0])
		for n in range(len(databases)):
			self.comboBox.addItem(databases[n])

	def get_params(self):
		with open('Data/Config.txt', 'w',encoding='utf-8') as f:
			ret = QMessageBox.question(self, 'Windykator',f"Czy napewno chcesz zapisać serwer jako: {self.serwerEdit.text()} i nazwę użytkownika jako: {self.userEdit.text()}?", QMessageBox.Yes | QMessageBox.No)
			if ret == QMessageBox.No:
				return
			f.write(f"{self.serwerEdit.text()}\n")
			f.write(self.userEdit.text())

	def go_to_license(self):
		self.widget.setCurrentIndex(3)

	def quit(self):
		try:
			self.app.exit()
		except:
			pass

	def get_database(self, try_to_log = False):
		global cnxn
		if try_to_log == True:
			self.login(True)
		return cnxn


def main():
	if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
		QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
	if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
		QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

	app = QApplication(sys.argv)
	widget = QtWidgets.QStackedWidget()

	mainwindow = MainWindow() #0

	widget.addWidget(mainwindow)

	widget.setFixedWidth(800)
	widget.setFixedHeight(500)
	widget.show()

	try:
		sys.exit(app.exec_())
	except:
		print("")

if __name__ == "__main__":
	main()

