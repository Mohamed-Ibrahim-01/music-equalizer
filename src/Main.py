import sys
import Utils
import qdarkstyle
from Page import Page
from PyQt5 import QtWidgets as qtw
from PyQt5 import uic
from SignalsStore import SignalsStore


class MainApp(qtw.QApplication):
    """The main application object"""

    def __init__(self, argv):
        super().__init__(argv)

        self.main_window = MainWindow()
        self.main_window.show()
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))


class MainWindow(qtw.QMainWindow):
    """The main application window"""

    def __init__(self):
        super().__init__()
        uic.loadUi("src/ui/main.ui", self)

        self.view_page = Page()
        self.sound_store = SignalsStore()
        self.initBody()
        self.initMenu()

    def initBody(self):
        self.view_page.stateChanged.connect(self.updateStatus)
        central_layout = self.centralWidget().layout()
        central_layout.addWidget(self.view_page)

    def updateStatus(self, msg):
        self.statusbar.clearMessage()
        self.statusbar.showMessage(msg)

    def initMenu(self):
        open_file = self.findChild(qtw.QAction, "actionLoad_Signal")
        open_file.setShortcut("Ctrl+O")
        open_file.triggered.connect(self.loadSound)

    def loadSound(self):
        loaded, name, path = Utils.openSound(self)
        if loaded:
            channel_idx = self.sound_store.addSignal((name, path))
            if channel_idx is not None:
                print(f"CHANNEL STORED in {channel_idx}")
            else:
                print("NOT A DICT SIGNAL")
        else:
            print("CSV NOT LOADED")


if __name__ == '__main__':
    app = MainApp(sys.argv)
    sys.exit(app.exec_())
