import pyodbc
import sys
import hashlib
from PyQt5.uic import loadUi 
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QDialog, QApplication, QVBoxLayout, QTableWidgetItem, QTableWidget, QWidget, QMessageBox, QCheckBox, QListWidgetItem
from PyQt5.QtGui import QIcon, QPixmap


class License(QDialog):
	def __init__(self, widget, mainwindow):
		super(License, self).__init__()
		loadUi("License.ui", self)
		self.widget = widget
		self.mainwindow = mainwindow
		self.saveButton.clicked.connect(self.save)
		self.backButton.clicked.connect(self.back)

	def save(self):
		try:
			self.cnxn = self.mainwindow.get_database(True)
			cursor = self.cnxn.cursor()
			cursor.execute("select adr_NIP from adr__Ewid join rb__RachBankowy on rb__RachBankowy.rb_IdObiektu = adr__Ewid.adr_IdObiektu where adr_TypAdresu=8 and adr_IdObiektu = 1 and rb_Podstawowy = 1 and rb_TypObiektu=0")
			NIP = [n for n in cursor]
			NIP = NIP[0][0]
			if str(NIP) == (str(self.NipEdit.text()).replace(" ", "")).replace("-", ""):
				NIP = int(NIP)
				#Some secrete code
				NIP = bytes(NIP, encoding='utf-8')
				#code = Some secrete code
				code.update(NIP)
				code = code.hexdigest()
				if str(code) == str(self.keylicenseEdit.text()):
					try:
						cursor.execute("UPDATE pd__Licencje SET License = 1;")
						self.cnxn.commit()
						msg = QMessageBox()
						msg.setText("Licencja została przyznana")
						x = msg.exec_()
					except Exception as e:
						msg = QMessageBox()
						msg.setText(str(e))
						msg.setIcon(QMessageBox.Critical)
						x = msg.exec_()
						return
				else:
					msg = QMessageBox()
					msg.setText("Podany klucz jest niepoprawny!")
					msg.setIcon(QMessageBox.Critical)
					x = msg.exec_()
					return
			else:
				msg = QMessageBox()
				msg.setText("Numer NIP nie pasuje do konta, na które próbujesz się zalogować!")
				msg.setIcon(QMessageBox.Critical)
				x = msg.exec_()
				return
		except:
			msg = QMessageBox()
			msg.setText("Najpierw należy pobrać bazy aby móc przypisać klucz do konta!")
			msg.setIcon(QMessageBox.Critical)
			x = msg.exec_()
			return

	def back(self):
		self.keylicenseEdit.setText("")
		self.NipEdit.setText("")
		self.widget.setCurrentIndex(0)

def main():
	if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
		QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
	if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
		QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

	app = QApplication(sys.argv)
	widget = QtWidgets.QStackedWidget()

	license = License() #0

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