from PyQt5 import QtCore as qtc
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import uic


class SoundList(qtw.QWidget):
    song_selected = qtc.pyqtSignal(str)
    volumeChanged = qtc.pyqtSignal(int)

    def __init__(self):
        super().__init__()
        uic.loadUi("src/ui/soundlist.ui", self)
        self.setMinimumSize(200, 250)
        self.loaded_songs = self.findChild(qtw.QListWidget, "loaded_songs")
        self.curr_volume_gain = 0

        self.loaded_songs.itemDoubleClicked.connect(self.changeCurrSong)
        self.loaded_songs.currentItemChanged.connect(self.updateSelected)
        self.volume_slider.valueChanged.connect(self.updateVolume)

    def addNewSong(self, name):
        songs_list = self.loaded_songs
        item = qtw.QListWidgetItem(songs_list)
        item_widget = qtw.QLabel(name)
        item.setSizeHint(item_widget.sizeHint())
        item_widget.setStyleSheet("""
            font-family: TeX Gyre Schola;
            font-size: 11;
            text-align: right;
            background-color: rgba(255, 255, 255, 0);
        """)

        item_widget.setAlignment(qtc.Qt.AlignCenter)
        songs_list.addItem(item)
        songs_list.setItemWidget(item, item_widget)

    def songsNum(self):
        return self.loaded_songs.count()

    def changeCurrSong(self, new_song):
        self.loaded_songs.setCurrentItem(new_song)

    def updateSelected(self, curr_song, previous_song):
        color = qtg.QBrush()
        color.setColor(qtg.QColor("#2a8aff"))
        curr_song.setBackground(color)
        self.song_selected.emit(self.loaded_songs.itemWidget(curr_song).text())

    def updateVolume(self, volume):
        self.curr_volume_gain = volume
        self.volumeChanged.emit(self.curr_volume_gain)
