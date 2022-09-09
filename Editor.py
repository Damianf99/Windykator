import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtPrintSupport import *
from PyQt5.QtCore import *

class RTE(QMainWindow, QDialog):
    def __init__(self, html_emails, id):
        super(RTE, self).__init__()
        self.editor = QTextEdit()
        self.fontSizeBox = QSpinBox()
        self.returned_html = ""
        self.html_emails = html_emails
        self.id = id
      
        font = QFont('Times', 11)
        self.editor.setFont(font)
        self.path = ""
        self.setCentralWidget(self.editor)
        self.setWindowTitle('Windykator')
        self.showMaximized()
        self.create_tool_bar()
        self.editor.setFontPointSize(24)
        
        
    def create_tool_bar(self):
        toolbar = QToolBar()
        
        save_action = QAction(QIcon('Pictures/save.png'),'Save', self)
        save_action.triggered.connect(self.saveFile)
        toolbar.addAction(save_action)
        
        undoBtn = QAction(QIcon('Pictures/undo.png'), 'undo', self)
        undoBtn.triggered.connect(self.editor.undo)
        toolbar.addAction(undoBtn)
        
        redoBtn = QAction(QIcon('Pictures/redo.png'), 'redo', self)
        redoBtn.triggered.connect(self.editor.redo)
        toolbar.addAction(redoBtn)
        
        copyBtn = QAction(QIcon('Pictures/copy.png'), 'copy', self)
        copyBtn.triggered.connect(self.editor.copy)
        toolbar.addAction(copyBtn)
        
        cutBtn = QAction(QIcon('Pictures/cut.png'), 'cut', self)
        cutBtn.triggered.connect(self.editor.cut)
        toolbar.addAction(cutBtn)
        
        pasteBtn = QAction(QIcon('Pictures/paste.png'), 'paste', self)
        pasteBtn.triggered.connect(self.editor.paste)
        toolbar.addAction(pasteBtn)
        
        
        self.fontBox = QComboBox(self)
        self.fontBox.addItems(["Courier Std", "Hellentic Typewriter Regular", "Helvetica", "Arial", "SansSerif", "Helvetica", "Times", "Monospace"])
        self.fontBox.activated.connect(self.setFont)
        toolbar.addWidget(self.fontBox)
        
        self.fontSizeBox.setValue(24)
        self.fontSizeBox.valueChanged.connect(self.setFontSize)
        toolbar.addWidget(self.fontSizeBox)
        
        rightAllign = QAction(QIcon('Pictures/right-align.png'), 'Right Allign', self)
        rightAllign.triggered.connect(lambda : self.editor.setAlignment(Qt.AlignRight))
        toolbar.addAction(rightAllign)
        
        leftAllign = QAction(QIcon('Pictures/left-align.png'), 'left Allign', self)
        leftAllign.triggered.connect(lambda : self.editor.setAlignment(Qt.AlignLeft))
        toolbar.addAction(leftAllign)
        
        centerAllign = QAction(QIcon('Pictures/center-align.png'), 'Center Allign', self)
        centerAllign.triggered.connect(lambda : self.editor.setAlignment(Qt.AlignCenter))
        toolbar.addAction(centerAllign)
        
        toolbar.addSeparator()
        
        boldBtn = QAction(QIcon('Pictures/bold.png'), 'Bold', self)
        boldBtn.triggered.connect(self.boldText)
        toolbar.addAction(boldBtn)
        
        underlineBtn = QAction(QIcon('Pictures/underline.png'), 'underline', self)
        underlineBtn.triggered.connect(self.underlineText)
        toolbar.addAction(underlineBtn)
        
        italicBtn = QAction(QIcon('Pictures/italic.png'), 'italic', self)
        italicBtn.triggered.connect(self.italicText)
        toolbar.addAction(italicBtn)
        
        
        self.addToolBar(toolbar)    
        
    def setFontSize(self):
        value = self.fontSizeBox.value()
        self.editor.setFontPointSize(value)
        
    def setFont(self):
        font = self.fontBox.currentText()
        self.editor.setCurrentFont(QFont(font))    
        
    def italicText(self):
        state = self.editor.fontItalic()
        self.editor.setFontItalic(not(state)) 
    
    def underlineText(self):
        state = self.editor.fontUnderline()
        self.editor.setFontUnderline(not(state))   
        
    def boldText(self):
        if self.editor.fontWeight != QFont.Bold:
            self.editor.setFontWeight(QFont.Bold)
            return
        self.editor.setFontWeight(QFont.Normal)         
    
    def saveFile(self): 
        self.html_emails[self.id] = self.editor.toHtml()
        msg = QMessageBox()
        msg.setText("Zapisano")
        x = msg.exec_()
            
    def file_saveas(self):
        self.path, _ = QFileDialog.getSaveFileName(self, "Save file", "", "text documents (*.text);Text documents (*.txt);All files (*.*)")
        if self.path == '':
            return   
        text = self.editor.toPlainText()
        try:
            with open(path, 'w') as f:
                f.write(text)
                #self.update_title()
        except Exception as e:
            print(e)   
            
def main():
	if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
		QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
	if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
		QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

	app = QApplication(sys.argv)
	window = RTE() #0
	window.show()

	try:
		sys.exit(app.exec_())
	except:
		print("")

if __name__ == "__main__":
	main()