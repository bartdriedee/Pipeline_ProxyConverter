import PySide2.QtWidgets as QtWidgets
import PySide2.QtCore as QtCore
from watch_folder import FolderWatcher
import sys,os


class ConverterGui(QtWidgets.QDialog):
    def __init__(self, watcher_thread, parent=None):
        super(ConverterGui, self).__init__(parent)
        self.setMinimumSize(600,100)
        self.setWindowTitle("Proxy Converter")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.files_converted = 0
        self.watchfolder_path = "no folder specified"
        self.watcher_thread = watcher_thread
        self.processed_files = ""

        self.createWidgets()
        self.createLayout()
        self.createConnections()

        self.updateStatusLabel()
        self.progressbarWaiting()

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
        self.btn_Cancel = QtWidgets.QPushButton("Stop_watching")

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
        self.btn_layout.addWidget(self.btn_Cancel)

        self.main_layout = QtWidgets.QVBoxLayout(self)

        self.main_layout.addLayout(self.ln_layout)
        self.main_layout.addLayout(self.btn_layout)

    def createConnections(self):
        print("create connetions")
        self.set_folder.clicked.connect(self.clickOk)
        self.btn_Cancel.clicked.connect(self.clickCancel)
        watcher_thread.signals.progress_signal.connect(self.progressbarSetPercentage)
        watcher_thread.signals.filename_signal.connect(self.updateStatusLabel)
        watcher_thread.signals.waiting_signal.connect(self.progressbarWaiting)
        watcher_thread.signals.count_signal.connect(self.addToCounter)
        watcher_thread.signals.processed_signal.connect(self.addToProccesed)


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

    def updateStatusLabel(self,filename=None):
        if filename is None:
            self.lbl_current_file.setText("Waiting for file to convert")
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

    def setFolder(self, folder=""):
        self.watchfolder_path = folder
        self.lbl_watchfolder_path.setText(self.watchfolder_path)

    def clickOk(self):
        self.updateStatusLabel("file.mov")
        self.progressbarSetPercentage(50)

    def clickCancel(self):
        self.updateStatusLabel()
        self.progressbarWaiting()


class WatcherConnections(QtCore.QObject):
    progress_signal = QtCore.Signal(object)
    filename_signal = QtCore.Signal(object)
    waiting_signal = QtCore.Signal(object)
    count_signal = QtCore.Signal(object)
    processed_signal = QtCore.Signal(object)


class WatcherThread(QtCore.QThread):
    def __init__(self, path):
        super(WatcherThread, self).__init__()
        self.src_path = path
        self.signals = WatcherConnections()
        print("WatcherThread created")

    def run(self):
        print ("RUN")
        FolderWatcher(self.src_path, self.signals).run()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    if len(sys.argv) > 1:
        src_path = sys.argv[1]
        if os.path.isdir(src_path):
            print("Watchfolder is set to: {}".format(src_path))
            watcher_thread = WatcherThread(src_path)
            watcher_thread.start()  # Calls WatcherThread.run()
            gui = ConverterGui()
            gui.show()
            sys.exit(app.exec_())
    else:
        print("Please specify a folder to watch")
        src_path = r"C:\Users\Surface\Desktop\TEST_FOLDER\RUSHES"
        watcher_thread = WatcherThread(src_path)
        gui = ConverterGui(watcher_thread)

        gui.show()
        gui.setFolder(src_path)

        watcher_thread.start()
        sys.exit(app.exec_())
