import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtPrintSupport import *
from PyQt5.QtCore import *
from PyQt5.uic import loadUi
from cryptography.fernet import Fernet

#
#
#
#
#
#
#
#
#
#
# Some secrete code
#
#
#
#
#
#
#
#
#
#
#
#

class Config(QDialog):
	def __init__(self, widget, mainwindow):
		super(Config, self).__init__()
		loadUi("ConfigEmail.ui", self)
		self.widget = widget
		self.mainwindow = mainwindow
		self.saveButton.clicked.connect(self.save)
		self.backButton.clicked.connect(self.go_back)
		self.passwdEdit.setEchoMode(QLineEdit.Password)

	def save(self):
		try:
			self.cnxn = self.mainwindow.get_database()
			cursor = self.cnxn.cursor()
			cursor.execute('select adr_NIP from adr__Ewid join rb__RachBankowy on rb__RachBankowy.rb_IdObiektu = adr__Ewid.adr_IdObiektu where adr_TypAdresu=8 and adr_IdObiektu = 1 and rb_Podstawowy = 1 and rb_TypObiektu=0;')
			NIP = [n for n in cursor]
			NIP = NIP[0][0]
		except Exception as e:
			msg = QMessageBox()
			msg.setText(str(e))
			msg.setIcon(QMessageBox.Critical)
			x = msg.exec_()
			return
		with open('Data/EmailConfig.txt', 'w',encoding='utf-8') as f:
			ret = QMessageBox.question(self, 'Windykator',f"Czy napewno chcesz zapisać podaną konfigurację konta email?", QMessageBox.Yes | QMessageBox.No)
			if ret == QMessageBox.No:
				return
			f.write(f"{NIP}\n")
			f.write(f"{self.serverEdit.text()}\n")
			f.write(f"{self.adressEdit.text()}\n")
			f.write(f"{self.portEdit.text()}\n")
			f.write(f"{self.passwdEdit.text()}\n")
			f.write(f"{self.nameEdit.text()}\n")
			f.write(f"{self.adressCopyEdit.text()}\n")
		write_key()
		key = load_key()
		file = "Data/EmailConfig.txt"
		encrypt(file, key)

	def load_config_data(self):
		try:
			self.cnxn = self.mainwindow.get_database()
			cursor = self.cnxn.cursor()
			cursor.execute('select adr_NIP from adr__Ewid join rb__RachBankowy on rb__RachBankowy.rb_IdObiektu = adr__Ewid.adr_IdObiektu where adr_TypAdresu=8 and adr_IdObiektu = 1 and rb_Podstawowy = 1 and rb_TypObiektu=0;')
			NIP = [n for n in cursor]
			NIP = NIP[0][0]
		except Exception as e:
			msg = QMessageBox()
			msg.setText(str(e))
			msg.setIcon(QMessageBox.Critical)
			x = msg.exec_()
			return
		fields = [self.serverEdit, self.adressEdit, self.portEdit, self.passwdEdit, self.nameEdit, self.adressCopyEdit]
		key = load_key()
		file = "Data/EmailConfig.txt"
		decrypt(file, key)
		with open('Data/EmailConfig.txt', 'r',encoding='utf-8') as f:
			line = f.readline()
			if line != "" and NIP == line[:-1]:
				line = f.readline()
				for i in range(len(fields)):
					line = line[:-1]
					fields[i].setText(line)
					line = f.readline()
					if line == "":
						break
		encrypt(file, key)

	def go_back(self):
		self.widget.setCurrentIndex(1)

def main():
	if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
		QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
	if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
		QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

	app = QApplication(sys.argv)
	widget = QtWidgets.QStackedWidget()

	config = Config() #0

	widget.addWidget(config)

	widget.setFixedWidth(900)
	widget.setFixedHeight(700)
	widget.show()

	try:
		sys.exit(app.exec_())
	except:
		print("")

if __name__ == "__main__":
	main()




