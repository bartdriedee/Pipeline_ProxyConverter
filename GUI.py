import PySide2.QtWidgets as QtWidgets
import PySide2.QtCore as QtCore
from watch_folder import FolderWatcher
import sys,os


class ConverterGui(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(ConverterGui, self).__init__(parent)
        self.setMinimumSize(600,100)
        self.setWindowTitle("Proxy Converter")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.files_converted = 0
        self.thread_running = False
        self.watchfolder_path = "no folder specified"
        self.processed_files = ""

        self.createWidgets()
        self.createLayout()
        self.createConnections()

        self.updateStatusLabel()


    def createWidgets(self):
        print("create widgets")
        self.empty_line = QtWidgets.QLabel()

        self.lbl_watchfolder = QtWidgets.QLabel("Watching folder:")
        self.lbl_watchfolder_path = QtWidgets.QLabel(self.watchfolder_path)
        self.lbl_watchfolder_path.setAlignment(QtCore.Qt.AlignRight)

        self.lbl_files_converted = QtWidgets.QLabel("Files converted:")
        self.lbl_files_converted.setAlignment(QtCore.Qt.AlignRight)
        self.lbl_counter = QtWidgets.QLabel(str(self.files_converted))
        self.lbl_counter.setAlignment(QtCore.Qt.AlignRight)

        self.lbl_status = QtWidgets.QLabel("Converting file:")
        self.lbl_current_file = QtWidgets.QLabel()
        self.lbl_current_file.setAlignment(QtCore.Qt.AlignRight)
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setAlignment(QtCore.Qt.AlignHCenter)
        self.txt_processed = QtWidgets.QTextEdit()

        self.set_folder = QtWidgets.QPushButton("Set Folder")
        self.btn_start_stop = QtWidgets.QPushButton("Start")

    def createLayout(self):
        print("create layout")
        self.folder_layout = QtWidgets.QFormLayout()
        self.folder_layout.addRow(self.lbl_watchfolder,self.lbl_watchfolder_path)
        self.folder_layout.addRow(self.lbl_files_converted, self.lbl_counter)

        self.status_layout = QtWidgets.QHBoxLayout()
        self.status_layout.addWidget(self.lbl_status)
        self.status_layout.addWidget(self.lbl_current_file)

        self.ln_layout = QtWidgets.QVBoxLayout()
        self.ln_layout.addLayout(self.folder_layout)
        self.ln_layout.addWidget(self.empty_line)
        self.ln_layout.addLayout(self.status_layout)
        self.ln_layout.addWidget(self.progress_bar)
        self.ln_layout.addWidget(self.txt_processed)

        self.btn_layout = QtWidgets.QHBoxLayout()
        self.btn_layout.addWidget(self.set_folder)
        self.btn_layout.addWidget(self.btn_start_stop)

        self.main_layout = QtWidgets.QVBoxLayout(self)

        self.main_layout.addLayout(self.ln_layout)
        self.main_layout.addLayout(self.btn_layout)

    def createConnections(self):
        print("create connetions")
        self.set_folder.clicked.connect(self.clickSetFolder)
        self.btn_start_stop.clicked.connect(self.clickStartStop)


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
        folder_selector = QtWidgets.QFileDialog(self)
        folder_selector.setFileMode(QtWidgets.QFileDialog.Directory)

        self.watchfolder_path = folder_selector.getExistingDirectory(self,"select folder")  # r"C:\Users\Surface\Desktop\TEST_FOLDER\RUSHES"
        self.setFolderLabel()

    def setFolderLabel(self):
        self.lbl_watchfolder_path.setText(self.watchfolder_path)

    def clickStartStop(self):
        if not self.thread_running:
            if self.watchfolder_path != "no folder specified":
                self.btn_start_stop.setText("Stop")
                self.thread_running = True
                self.startWatcher()
                self.progressbarWaiting()
                self.updateStatusLabel()

        else:
            self.btn_start_stop.setText("Start")
            self.thread_running = False
            self.progressbarStop()
            self.updateStatusLabel()



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
