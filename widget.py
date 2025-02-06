import sys
from datetime import datetime
from PySide6.QtWidgets import (QMainWindow, QApplication, QFileDialog,
                             QMessageBox, QFontDialog, QColorDialog, QDialog,
                             QTextEdit, QLabel, QPushButton, QVBoxLayout, QWidget)
from PySide6.QtCore import Qt, QFile, QTextStream
from PySide6.QtGui import QTextCharFormat, QColor, QPageLayout, QTextCursor, QFont, QPalette
from PySide6.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
from PySide6.QtUiTools import QUiLoader

class FindReplaceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Find and Replace")
        self.setModal(False)

        # Create widgets
        self.find_label = QLabel("Find:")
        self.find_text = QTextEdit()
        self.find_text.setMaximumHeight(30)
        self.replace_label = QLabel("Replace with:")
        self.replace_text = QTextEdit()
        self.replace_text.setMaximumHeight(30)

        self.find_button = QPushButton("Find Next")
        self.replace_button = QPushButton("Replace")
        self.replace_all_button = QPushButton("Replace All")

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.find_label)
        layout.addWidget(self.find_text)
        layout.addWidget(self.replace_label)
        layout.addWidget(self.replace_text)
        layout.addWidget(self.find_button)
        layout.addWidget(self.replace_button)
        layout.addWidget(self.replace_all_button)

        self.setLayout(layout)

        # Connect signals
        self.find_button.clicked.connect(self.find_text_action)
        self.replace_button.clicked.connect(self.replace_text_action)
        self.replace_all_button.clicked.connect(self.replace_all_action)

    def find_text_action(self):
        text = self.find_text.toPlainText()
        if not self.parent.textEdit.find(text):
            # If text not found, wrap around to beginning
            cursor = self.parent.textEdit.textCursor()
            cursor.movePosition(QTextCursor.Start)
            self.parent.textEdit.setTextCursor(cursor)
            if not self.parent.textEdit.find(text):
                QMessageBox.information(self, "Not Found",
                                     f"Cannot find '{text}'")

    def replace_text_action(self):
        cursor = self.parent.textEdit.textCursor()
        if cursor.hasSelection():
            cursor.insertText(self.replace_text.toPlainText())

    def replace_all_action(self):
        text = self.find_text.toPlainText()
        replace_with = self.replace_text.toPlainText()
        content = self.parent.textEdit.toPlainText()
        new_content = content.replace(text, replace_with)
        self.parent.textEdit.setPlainText(new_content)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.load_ui()
        self.current_file = None
        self.zoom_factor = 1.0
        self.last_background_color = QColor('white')
        self.setup_connections()

    def load_ui(self):
        loader = QUiLoader()
        ui_file = QFile("form.ui")
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file)
        ui_file.close()

        # Set the central widget to be the loaded UI
        self.setCentralWidget(self.ui.centralWidget())
        self.setMenuBar(self.ui.menubar)
        self.setStatusBar(self.ui.statusbar)
        self.addToolBar(self.ui.toolBar)

        # Store reference to text edit widget
        self.textEdit = self.ui.textEdit

    def setup_connections(self):
        # File menu
        self.ui.actionNew.triggered.connect(self.new_file)
        self.ui.actionOpen.triggered.connect(self.open_file)
        self.ui.actionSave.triggered.connect(self.save_file)
        self.ui.actionSave_As.triggered.connect(self.save_as_file)
        self.ui.actionPrint.triggered.connect(self.print_file)
        self.ui.actionPrint_Preview.triggered.connect(self.print_preview)
        self.ui.actionExport_PDF.triggered.connect(self.export_pdf)
        self.ui.actionExit.triggered.connect(self.close)

        # Edit menu
        self.textEdit.undoAvailable.connect(self.ui.actionUndo.setEnabled)
        self.textEdit.redoAvailable.connect(self.ui.actionRedo.setEnabled)
        self.ui.actionUndo.triggered.connect(self.textEdit.undo)
        self.ui.actionRedo.triggered.connect(self.textEdit.redo)
        self.ui.actionCut.triggered.connect(self.textEdit.cut)
        self.ui.actionCopy.triggered.connect(self.textEdit.copy)
        self.ui.actionPaste.triggered.connect(self.textEdit.paste)
        self.ui.actionFind.triggered.connect(self.show_find_dialog)
        self.ui.actionReplace.triggered.connect(self.show_find_dialog)
        self.ui.actionSelect_All.triggered.connect(self.textEdit.selectAll)
        self.ui.actionInsert_Date_Time.triggered.connect(self.insert_datetime)

        # Format menu
        self.ui.actionWord_Wrap.triggered.connect(self.toggle_word_wrap)
        self.ui.actionFont.triggered.connect(self.choose_font)
        self.ui.actionText_Color.triggered.connect(self.choose_text_color)
        self.ui.actionBackground_Color.triggered.connect(self.choose_background_color)

        # Style actions
        self.ui.actionBold.triggered.connect(lambda: self.format_text('bold'))
        self.ui.actionItalic.triggered.connect(lambda: self.format_text('italic'))
        self.ui.actionUnderline.triggered.connect(lambda: self.format_text('underline'))
        self.ui.actionStrikethrough.triggered.connect(lambda: self.format_text('strikethrough'))

        # Alignment actions
        self.ui.actionAlign_Left.triggered.connect(lambda: self.textEdit.setAlignment(Qt.AlignLeft))
        self.ui.actionAlign_Center.triggered.connect(lambda: self.textEdit.setAlignment(Qt.AlignCenter))
        self.ui.actionAlign_Right.triggered.connect(lambda: self.textEdit.setAlignment(Qt.AlignRight))
        self.ui.actionAlign_Justify.triggered.connect(lambda: self.textEdit.setAlignment(Qt.AlignJustify))

        # View menu
        self.ui.actionZoom_In.triggered.connect(self.zoom_in)
        self.ui.actionZoom_Out.triggered.connect(self.zoom_out)
        self.ui.actionReset_Zoom.triggered.connect(self.reset_zoom)
        self.ui.actionShow_Status_Bar.triggered.connect(self.toggle_statusbar)
        self.ui.actionShow_Toolbar.triggered.connect(self.toggle_toolbar)

        # Help menu
        self.ui.actionAbout.triggered.connect(self.show_about)
        self.ui.actionCheck_Updates.triggered.connect(self.check_updates)

    def new_file(self):
        if self.maybe_save():
            self.textEdit.clear()
            self.current_file = None

    def open_file(self):
        if self.maybe_save():
            filename, _ = QFileDialog.getOpenFileName(self)
            if filename:
                self.load_file(filename)

    def save_file(self):
        if self.current_file:
            return self.save_file_to(self.current_file)
        return self.save_as_file()

    def save_as_file(self):
        filename, _ = QFileDialog.getSaveFileName(self)
        if filename:
            return self.save_file_to(filename)
        return False

    def save_file_to(self, filename):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.textEdit.toPlainText())
            self.current_file = filename
            return True
        except Exception as e:
            QMessageBox.warning(self, "Save Error", f"Could not save file: {str(e)}")
            return False

    def load_file(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.textEdit.setPlainText(f.read())
            self.current_file = filename
        except Exception as e:
            QMessageBox.warning(self, "Load Error", f"Could not load file: {str(e)}")

    def maybe_save(self):
        if not self.textEdit.document().isModified():
            return True

        ret = QMessageBox.warning(self, "Application",
                                "The document has been modified.\n"
                                "Do you want to save your changes?",
                                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)

        if ret == QMessageBox.Save:
            return self.save_file()
        elif ret == QMessageBox.Cancel:
            return False
        return True

    def print_file(self):
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)

        if dialog.exec_() == QPrintDialog.Accepted:
            self.textEdit.print_(printer)

    def print_preview(self):
        printer = QPrinter(QPrinter.HighResolution)
        preview = QPrintPreviewDialog(printer, self)
        preview.paintRequested.connect(lambda p: self.textEdit.print_(p))
        preview.exec_()

    def export_pdf(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Export PDF", None, "PDF files (*.pdf)")
        if filename:
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(filename)
            self.textEdit.print_(printer)

    def show_find_dialog(self):
        dialog = FindReplaceDialog(self)
        dialog.show()

    def insert_datetime(self):
        datetime_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.textEdit.insertPlainText(datetime_str)

    def toggle_word_wrap(self):
        self.textEdit.setLineWrapMode(
            QTextEdit.NoWrap if self.textEdit.lineWrapMode() == QTextEdit.WidgetWidth
            else QTextEdit.WidgetWidth
        )

    def choose_font(self):
        current = self.textEdit.currentFont()
        font, ok = QFontDialog.getFont(current, self)
        if ok:
            self.textEdit.setCurrentFont(font)

    def choose_text_color(self):
        color = QColorDialog.getColor(self.textEdit.textColor(), self)
        if color.isValid():
            self.textEdit.setTextColor(color)

    def choose_background_color(self):
        color = QColorDialog.getColor(self.last_background_color, self)
        if color.isValid():
            self.last_background_color = color
            cursor = self.textEdit.textCursor()
            if cursor.hasSelection():
                fmt = QTextCharFormat()
                fmt.setBackground(color)
                cursor.mergeCharFormat(fmt)
            else:
                self.textEdit.setStyleSheet(f"QTextEdit {{ background-color: {color.name()}; }}")

    def create_palette(self, color):
        palette = self.textEdit.palette()
        palette.setColor(self.textEdit.backgroundRole(), color)
        return palette

    def format_text(self, format_type):
        cursor = self.textEdit.textCursor()
        text_format = cursor.charFormat()

        if format_type == 'bold':
            text_format.setFontWeight(
                QFont.Bold if text_format.fontWeight() != QFont.Bold
                else QFont.Normal
            )
        elif format_type == 'italic':
            text_format.setFontItalic(not text_format.fontItalic())
        elif format_type == 'underline':
            text_format.setFontUnderline(not text_format.fontUnderline())
        elif format_type == 'strikethrough':
            text_format.setFontStrikeOut(not text_format.fontStrikeOut())

        cursor.mergeCharFormat(text_format)
        self.textEdit.setTextCursor(cursor)

    def zoom_in(self):
        self.zoom_factor *= 1.2
        self.textEdit.setZoomFactor(self.zoom_factor)

    def zoom_out(self):
        self.zoom_factor /= 1.2
        self.textEdit.setZoomFactor(self.zoom_factor)

    def reset_zoom(self):
        self.zoom_factor = 1.0
        self.textEdit.setZoomFactor(self.zoom_factor)

    def toggle_statusbar(self):
        self.statusBar().setVisible(self.ui.actionShow_Status_Bar.isChecked())

    def toggle_toolbar(self):
        self.ui.toolBar.setVisible(self.ui.actionShow_Toolbar.isChecked())

    def show_about(self):
        QMessageBox.about(self, "About Notepadino",
                         "Notepadino v1.0\n\n"
                         "A notepad built with PySide6\n"
                         "Created by Zakaria Farih")

    def check_updates(self):
        QMessageBox.information(self, "Check for Updates",
                              "You are running the latest version.")

    def closeEvent(self, event):
        if self.maybe_save():
            event.accept()
        else:
            event.ignore()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
