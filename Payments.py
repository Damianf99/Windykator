import sys
import os
import pyodbc
import Editor
import smtplib, email
import numpy as np
import threading
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QDialog, QApplication, QTableWidgetItem, QCheckBox, QWidget, QHBoxLayout, QHeaderView, QMessageBox, QInputDialog, QLineEdit, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QObject, pyqtSignal
from datetime import date
from cryptography.fernet import Fernet
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

#Hasło do konta gmail:
#okqzwuqkzlgxvifq


class Helper(QObject):
    finished = pyqtSignal()

class MyWarnings(QDialog):
    def __init__(self, text):
        super(MyWarnings, self).__init__()
        self.widget2 = QLabel(text)
        layout = QVBoxLayout()
        layout.addWidget(self.widget2)
        self.setLayout(layout)

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

class Payments(QDialog):
	def __init__(self, widget, mainwindow, config):
		super(Payments, self).__init__()
		loadUi("Payments.ui", self)
		self.widget = widget
		self.mainwindow = mainwindow
		self.config = config
		self.endButton.clicked.connect(self.quit)
		self.getPaymentsButton.clicked.connect(self.get_payments)
		self.cnxn = None
		self.check_boxes = []
		self.check_boxes_lower_table = []
		self.check_states = []
		self.check_states_lower_table = []
		self.customers_data = []
		self.sendEmailButton.clicked.connect(self.send_email)
		self.PaymentsAllCheck.clicked.connect(self.change_all_states)
		self.PaymentsAllCheck.clicked.connect(self.show)
		self.CompanyAllCheck.clicked.connect(self.change_all_states_lower_table)
		self.makeCallButton.clicked.connect(self.create_emails)
		self.editEmailButton.clicked.connect(self.edit_email)
		self.configEmailButton.clicked.connect(self.config_email)
		self.testEmailButton.clicked.connect(self.test_email)
		self.fromLineEdit.setText("0")
		self.toLineEdit.setText("0")
		self.warehouses_id = []

	def fill_comboBoxes(self):
		self.cnxn = self.mainwindow.get_database()
		cursor = self.cnxn.cursor()
		cursor.execute("select mag_Nazwa from sl_Magazyn")
		self.warehouseCombo.clear()
		self.warehouseCombo.addItem("Dowolny")
		for n in cursor:
			self.warehouseCombo.addItem(str(n).split("'")[1])
		self.acceptCombo.clear()
		self.acceptCombo.addItem("Dowolny")
		self.skipCombo.clear()
		self.skipCombo.addItem("Dowolny")
		cursor.execute("select ckh_Nazwa from sl_CechaKh")
		for n in cursor:
			self.acceptCombo.addItem(str(n)[2:-4])
			self.skipCombo.addItem(str(n)[2:-4])
		self.szablonCombo.clear()
		self.szablonCombo.addItem("Wezwanie do zapłaty")
		self.szablonCombo.addItem("Termin dziś")
		self.szablonCombo.addItem("Przypomnienie")
		self.warehouseCombo.view().setMinimumWidth(self.warehouseCombo.minimumSizeHint().width())
		self.acceptCombo.view().setMinimumWidth(self.acceptCombo.minimumSizeHint().width())
		self.skipCombo.view().setMinimumWidth(self.skipCombo.minimumSizeHint().width())
		self.szablonCombo.view().setMinimumWidth(self.szablonCombo.minimumSizeHint().width())

	def get_payments(self):
		self.CompanyTable.setRowCount(0)
		cursor = self.cnxn.cursor()
		self.warehouses_id = [9999]
		warehouse_names = []
		if self.warehouseCombo.currentText() == 'Dowolny':
			cursor.execute("select mag_Id from sl_Magazyn")
			for n in cursor:
				self.warehouses_id.append(int(str(n)[1:2]))
		else:
			cursor.execute("select mag_Nazwa, mag_Id from sl_Magazyn")
			for n in cursor:
				warehouse_names.append(n)
			for n in range(len(warehouse_names)):
				if warehouse_names[n][0] == str(self.warehouseCombo.currentText()):
					self.warehouses_id.append(warehouse_names[n][1])
		cursor.execute("select ckh_Nazwa from sl_CechaKh")
		iterator = 0
		kh_features = ""
		kh_no_features = ""
		for n in cursor:
			iterator += 1
			if str(self.acceptCombo.currentText()) == str(n)[2:-4]:
				kh_features = f" AND EXISTS (Select ck_IdKhnt from kh_CechaKh where Bk.nzf_IdObiektu = kh_CechaKh.ck_IdKhnt and ck_IdCecha = {iterator}) "
			if str(self.skipCombo.currentText()) == str(n)[2:-4]:
				kh_no_features = f" AND NOT EXISTS (Select ck_IdKhnt from kh_CechaKh where Bk.nzf_IdObiektu = kh_CechaKh.ck_IdKhnt and ck_IdCecha = {iterator}) "
		self.warehouses_id = tuple(self.warehouses_id)
		self.check_states.clear()
		self.check_boxes.clear()
		self.customers_data = []
		if self.allPaymentsRadio.isChecked():
			cursor.execute(f"select adr_Symbol, adr_Nazwa, adr_adres, adr_Miejscowosc, adr_NIP, count(adr_Symbol) as Il_dok, (MAX(DniSpoznienia)) as Dni_spoznienia, FORMAT(CONVERT(float, SUM(naleznosc)),'N2') as naleznosc, am_Email from vwFinanseRozrachunkiWgDokumentow bk LEFT JOIN adr__Ewid AS Adresy ON Bk.nzf_IdAdresu=Adresy.adr_Id LEFT JOIN adr_Email ON adr_Email.am_IdAdres = Adresy.adr_Id WHERE ((Rozliczenie IN (0, 1)) AND ( ( nzf_Status = 1 AND nzf_Typ IN (39, 40) OR nzf_Typ NOT IN (39, 40) ) ) ) AND (nzf_Typ in (39,40)) and bk.dok_magid in {self.warehouses_id} {kh_features} {kh_no_features} and naleznosc is not NULL GROUP BY adr_Id, adr_Symbol, adr_Nazwa, adr_adres, adr_Miejscowosc, adr_NIP, adr_NazwaPelna, am_Email")
		elif self.expiredPaymentsRadio.isChecked():
			if (len(self.fromLineEdit.text()) == 0):
				self.fromLineEdit.setText("0")
			if (len(self.toLineEdit.text()) == 0):
				self.toLineEdit.setText("0")
			if (self.fromLineEdit.text()).isdigit() and (self.toLineEdit.text()).isdigit():
				cursor.execute(f"select adr_Symbol, adr_Nazwa, adr_adres, adr_Miejscowosc, adr_NIP, count(adr_Symbol) as Il_dok, (MAX(DniSpoznienia)) as Dni_spoznienia, FORMAT(CONVERT(float, SUM(naleznosc)),'N2') as naleznosc, am_Email from vwFinanseRozrachunkiWgDokumentow bk LEFT JOIN adr__Ewid AS Adresy ON Bk.nzf_IdAdresu=Adresy.adr_Id LEFT JOIN adr_Email ON adr_Email.am_IdAdres = Adresy.adr_Id WHERE ((Rozliczenie IN (0, 1)) AND ( ( nzf_Status = 1 AND nzf_Typ IN (39, 40) OR nzf_Typ NOT IN (39, 40) ) ) ) AND (nzf_Typ in (39,40)) and bk.dok_magid in {self.warehouses_id} and naleznosc is not NULL and (DniSpoznienia >= {self.fromLineEdit.text()} and DniSpoznienia <= {self.toLineEdit.text()}) {kh_features} {kh_no_features} GROUP BY adr_Id, adr_Symbol, adr_Nazwa, adr_adres, adr_Miejscowosc, adr_NIP, adr_NazwaPelna, am_Email")
			else:
				msg = QMessageBox()
				msg.setText("Wybrano złe wartości przedziału dni!")
				msg.setIcon(QMessageBox.Critical)
				x = msg.exec_()
				return
		else:
			msg = QMessageBox()
			msg.setText("Nie wybrano należności!")
			msg.setIcon(QMessageBox.Critical)
			x = msg.exec_()
			return
		j = 0
		for n in cursor:
			self.customers_data.append(n)
			number = n[-2].split(",")
			number = " ".join(number)
			self.customers_data[j][-2] = number
			if n[-3] == None:
				self.customers_data[j][-3] = 0
			j += 1
		if len(self.customers_data) == 0:
			self.PaymentsTable.setRowCount(0)
			return
		self.PaymentsTable.setRowCount(len(self.customers_data))
		self.PaymentsTable.setColumnCount(len(self.customers_data[0])+1)
		for n in range(len(self.customers_data)):
			Widget = QWidget()
			self.CheckBox = QCheckBox()
			self.check_states.append(self.CheckBox)
			self.CheckBox.clicked.connect(self.show)
			Layout = QHBoxLayout(Widget)
			Layout.addWidget(self.CheckBox)
			Layout.setAlignment(Qt.AlignCenter)
			Layout.setContentsMargins(0,0,0,0)
			Widget.setLayout(Layout)
			self.check_boxes.append(Widget)
		header = self.PaymentsTable.horizontalHeader()
		header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
		header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
		header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
		header.setSectionResizeMode(7, QHeaderView.ResizeToContents)
		for i in range(len(self.customers_data)):
				self.PaymentsTable.setCellWidget(i,0,self.check_boxes[i])
				self.PaymentsTable.setItem(i, 1, QTableWidgetItem(str(self.customers_data[i][0])))
				self.PaymentsTable.setItem(i, 2, QTableWidgetItem(str(self.customers_data[i][1])))
				self.PaymentsTable.setItem(i, 3, QTableWidgetItem(str(self.customers_data[i][2])))
				self.PaymentsTable.setItem(i, 4, QTableWidgetItem(str(self.customers_data[i][3])))
				self.PaymentsTable.setItem(i, 5, QTableWidgetItem(str(self.customers_data[i][4])))
				self.PaymentsTable.setItem(i, 6, QTableWidgetItem(str(self.customers_data[i][5])))
				self.PaymentsTable.setItem(i, 7, QTableWidgetItem(str(self.customers_data[i][6])))
				self.PaymentsTable.setItem(i, 8, QTableWidgetItem(str(self.customers_data[i][7])))
				self.PaymentsTable.setItem(i, 9, QTableWidgetItem(str(self.customers_data[i][8])))

	def show(self):
		self.check_states_lower_table.clear()
		self.check_boxes_lower_table.clear()
		cursor = self.cnxn.cursor()
		self.company_details = []
		names = ['PUSTY']
		for n in range(len(self.check_boxes)):
			if self.check_states[n].isChecked():
				names.append(self.customers_data[n][0])
		names = tuple(names)
		if len(names) == 1:
			self.CompanyTable.setRowCount(0)
			return
		if self.expiredPaymentsRadio.isChecked():
			if (len(self.fromLineEdit.text()) == 0):
				self.fromLineEdit.setText("0")
			if (len(self.toLineEdit.text()) == 0):
				self.toLineEdit.setText("0")
			if (self.fromLineEdit.text()).isdigit() and (self.toLineEdit.text()).isdigit():
				cursor.execute(f"select adr_Symbol, CONVERT(varchar, nzf_data, 103) as DataPowstania, nzf_NumerPelny as NumerDokumentu,  CONVERT(varchar, nzf_TerminPlatnosci, 103) as termin, DniSpoznienia, FORMAT(CONVERT(float, naleznosc),'N2') as Naleznosc, FORMAT(CONVERT(float, nalPierwotna),'N2') as NalPierwotna from vwFinanseRozrachunkiWgDokumentow bk LEFT JOIN adr__Ewid AS Adresy ON Bk.nzf_IdAdresu=Adresy.adr_Id LEFT outer join dok__dokument as dokinfo ON Bk.nzf_IdDokumentAuto=dokinfo.dok_id left outer join sl_FormaPlatnosci as fp on dokinfo.dok_PlatId = fp_Id WHERE ((Rozliczenie IN (0, 1)) AND ( ( nzf_Status = 1 AND nzf_Typ IN (39, 40) OR nzf_Typ NOT IN (39, 40) ) ) ) AND (nzf_Typ in (39,40)) and bk.dok_magid in {self.warehouses_id} and naleznosc is not NULL and nalPierwotna is not NULL and adr_Symbol in {names} and (DniSpoznienia >= {self.fromLineEdit.text()} and DniSpoznienia <= {self.toLineEdit.text()}) ORDER BY Bk.nzf_TerminPlatnosci")
		elif self.allPaymentsRadio.isChecked():
			cursor.execute(f"select adr_Symbol, CONVERT(varchar, nzf_data, 103) as DataPowstania, nzf_NumerPelny as NumerDokumentu,  CONVERT(varchar, nzf_TerminPlatnosci, 103) as termin, DniSpoznienia, FORMAT(CONVERT(float, naleznosc),'N2') as Naleznosc, FORMAT(CONVERT(float, nalPierwotna),'N2') as NalPierwotna from vwFinanseRozrachunkiWgDokumentow bk LEFT JOIN adr__Ewid AS Adresy ON Bk.nzf_IdAdresu=Adresy.adr_Id LEFT outer join dok__dokument as dokinfo ON Bk.nzf_IdDokumentAuto=dokinfo.dok_id left outer join sl_FormaPlatnosci as fp on dokinfo.dok_PlatId = fp_Id WHERE ((Rozliczenie IN (0, 1)) AND ( ( nzf_Status = 1 AND nzf_Typ IN (39, 40) OR nzf_Typ NOT IN (39, 40) ) ) ) AND (nzf_Typ in (39,40)) and bk.dok_magid in {self.warehouses_id} and naleznosc is not NULL and nalPierwotna is not NULL and adr_Symbol in {names} ORDER BY Bk.nzf_TerminPlatnosci")
		else:
			msg = QMessageBox()
			msg.setText("Wybrano złe wartości przedziału dni!")
			msg.setIcon(QMessageBox.Critical)
			x = msg.exec_()
			return
		j = 0
		for n in cursor:
			self.company_details.append(n)
			number = n[-1].split(",")
			number = " ".join(number)
			self.company_details[j][-1] = number
			number = n[-2].split(",")
			number = " ".join(number)
			self.company_details[j][-2] = number
			if n[4] == None:
				self.company_details[j][4] = 0
			j += 1
		self.CompanyTable.setRowCount(len(self.company_details))
		self.CompanyTable.setColumnCount(len(self.company_details[0])+1)
		for n in range(len(self.company_details)):
			Widget = QWidget()
			self.CheckBox = QCheckBox()
			self.check_states_lower_table.append(self.CheckBox)
			Layout = QHBoxLayout(Widget)
			Layout.addWidget(self.CheckBox)
			Layout.setAlignment(Qt.AlignCenter)
			Layout.setContentsMargins(0,0,0,0)
			Widget.setLayout(Layout)
			self.check_boxes_lower_table.append(Widget)
		header = self.CompanyTable.horizontalHeader()
		header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
		for i in range(len(self.company_details)):
				self.CompanyTable.setCellWidget(i,0,self.check_boxes_lower_table[i])
				self.CompanyTable.setItem(i, 1, QTableWidgetItem(str(self.company_details[i][0])))
				self.CompanyTable.setItem(i, 2, QTableWidgetItem(str(self.company_details[i][1])))
				self.CompanyTable.setItem(i, 3, QTableWidgetItem(str(self.company_details[i][2])))
				self.CompanyTable.setItem(i, 4, QTableWidgetItem(str(self.company_details[i][3])))
				self.CompanyTable.setItem(i, 5, QTableWidgetItem(str(self.company_details[i][4])))
				self.CompanyTable.setItem(i, 6, QTableWidgetItem(str(self.company_details[i][5])))
				self.CompanyTable.setItem(i, 7, QTableWidgetItem(str(self.company_details[i][6])))

	def change_all_states(self):
		if self.PaymentsAllCheck.isChecked():
			for n in range(len(self.check_states)):
				self.check_states[n].setChecked(True)
		else:
			for n in range(len(self.check_states)):
				self.check_states[n].setChecked(False)

	def change_all_states_lower_table(self):
		try:
			if self.CompanyAllCheck.isChecked():
				for n in range(len(self.check_states_lower_table)):
					self.check_states_lower_table[n].setChecked(True)
			else:
				for n in range(len(self.check_states_lower_table)):
					self.check_states_lower_table[n].setChecked(False)
		except:
			pass

	def load_data_from_email_config(self):
		fields = []
		key = load_key()
		file = "Data/EmailConfig.txt"
		decrypt(file, key)
		with open('Data/EmailConfig.txt', 'r',encoding='utf-8') as f:
			line = f.readline()
			while line != "":
				line = line[:-1]
				fields.append(line)
				line = f.readline()
		encrypt(file, key)
		return fields

	def test_email(self):
		cursor = self.cnxn.cursor()
		cursor.execute("select adr_NazwaPelna, adr_Ulica, adr_NrDomu, adr_NrLokalu, adr_Kod, adr_Miejscowosc, adr_NIP, rb_Nazwa, rb_Numer, adr_Telefon from adr__Ewid join rb__RachBankowy on rb__RachBankowy.rb_IdObiektu = adr__Ewid.adr_IdObiektu where adr_TypAdresu=8 and adr_IdObiektu = 1 and rb_Podstawowy = 1 and rb_TypObiektu=0")
		database_data = [n for n in cursor]
		user = [database_data[0][n] for n in range(len(database_data[0]))]
		today = date.today()
		today = today.strftime("%d.%m.%Y")
		fields = self.load_data_from_email_config()

		email, okPressed = QInputDialog.getText(self, "Windykator", "Podaj mail do którego ma zostać wysłana wiadomość testowa:", QLineEdit.Normal, "")
		if okPressed and email != '':
			try:
				sender_email = fields[2]
				receiver_email = email
				password = fields[4]

				#Create MIMEMultipart object
				msg = MIMEMultipart("alternative")
				msg["Subject"] = "Test"
				if fields[5] != "":
					msg["From"] = fields[5]
				else:
					msg["From"] = fields[2]
				msg["To"] = receiver_email

				#HTML Message Part
				try:
					if len(self.html_emails) == 1:
						html = self.html_emails[0]
				except:
					msg = QMessageBox()
					msg.setText("Aby wysłać wiadomość testową należy wygenerować wezwanie tylko do jednego klienta!")
					msg.setIcon(QMessageBox.Critical)
					x = msg.exec_()
					return

				try:
					part = MIMEText(html, "html")
				except:
					msg = QMessageBox()
					msg.setText("Aby wysłać wiadomość testową należy wygenerować wezwanie tylko do jednego klienta!")
					msg.setIcon(QMessageBox.Critical)
					x = msg.exec_()
					return
				msg.attach(part)

				# Create secure SMTP connection and send email
				server = smtplib.SMTP(fields[1], int(fields[3]))
				server.ehlo()
				server.starttls()
				server.ehlo()
				server.login(sender_email, password)
				server.sendmail(
					sender_email, receiver_email, msg.as_string()
				)
				msg = QMessageBox()
				msg.setText(f"Wiadomość została poprawnie wysłana na email: {email}")
				x = msg.exec_()
			except Exception as e:
				print(e)
				msg = QMessageBox()
				msg.setText(str(e))
				msg.setIcon(QMessageBox.Critical)
				x = msg.exec_()
				return

	def send_email(self):
		self.err = ""
		self.a = MyWarnings(f"Wysyłanie...")
		self.a.show()
		self.helper = Helper()
		self.helper.finished.connect(self.joining)
		self.helper.finished.connect(self.a.close)
		self.t1 = threading.Thread(target=self.sending_email,args=(self.helper, ))
		self.t1.start()

	def joining(self):
		self.t1.join()

	def sending_email(self, helper):
		#fields = ['NIP', 'Serwer poczty', 'mail-główny', 'port', 'hasło', 'Nazwa użytkownika', 'email-pomocniczy']
		try:
			fields = self.load_data_from_email_config()
			emails = []
			for i in range(1, len(self.adr_symbol)):
				for j in range(len(self.customers_data)):
					if self.adr_symbol[i] == self.customers_data[j][0]:
						emails.append(self.customers_data[j][8])
		except:
			self.a.widget2.setText("BŁĄD!")
			self.err = "Nie wykryto email'a odbiorcy lub maile nie zostały wygenerowane! Zaznacz w górnej tablicy poprawnego odbiorce"

		if len(emails) == 0 and self.err == "":
			self.a.widget2.setText("BŁĄD!")
			self.err = "Nie wykryto email'a odbiorcy lub maile nie zostały wygenerowane! Zaznacz w górnej tablicy poprawnego odbiorce"

		if len(self.html_emails) == 0 and self.err == "":
			self.a.widget2.setText("BŁĄD!")
			self.err = "Brak wygenerowanych wiadomości!"

		if self.err == "":
			sender_email = fields[2]
			password = fields[4]
			try:
				# Create secure SMTP connection and send email
				server = smtplib.SMTP(fields[1], int(fields[3]))
				server.ehlo()
				server.starttls()
				server.ehlo()
				server.login(sender_email, password)
			except Exception as e:
				self.a.widget2.setText("BŁĄD!")
				self.err = str(e)
			if self.err == "":
				for i in range(len(self.html_emails)):
					receiver_email = emails[i]
					self.a.widget2.setText(f"Pozostało do wysłania: {len(self.html_emails)-i}\nAktualnie wysyłanie do: {receiver_email}")
					#Create MIMEMultipart object
					msg = MIMEMultipart("alternative")
					msg["Subject"] = self.szablonCombo.currentText()
					if fields[5] != "":
						msg["From"] = fields[5]
					else:
						msg["From"] = fields[2]
					msg["To"] = receiver_email

					html = self.html_emails[i]

					part = MIMEText(html, "html")
					msg.attach(part)
					try:
						server.sendmail(
							sender_email, receiver_email, msg.as_string()
						)
					except Exception as e:
						self.a.widget2.setText("BŁĄD!")
						self.err = str(e)
						break
			if fields[6] != "" and self.err == "":
				for i in range(len(self.html_emails)):
					receiver_email = fields[6]
					self.a.widget2.setText(f"Kopia - Pozostało do wysłania: {len(self.html_emails)-i}\nAktualnie wysyłanie do: {receiver_email}")
					#Create MIMEMultipart object
					msg = MIMEMultipart("alternative")
					msg["Subject"] = f"{self.szablonCombo.currentText()} - {emails[i]}"
					if fields[5] != "":
						msg["From"] = fields[5]
					else:
						msg["From"] = fields[2]
					msg["To"] = receiver_email

					html = self.html_emails[i]

					part = MIMEText(html, "html")
					msg.attach(part)
					try:
						server.sendmail(
							sender_email, receiver_email, msg.as_string()
						)
					except Exception as e:
						self.a.widget2.setText("BŁĄD!")
						self.err = str(e)
						break
			try:
				server.quit()
			except:
				pass
		if self.err == "":
			self.helper.finished.connect(self.end_of_sending_mail)
		else:
			self.helper.finished.connect(self.bad_end_of_sending_mail)
		helper.finished.emit()

	def end_of_sending_mail(self):
		msg = QMessageBox()
		msg.setText(f"Wszystkie wiadomości zostały wysłane poprawnie")
		x = msg.exec_()

	def bad_end_of_sending_mail(self):
		msg = QMessageBox()
		msg.setText(self.err)
		msg.setIcon(QMessageBox.Critical)
		x = msg.exec_()

	def quit(self):
		try:
			QtCore.QCoreApplication.quit()
			status = QtCore.QProcess.startDetached(sys.executable, sys.argv)
		except:
			pass

	def create_emails(self):
		cursor = self.cnxn.cursor()
		cursor.execute("select adr_NazwaPelna, adr_Ulica, adr_NrDomu, adr_NrLokalu, adr_Kod, adr_Miejscowosc, adr_NIP, rb_Nazwa, rb_Numer, adr_Telefon from adr__Ewid join rb__RachBankowy on rb__RachBankowy.rb_IdObiektu = adr__Ewid.adr_IdObiektu where adr_TypAdresu=8 and adr_IdObiektu = 1 and rb_Podstawowy = 1 and rb_TypObiektu=0")
		database_data = [n for n in cursor]
		user = [database_data[0][n] for n in range(len(database_data[0]))]
		upper_table_current_states = [n for n in range(len(self.check_states)) if self.check_states[n].isChecked()]
		lower_table_current_states = [n for n in range(len(self.check_states_lower_table)) if self.check_states_lower_table[n].isChecked()]
		self.adr_symbol = ["PUSTY"]
		lower_symbols = []
		for n in lower_table_current_states:
			lower_symbols.append(self.company_details[n][0])
		for n in upper_table_current_states:
			if self.customers_data[n][0] in lower_symbols:
				self.adr_symbol.append(self.customers_data[n][0])
		self.adr_symbol = tuple(self.adr_symbol)
		data_to_send = []
		for i in upper_table_current_states:
			temp = []
			for j in lower_table_current_states:
				if self.company_details[j][0] == self.customers_data[i][0]:
					temp.append(self.company_details[j])
			if len(temp) != 0:
				data_to_send.append(temp[:])
		try:
			cursor.execute(f"""
			select adr_Symbol, adr_Nazwa, adr_adres, adr_Kod, adr_Miejscowosc, adr_NIP as Il_dok, am_Email 
			from vwFinanseRozrachunkiWgDokumentow bk LEFT JOIN adr__Ewid AS Adresy ON Bk.nzf_IdAdresu=Adresy.adr_Id LEFT JOIN adr_Email ON adr_Email.am_IdAdres = Adresy.adr_Id 
			WHERE ((Rozliczenie IN (0, 1)) AND ( ( nzf_Status = 1 AND nzf_Typ IN (39, 40) OR nzf_Typ NOT IN (39, 40) ) ) ) AND (nzf_Typ in (39,40)) 
			and naleznosc is not NULL and adr_Symbol in {self.adr_symbol} GROUP BY adr_Symbol, adr_Nazwa, adr_adres, adr_Kod, adr_Miejscowosc, adr_NIP, am_Email
			""")
		except:
			msg = QMessageBox()
			msg.setText("Nie wybrano klientów dla których miały wygenerować się maile!")
			msg.setIcon(QMessageBox.Critical)
			x = msg.exec_()
			return
		database_data = [n for n in cursor]
		company_data = []
		for i in range(1, len(self.adr_symbol)):
			for n in range(len(database_data)):
				if database_data[n][0] == self.adr_symbol[i]:
					company_data.append(database_data[n])
		if len(data_to_send[0]) == 0:
			msg = QMessageBox()
			msg.setText("Nie możesz wysłać danych do klientów, do których nie powinny zostać one wysłane!")
			msg.setIcon(QMessageBox.Critical)
			x = msg.exec_()
			return
		total_to_pay = []
		self.html_emails = []
		for i in range(len(data_to_send)):
			total = 0
			for j in range(len(data_to_send[i])):
				total += float(data_to_send[i][j][5].replace(" ", ""))
			total = str(round(total, 2))
			total = total.split(".")
			if len(total[1]) != 2:
				total[1] += "0"
			if len(total[0]) > 3:
				total[0] = list(total[0])
				total[0][-4] += " "
				total[0] = "".join(total[0])
			if len(total[0]) > 7:
				total[0] = list(total[0])
				total[0][-8] += " "
			if len(total[0]) > 11:
				total[0] = list(total[0])
				total[0][-12] += " "
				total[0] = "".join(total[0])
			total = ".".join(total)
			total_to_pay.append(total)
		self.receiverCombo.clear()
		for i in range(1,len(self.adr_symbol)):
			self.receiverCombo.addItem(self.adr_symbol[i])
		for i in range(len(data_to_send)):
			today = date.today()
			today = today.strftime("%d.%m.%Y")
			row = ""
			for j in range(len(data_to_send[i])):
				row += f"<TR><TD align=left>{data_to_send[i][j][1]}</TD><TD align=left>{data_to_send[i][j][2]}</TD><TD align=left>{data_to_send[i][j][3]}</TD><TD align=right>{data_to_send[i][j][4]}</TD><TD align=right>{data_to_send[i][j][5]}</TD><TD align=right>{data_to_send[i][j][6]}</TD></TR>"
			if self.szablonCombo.currentText() == "Wezwanie do zapłaty":
				#Wezwanie do zapłaty
				self.html_emails.append(f'<div style="font-family: Arial;"><P align=right>{user[5]}, {today}</P><P align=left><FONT face="Arial", color="black"><STRONG>Wystawca:</STRONG></FONT></P><BLOCKQUOTE style="MARGIN-RIGHT: 0px" dir=ltr><P align=left><FONT face="Arial", color="black">{user[0]}<BR>{user[1]} {user[2]}/{user[3]}, {user[4]} {user[5]}<BR>NIP: {user[6]}<BR>Bank: {user[7]}<BR>Numer konta: {user[8]}<BR>tel. {user[9]}</FONT></P></BLOCKQUOTE><P align=left><STRONG><FONT face="Arial", color="black">Dłużnik:</FONT></STRONG></P><BLOCKQUOTE style="MARGIN-RIGHT: 0px" dir=ltr><P align=left>{company_data[i][1]}<BR>{company_data[i][2]}, {company_data[i][3]} {company_data[i][4]}<BR>NIP: {company_data[i][5]}</P></BLOCKQUOTE><P align=center><STRONG><FONT size=4 face="Arial", color="black">WEZWANIE DO ZAPŁATY</FONT></STRONG>&nbsp;</P><P align=left>Zawiadamiamy, że do dnia dzisiejszego nie została dokonana zapłata kwoty {total_to_pay[i]} PLN, zgodnie z poniższym wykazem:</P><P align=center><TABLE border=1 cellpadding=5 style="border: solid black 1px; border-collapse: collapse;"><TR><TH>Data Powstania </TH><TH>Dokument</TH><TH>Termin Płatności</TH><TH>Dni Spóźnienia</TH><TH>Należność</TH><TH>Należność Pierwotna</TH></TR>{row}</TABLE></P><P align=left>Prosimy o dokonanie zapłaty powyższej kwoty na rachunek bankowy: {user[8]} ({user[7]})</P></div>')
			if self.szablonCombo.currentText() == "Termin dziś":
				#Termin dzis
				self.html_emails.append(f'<div style="font-family: Arial;"><P align=right>{user[5]}, {today}</P><P align=left><FONT face="Arial", color="black"><STRONG>Wystawca:</STRONG></FONT></P><BLOCKQUOTE style="MARGIN-RIGHT: 0px" dir=ltr><P align=left><FONT face="Arial", color="black">{user[0]}<BR>{user[1]} {user[2]}/{user[3]}, {user[4]} {user[5]}<BR>NIP: {user[6]}<BR>Bank: {user[7]}<BR>Numer konta: {user[8]}<BR>tel. {user[9]}</FONT></P></BLOCKQUOTE><P align=left><STRONG><FONT face="Arial", color="black">Dłużnik:</FONT></STRONG></P><BLOCKQUOTE style="MARGIN-RIGHT: 0px" dir=ltr><P align=left>{company_data[i][1]}<BR>{company_data[i][2]}, {company_data[i][3]} {company_data[i][4]}<BR>NIP: {company_data[i][5]}</P></BLOCKQUOTE><P align=center><STRONG><FONT size=4 face="Arial", color="black">PRZYPOMNIENIE O PŁATNOŚCI</FONT></STRONG>&nbsp;</P><P align=left>Uprzejmie przypominamy, że dziś przypada termin zapłaty następujących faktur:</P><P align=center><TABLE border=1 cellpadding=5 style="border: solid black 1px; border-collapse: collapse;"><TR><TH>Data Powstania </TH><TH>Dokument</TH><TH>Termin Płatności</TH><TH>Dni Spóźnienia</TH><TH>Należność</TH><TH>Należność Pierwotna</TH></TR>{row}</TABLE></P><P align=left>Serdecznie dziękujemy jeśli zapłaciliście już Państwo za te faktury. <br><br>Jeżeli płatność jeszcze nie została uregulowana, prosimy o dokonanie zapłaty w dniu dzisiejszym na  rachunek bankowy: {user[8]} ({user[7]})<br>Jeśli mimo tego przypomnienia stwierdzą Państwo, że nie są w stanie zapłacić ww faktur, prosimy o informację zwrotną na temat planowanego terminu zapłaty.<br><br>Pozdrawiamy.</P></div>')
			if self.szablonCombo.currentText() == "Przypomnienie":
				#Przypomnienie
				self.html_emails.append(f'<div style="font-family: Arial;"><P align=right>{user[5]}, {today}</P><P align=left><FONT face="Arial", color="black"><STRONG>Wystawca:</STRONG></FONT></P><BLOCKQUOTE style="MARGIN-RIGHT: 0px" dir=ltr><P align=left><FONT face="Arial", color="black">{user[0]}<BR>{user[1]} {user[2]}/{user[3]}, {user[4]} {user[5]}<BR>NIP: {user[6]}<BR>Bank: {user[7]}<BR>Numer konta: {user[8]}<BR>tel. {user[9]}</FONT></P></BLOCKQUOTE><P align=left><STRONG><FONT face="Arial", color="black">Dłużnik:</FONT></STRONG></P><BLOCKQUOTE style="MARGIN-RIGHT: 0px" dir=ltr><P align=left>{company_data[i][1]}<BR>{company_data[i][2]}, {company_data[i][3]} {company_data[i][4]}<BR>NIP: {company_data[i][5]}</P></BLOCKQUOTE><P align=center><STRONG><FONT size=4 face="Arial", color="black">PRZYPOMNIENIE O PŁATNOŚCI</FONT></STRONG>&nbsp;</P><P align=left>Zawiadamiamy, że do dnia dzisiejszego nie zostały uregulowane należności w kwocie {total_to_pay[i]} PLN, wynikające z następujących dokumentów:</P><P align=center><TABLE border=1 cellpadding=5 style="border: solid black 1px; border-collapse: collapse;"><TR><TH>Data Powstania </TH><TH>Dokument</TH><TH>Termin Płatności</TH><TH>Dni Spóźnienia</TH><TH>Należność</TH><TH>Należność Pierwotna</TH></TR>{row}</TABLE></P><P align=left>Prosimy o niezwłoczne dokonanie zapłaty ww kwoty na rachunek bankowy:{user[8]} ({user[7]})<br>Jeśli z jakiejś przyczyny, szybka zapłata nie jest możliwa, prosimy - w odpowiedzi na tego maila -  o określenie terminu zapłaty. </P></div>')

	def edit_email(self):
		try:
			if len(self.html_emails) != 0:
				id = self.adr_symbol.index(self.receiverCombo.currentText()) - 1
				window = Editor.RTE(self.html_emails, id)
				Dialog = QDialog()
				window.editor.setText(self.html_emails[id])
				Dialog.show()
			else:
				msg = QMessageBox()
				msg.setText("Żadne maile nie zostały wygenerowane!")
				msg.setIcon(QMessageBox.Critical)
				x = msg.exec_()
				return
		except:
			msg = QMessageBox()
			msg.setText("Żadne maile nie zostały wygenerowane!")
			msg.setIcon(QMessageBox.Critical)
			x = msg.exec_()
			return

	def config_email(self):
		self.config.load_config_data()
		self.widget.setCurrentIndex(2)

def main():
	if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
		QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
	if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
		QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

	app = QApplication(sys.argv)
	widget = QtWidgets.QStackedWidget()

	mainwindow = MainWindow() #0

	widget.addWidget(mainwindow)

	widget.setFixedWidth(900)
	widget.setFixedHeight(700)
	widget.show()

	try:
		sys.exit(app.exec_())
	except:
		print("")

if __name__ == "__main__":
	main()