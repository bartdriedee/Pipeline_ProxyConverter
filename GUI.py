import PySide2.QtWidgets as QtWidgets
import PySide2.QtCore as QtCore
import PySide2.QtGui as QtGui
from watch_folder import FolderWatcher
import sys
import os


class ConverterGui(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(ConverterGui, self).__init__(parent)
        self.setMinimumSize(600,100)
        self.setWindowTitle("ConvertTo v1.00")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.files_converted = 0
        self.thread_running = False
        self.folder_message = "Enter a valid folder path"
        self.watchfolder_path = self.folder_message
        self.processed_files = ""
        self.format = "prores"

        self.createWidgets()
        self.createLayout()
        self.createConnections()
        self.updateStatusLabel()


    def createWidgets(self):
        print("create widgets")
        self.empty_line = QtWidgets.QLabel()

        self.lbl_watchfolder = QtWidgets.QLabel("Watching folder:")
        self.lne_watchfolder_path = QtWidgets.QLineEdit(self.folder_message)

        self.btn_set_folder = QtWidgets.QPushButton()
        self.btn_set_folder.setIcon(QtGui.QIcon("icons8-folder-40.png"))
        self.btn_set_folder.setFlat(True)

        self.rbn_prores = QtWidgets.QRadioButton("Prores proxy")
        self.rbn_prores.setChecked(True)
        self.rbn_h264 = QtWidgets.QRadioButton("H264")

        self.lbl_files_converted = QtWidgets.QLabel("Files converted:")

        self.lbl_counter = QtWidgets.QLabel(str(self.files_converted))
        self.lbl_counter.setAlignment(QtCore.Qt.AlignRight)

        self.lbl_status = QtWidgets.QLabel("Converting file:")
        self.lbl_current_file = QtWidgets.QLabel()
        self.lbl_current_file.setAlignment(QtCore.Qt.AlignRight)
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setAlignment(QtCore.Qt.AlignHCenter)
        self.txt_processed = QtWidgets.QTextEdit()

        self.btn_start_stop = QtWidgets.QPushButton("Start")
        self.btn_start_stop.setEnabled(False)

    def createLayout(self):
        print("create layout")
        self.folder_path_layout = QtWidgets.QHBoxLayout()
        self.folder_path_layout.addWidget(self.lne_watchfolder_path)
        self.folder_path_layout.addWidget(self.btn_set_folder)

        self.format_layout = QtWidgets.QHBoxLayout()
        self.format_layout.addWidget(self.rbn_h264)
        self.format_layout.addWidget(self.rbn_prores)

        self.folder_lbl_layout = QtWidgets.QHBoxLayout()
        self.folder_lbl_layout.addWidget(self.lbl_watchfolder)
        self.folder_lbl_layout.addStretch()

        self.counter_layout = QtWidgets.QHBoxLayout()
        self.counter_layout.addWidget(self.lbl_files_converted)
        self.counter_layout.addWidget(self.lbl_counter)

        self.status_layout = QtWidgets.QHBoxLayout()
        self.status_layout.addWidget(self.lbl_status)
        self.status_layout.addWidget(self.lbl_current_file)

        self.folder_layout = QtWidgets.QVBoxLayout()
        self.folder_layout.addLayout(self.folder_lbl_layout)
        self.folder_layout.addLayout(self.folder_path_layout)

        self.btn_layout = QtWidgets.QHBoxLayout()
        self.btn_layout.addStretch()
        self.btn_layout.addWidget(self.btn_start_stop)

        # top level layout gets self as parameter
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.addLayout(self.folder_layout)
        self.main_layout.addLayout(self.format_layout)
        self.main_layout.addWidget(self.empty_line)
        self.main_layout.addLayout(self.counter_layout)
        self.main_layout.addLayout(self.status_layout)
        self.main_layout.addWidget(self.progress_bar)
        self.main_layout.addWidget(self.txt_processed)
        self.main_layout.addLayout(self.btn_layout)

    def createConnections(self):
        print("create connetions")
        self.btn_set_folder.clicked.connect(self.clickSetFolder)
        self.btn_start_stop.clicked.connect(self.clickStartStop)
        self.rbn_prores.toggled.connect(self.proresToggled)
        self.rbn_h264.toggled.connect(self.h264Toggled)
        self.lne_watchfolder_path.editingFinished.connect(self.editPath)

    def proresToggled(self):
        print("prores")
        self.format = "prores"

    def h264Toggled(self):
        print("h264")
        self.format = "h264"

    def addToCounter(self):
        self.files_converted +=1
        self.lbl_counter.setText(str(self.files_converted))

    def addToProccesed(self, file):
        txt = []
        txt.append(self.processed_files)
        txt.append("\n")
        txt.append(file)
        self.processed_files = r"".join(txt)
        self.txt_processed.setText(self.processed_files)

    def updateStatusLabel(self, filename=None):
        if filename is None:
            if self.thread_running:
                self.lbl_current_file.setText("Waiting for file to convert")
            else:
                if self.watchfolder_path == self.folder_message:
                    self.lbl_current_file.setText("No path set")
                else:
                    self.lbl_current_file.setText("Press start to convert")
        else:
            self.lbl_current_file.setText(filename)

    def progressbarWaiting(self):
        self.progress_bar.reset()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)

    def progressbarSetPercentage(self, percentage):
        self.progress_bar.reset()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(percentage)

    def progressbarStop(self):
        self.progress_bar.reset()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setTextVisible = False

    def clickSetFolder(self):
        start_path = self.lne_watchfolder_path.text()
        folder_selector = QtWidgets.QFileDialog(self)
        if self.validatePath(start_path):
            folder_selector.setDirectory(start_path)
        folder_selector.setFileMode(QtWidgets.QFileDialog.Directory)
        selected_folder = folder_selector.getExistingDirectory(self,"select folder")
        if selected_folder:
            self.watchfolder_path = selected_folder
            self.setFolderLabel(self.watchfolder_path)
            self.updateStatusLabel()
            self.editPath()

    def setFolderLabel(self, label):
        self.lne_watchfolder_path.setText(label)

    def clickStartStop(self):
        if not self.thread_running:
                self.btn_start_stop.setText("Stop")
                self.thread_running = True
                self.startWatcher()
                self.progressbarWaiting()
                self.updateStatusLabel()
                self.disableInput()
        else:
            self.btn_start_stop.setText("Start")
            self.thread_running = False
            self.progressbarStop()
            self.updateStatusLabel()
            self.enableInput()

    def disableInput(self):
        self.rbn_prores.setDisabled(True)
        self.rbn_h264.setDisabled(True)
        self.lne_watchfolder_path.setDisabled(True)
        self.btn_set_folder.setDisabled(True)

    def enableInput(self):
        self.rbn_prores.setEnabled(True)
        self.rbn_h264.setEnabled(True)
        self.lne_watchfolder_path.setEnabled(True)
        self.btn_set_folder.setEnabled(True)

    def validatePath(self, input_path):
        if os.path.isdir(input_path):
            print("{} is a valid path".format(input_path))
            return True
        else:

            return False

    def editPath(self):
        if self.validatePath(self.lne_watchfolder_path.text()):
            print("Enable Button")
            self.btn_start_stop.setEnabled(True)
            self.lne_watchfolder_path.setStyleSheet("color:black;")
        else:
            self.setFolderLabel(self.folder_message)
            self.btn_start_stop.setEnabled(False)
            self.lne_watchfolder_path.setStyleSheet("color:red;")


    def startWatcher(self):
        self.watcher_thread = WatcherThread(self)
        self.signals = WatcherConnections()
        self.watcher_thread.start()
        self.signals.progress_signal.connect(self.progressbarSetPercentage)
        self.signals.filename_signal.connect(self.updateStatusLabel)
        self.signals.waiting_signal.connect(self.progressbarWaiting)
        self.signals.count_signal.connect(self.addToCounter)
        self.signals.processed_signal.connect(self.addToProccesed)


class WatcherConnections(QtCore.QObject):
    progress_signal = QtCore.Signal(object)
    filename_signal = QtCore.Signal(object)
    waiting_signal = QtCore.Signal(object)
    count_signal = QtCore.Signal(object)
    processed_signal = QtCore.Signal(object)


class WatcherThread(QtCore.QThread):
    def __init__(self, gui):
        super(WatcherThread, self).__init__()
        self.gui = gui
        print("WatcherThread created")

    def run(self,):
        FolderWatcher(self.gui).run()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)


    if len(sys.argv) > 1:
        src_path = sys.argv[1]
        if os.path.isdir(src_path):
            print("Watchfolder is set to: {}".format(src_path))
            gui = ConverterGui()
            gui.watchfolder_path = src_path
            gui.setFolderLabel()
            gui.show()

            sys.exit(app.exec_())
    else:
        gui = ConverterGui()
        gui.show()
        sys.exit(app.exec_())
