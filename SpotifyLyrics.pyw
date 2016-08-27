from PyQt5 import QtCore, QtGui, QtWidgets
import backend
import time
from datetime import datetime
import threading
import os
import re

if os.name == "nt":
    import ctypes

    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("spotifylyrics.version1")


class Communicate(QtCore.QObject):
    signal = QtCore.pyqtSignal(str, str)


class Ui_Form(object):
    sync = False
    ontop = False
    if os.name == "nt":
        settingsdir = os.getenv("APPDATA") + "\\SpotifyLyrics\\"
    else:
        settingsdir = os.path.expanduser("~") + "/.SpotifyLyrics/"

    def __init__(self):
        super().__init__()

        self.comm = Communicate()
        self.comm.signal.connect(self.change_lyrics)
        self.setupUi(Form)
        self.set_style()
        self.load_save_settings()
        self.start_thread()

    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(550, 610)
        Form.setMinimumSize(QtCore.QSize(350, 310))
        self.gridLayout_2 = QtWidgets.QGridLayout(Form)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.topLayout = QtWidgets.QVBoxLayout()
        self.topLayout.setObjectName("horizontalLayout_2")
        self.label_songname = QtWidgets.QLabel(Form)
        self.label_songname.setObjectName("label_songname")
        self.label_songname.setOpenExternalLinks(True)
        self.topLayout.addWidget(self.label_songname, 0, QtCore.Qt.AlignCenter)  # Left | QtCore.Qt.AlignHCenter)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.topLayout.addItem(spacerItem)
        self.settingsLayout = QtWidgets.QHBoxLayout()
        self.settingsLayout.setObjectName("settingsLayout")
        self.comboBox = QtWidgets.QComboBox(Form)
        self.comboBox.setGeometry(QtCore.QRect(160, 120, 69, 22))
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.settingsLayout.addWidget(self.comboBox, 0, QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.fontBox = QtWidgets.QSpinBox(Form)
        self.fontBox.setMinimum(1)
        self.fontBox.setProperty("value", 10)
        self.fontBox.setObjectName("fontBox")
        self.settingsLayout.addWidget(self.fontBox, 0, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.topLayout.addLayout(self.settingsLayout)
        self.verticalLayout_2.addLayout(self.topLayout)
        self.textBrowser = QtWidgets.QTextBrowser(Form)
        self.textBrowser.setObjectName("textBrowser")
        self.textBrowser.setAcceptRichText(True)
        self.textBrowser.setStyleSheet("font-size: %spt;" % self.fontBox.value() * 2)
        self.textBrowser.setFontPointSize(self.fontBox.value())
        self.verticalLayout_2.addWidget(self.textBrowser)
        self.gridLayout_2.addLayout(self.verticalLayout_2, 2, 0, 1, 1)

        self.retranslateUi(Form)
        self.fontBox.valueChanged.connect(self.update_fontsize)
        self.comboBox.currentIndexChanged.connect(self.optionschanged)
        QtCore.QMetaObject.connectSlotsByName(Form)
        Form.setTabOrder(self.textBrowser, self.comboBox)
        Form.setTabOrder(self.comboBox, self.fontBox)

    def load_save_settings(self, save=False):
        settingsfile = self.settingsdir + "settings.ini"
        if save == False:
            if os.path.exists(settingsfile):
                with open(settingsfile, 'r') as settings:
                    for line in settings.readlines():
                        lcline = line.lower()
                        if "syncedlyrics" in lcline:
                            if "true" in lcline:
                                self.sync = True
                            else:
                                self.sync = False
                        if "alwaysontop" in lcline:
                            if "true" in lcline:
                                self.ontop = True
                            else:
                                self.ontop = False
                        if "fontsize" in lcline:
                            set = line.split("=", 1)[1].strip()
                            try:
                                self.fontBox.setValue(int(set))
                            except ValueError:
                                pass
            else:
                directory = os.path.dirname(settingsfile)
                if not os.path.exists(directory):
                    os.makedirs(directory)
                with open(settingsfile, 'w+') as settings:
                    settings.write("[settings]\nSyncedLyrics=False\nAlwaysOnTop=False\nFontSize=10")
            if self.sync == True:
                self.comboBox.setItemText(1, ("Synced Lyrics (on)"))
            if self.ontop == True:
                Form.setWindowFlags(Form.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
                self.comboBox.setItemText(2, ("Always on Top (on)"))
                Form.show()
        else:
            with open(settingsfile, 'w+') as settings:
                settings.write("[settings]\n")
                if self.sync == True:
                    settings.write("SyncedLyrics=True\n")
                else:
                    settings.write("SyncedLyrics=False\n")
                if self.ontop == True:
                    settings.write("AlwaysOnTop=True\n")
                else:
                    settings.write("AlwaysOnTop=False\n")
                settings.write("FontSize=%s" % str(self.fontBox.value()))

    def optionschanged(self):
        if self.comboBox.currentIndex() == 1:
            if self.sync == True:
                self.sync = False
                self.comboBox.setItemText(1, ("Synced Lyrics"))
            else:
                self.sync = True
                self.comboBox.setItemText(1, ("Synced Lyrics (on)"))
        elif self.comboBox.currentIndex() == 2:
            if self.ontop == False:
                self.ontop = True
                Form.setWindowFlags(Form.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
                self.comboBox.setItemText(2, ("Always on Top (on)"))
                Form.show()
            else:
                self.ontop = False
                Form.setWindowFlags(Form.windowFlags() & ~QtCore.Qt.WindowStaysOnTopHint)
                self.comboBox.setItemText(2, ("Always on Top"))
                Form.show()
        elif self.comboBox.currentIndex() == 3:
            self.load_save_settings(save=True)
        else:
            pass
        self.comboBox.setCurrentIndex(0)

    def set_style(self):
        if os.path.exists(self.settingsdir + "theme.ini"):
            themefile = self.settingsdir + "theme.ini"
        else:
            themefile = "theme.ini"
        if os.path.exists(themefile):
            with open(themefile, 'r') as theme:
                try:
                    for setting in theme.readlines():
                        lcsetting = setting.lower()
                        try:
                            set = setting.split("=", 1)[1].strip()
                        except IndexError:
                            set = ""
                        if "windowopacity" in lcsetting:
                            Form.setWindowOpacity(float(set))
                        if "backgroundcolor" in lcsetting:
                            Form.setStyleSheet("background-color: %s" % set)
                        if "lyricsbackgroundcolor" in lcsetting:
                            style = self.textBrowser.styleSheet()
                            style = style + "background-color: %s;" % set
                            self.textBrowser.setStyleSheet(style)
                        if "lyricstextcolor" in lcsetting:
                            style = self.textBrowser.styleSheet()
                            style = style + "color: %s;" % set
                            self.textBrowser.setStyleSheet(style)
                        if "songnamecolor" in lcsetting:
                            style = self.label_songname.styleSheet()
                            style = style + "color: %s;" % set
                            self.label_songname.setStyleSheet(style)
                        if "fontboxbackgroundcolor" in lcsetting:
                            style = self.fontBox.styleSheet()
                            style = style + "background-color: %s;" % set
                            self.comboBox.setStyleSheet(style)
                            self.fontBox.setStyleSheet(style)
                        if "fontboxtextcolor" in lcsetting:
                            style = self.fontBox.styleSheet()
                            style = style + "color: %s;" % set
                            self.comboBox.setStyleSheet(style)
                            self.fontBox.setStyleSheet(style)
                        if "songnameunderline" in lcsetting:
                            if "true" in set.lower():
                                style = self.label_songname.styleSheet()
                                style = style + "text-decoration: underline;"
                                self.label_songname.setStyleSheet(style)
                except Exception:
                    pass
        else:
            self.label_songname.setStyleSheet("color: black; text-decoration: underline;")
            pass

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def update_fontsize(self):
        self.textBrowser.setFontPointSize(self.fontBox.value())
        style = self.textBrowser.styleSheet()
        style = style.replace('%s' % style[style.find("font"):style.find("pt;") + 3], '')
        style = style.replace('p ', '')
        self.textBrowser.setStyleSheet(style + "p font-size: %spt;" % self.fontBox.value() * 2)
        lyrics = self.textBrowser.toPlainText()
        self.textBrowser.setText(lyrics)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Spotify Lyrics - {}".format(backend.version())))
        Form.setWindowIcon(QtGui.QIcon(self.resource_path('icon.png')))
        if backend.versioncheck() == True:
            self.label_songname.setText(_translate("Form", "Spotify Lyrics"))
        else:
            self.label_songname.setText(_translate("Form",
                                                   "Spotify Lyrics <style type=\"text/css\">a {text-decoration: none}</style><a href=\"https://github.com/fr31/spotifylyrics/releases\"><sup>(update)</sup></a>"))
        self.textBrowser.setText(_translate("Form", "Play a song in Spotify to fetch lyrics."))
        self.fontBox.setToolTip(_translate("Form", "Font Size"))
        self.comboBox.setItemText(0, _translate("Form", "Options"))
        self.comboBox.setItemText(1, _translate("Form", "Synced Lyrics"))
        self.comboBox.setItemText(2, _translate("Form", "Always on Top"))
        self.comboBox.setItemText(3, _translate("Form", "Save Settings"))

    def osx_lyrics_thread(self, comm):
        lyrics, url, timed = None, None, None

        oldsongname = ""
        style = self.label_songname.styleSheet()
        if style == "":
            color = "color: black"
        else:
            color = style
        while True:

            # keeps track of the closest verse in the future
            closest_index = 0

            # keeps track of how many seconds from the start
            # the closest verse in history is
            closest_timestamp = 10000

            songname = backend.getwindowtitle()

            # this part only handles song changes
            if oldsongname != songname:
                lyrics, url, timed = backend.getlyrics(songname, sync=self.sync)
                if songname != "Spotify" and songname != "":
                    oldsongname = songname
                    comm.signal.emit(songname, "Loading...")

                    if url == "":
                        header = songname
                    else:
                        header = '''<style type="text/css">a {text-decoration: none; %s}</style><a href="%s">%s</a>''' % (
                            color, url, songname)
                    if timed == False:
                        comm.signal.emit(header, lyrics)

            # under OS/X the title does not include position
            # so this part is required to be separate
            elif self.sync and timed:
                epoch = datetime(1970, 1, 1)
                output = []
                position = backend.get_position()

                for i, line in enumerate(lyrics.splitlines()):
                    timestamp = line.split("]")[0][1:]

                    # we can have multiple timestamps for repeated
                    # lines
                    repeats = []
                    if len(line.split("]")) > 2:
                        repeats = line.split("]")[1:-1]

                    rest = line.split("]")[-1].strip()
                    # if we can parse a datetime object, this is indeed a valid verse
                    try:
                        timestamp = datetime.combine(epoch, datetime.strptime("01:" + timestamp, "%H:%M:%S.%f").time())
                    # otherwise this is a metadata line we can ignore
                    except ValueError:
                        continue
                    repeats_ = []

                    # surround each of these with a try/except too because
                    # sometimes there might be ] characters in the title
                    # that don't come from timestamps
                    for s in repeats:
                        try:
                            repeats_.append(
                                datetime.combine(epoch, datetime.strptime("01:" + s[1:], "%H:%M:%S.%f").time()))
                        except ValueError:
                            pass
                    repeats = repeats_

                    # check all timestamps associated with the current line/verse
                    for stamp in [timestamp] + repeats:
                        # print(closest_timestamp, stamp.timestamp(), position)
                        # print("Seconds until this timestamp: %f" % (stamp.timestamp() - position))
                        # print("******")

                        # check that the stamp is in the future, but closer
                        # in future than our current candidate,
                        if closest_timestamp > stamp.timestamp() > position:
                            closest_timestamp = stamp.timestamp()
                            # we want the index right before the current line,
                            # but the timestamp of this line
                            closest_index = len(output) - 1

                    output.append("%s" % (rest))
                # if first_index != closest_index:
                print("Current line: @%d: %s" % (closest_index, output[closest_index]))
                output[
                    closest_index] = "<style type=\"text/css\">b {font-size: %spt}</style><b>%s</b>" % (
                    self.fontBox.value() * 2, output[closest_index])
                if closest_index >= 3:
                    output[closest_index - 3] += "<a name=\"#scrollHere\"></a>"
                comm.signal.emit(header, "<center>%s</center>" % "<br>".join(output))
                time.sleep(.3)

    def lyrics_thread(self, comm):
        if sys.platform == 'darwin':
            self.osx_lyrics_thread(comm)
        else:
            oldsongname = ""
            style = self.label_songname.styleSheet()
            if style == "":
                color = "color: black"
            else:
                color = style
            while True:
                songname = backend.getwindowtitle()
                if oldsongname != songname:
                    if songname != "Spotify" and songname != "":
                        oldsongname = songname
                        comm.signal.emit(songname, "Loading...")
                        start = time.time()
                        lyrics, url, timed = backend.getlyrics(songname, sync=self.sync)

                        if url == "":
                            header = songname
                        else:
                            header = '''<style type="text/css">a {text-decoration: none; %s}</style><a href="%s">%s</a>''' % (
                                color, url, songname)
                        if timed == True:
                            lrc = []
                            lyricsclean = ""
                            firstline = False
                            for line in lyrics.splitlines():
                                lrc.append(line)
                                if line.startswith(("[0", "[1", "[2")):
                                    firstline = True
                                    regex = re.compile('\[.+?\]')
                                    line = regex.sub('', line)
                                    lyricsclean = lyricsclean + line.strip() + "\n"
                                elif line == "" and firstline == True:
                                    lyricsclean = lyricsclean + "\n"
                            comm.signal.emit(header, lyricsclean)
                            count = -1
                            firstline = False
                            for line in lrc:
                                if line == "" and firstline == True:
                                    count += 1
                                if line.startswith(("[0", "[1", "[2")):
                                    firstline = True
                                    count += 1
                                    ltime = line[line.find("[") + 1:line.find("]")]
                                    add = float(ltime[0:2]) * 60
                                    try:
                                        ltime = float(ltime[3:])
                                    except ValueError:
                                        ltime = 0.0
                                    rtime = add + ltime - 0.5
                                    lyrics1 = lyricsclean.splitlines()
                                    regex = re.compile('\[.+?\]')
                                    line = regex.sub('', line)
                                    regex = re.compile('\<.+?\>')
                                    line = regex.sub('', line)
                                    lyrics1[count] = "<b>%s</b>" % line.strip()
                                    if count - 2 > 0:
                                        lyrics1[count - 2] = "<a name=\"#scrollHere\">%s</a>" % lyrics1[
                                            count - 2].strip()
                                    boldlyrics = '<br>'.join(lyrics1)
                                    while True:
                                        if rtime <= time.time() - start and backend.getwindowtitle() != "Spotify":
                                            boldlyrics = '<style type="text/css">p {font-size: %spt}</style><p>' % self.fontBox.value() * 2 + boldlyrics + '</p>'
                                            comm.signal.emit(header, boldlyrics)
                                            time.sleep(0.5)
                                            break
                                        elif backend.getwindowtitle() == "Spotify":
                                            time.sleep(0.2)
                                            start = start + 0.2
                                        else:
                                            if songname != backend.getwindowtitle():
                                                break
                                            else:
                                                time.sleep(0.2)
                                if songname != backend.getwindowtitle() and backend.getwindowtitle() != "Spotify":
                                    break
                        if timed == False:
                            comm.signal.emit(header, lyrics)

                time.sleep(1)

    def start_thread(self):
        lyricsthread = threading.Thread(target=self.lyrics_thread, args=(self.comm,))
        lyricsthread.daemon = True
        lyricsthread.start()

    def change_lyrics(self, songname, lyrics):
        _translate = QtCore.QCoreApplication.translate
        self.label_songname.setText(_translate("Form", songname))
        self.textBrowser.setText(_translate("Form", lyrics))
        self.textBrowser.scrollToAnchor("#scrollHere")


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    Form.show()
    sys.exit(app.exec_())
