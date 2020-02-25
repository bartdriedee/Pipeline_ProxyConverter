import PySide2.QtWidgets as QtWidgets
import PySide2.QtCore as QtCore
import PySide2.QtGui as QtGui
from watch_folder import FolderWatcher
import sys, os

class ConverterGui(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(ConverterGui, self).__init__(parent)
        self.setMinimumSize(600,100)
        self.setWindowTitle("ConvertTo v1.00")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.files_converted = 0
        self.thread_running = False
        self.folder_message = "Enter a valid folder path"
        self.folder_icon = "data/icons8-folder-40.png"
        self.watchfolder_path = self.folder_message
        self.processed_files = ""
        self.existing_files = []
        self.watch = False

        self.createWidgets()
        self.createLayout()
        self.createConnections()
        self.updateStatusLabel()
        self.proresToggled()
        self.fileFolderToggled()
        self.editPath()

    #Update path for OSX app
    def resource_path(self, relative):
        if hasattr(sys, "_MEIPASS"):
            print(os.path.join(sys._MEIPASS, relative))
            return os.path.join(sys._MEIPASS, relative)
        return os.path.join(relative)

    def createWidgets(self):
        print("create widgets")
        self.lbl_watchfolder = QtWidgets.QLabel("Watching folder:")
        self.lne_watchfolder_path = QtWidgets.QLineEdit(self.folder_message)

        self.btn_set_folder = QtWidgets.QPushButton()
        self.btn_set_folder.setIcon(QtGui.QIcon(self.resource_path(self.folder_icon)))
        self.btn_set_folder.setFlat(True)

        self.lbl_watch = QtWidgets.QLabel("Watchfolder")
        self.cb_watch = QtWidgets.QCheckBox()

        self.lbl_format = QtWidgets.QLabel("File format:")
        self.rbn_h264 = QtWidgets.QRadioButton("H264")
        self.rbn_prores = QtWidgets.QRadioButton("Prores proxy")

        self.rbn_format_group = QtWidgets.QButtonGroup()
        self.rbn_format_group.addButton(self.rbn_h264)
        self.rbn_format_group.addButton(self.rbn_prores)
        self.rbn_prores.setChecked(True)

        self.lbl_sorting = QtWidgets.QLabel("Proxy sorting:")
        self.rbn_no_folder = QtWidgets.QRadioButton("No folders")
        self.rbn_card_folder = QtWidgets.QRadioButton("Folder per card")
        self.rbn_file_folder = QtWidgets.QRadioButton("Folder next to source")

        self.rbn_sorting_group = QtWidgets.QButtonGroup()
        self.rbn_sorting_group.addButton(self.rbn_no_folder)
        self.rbn_sorting_group.addButton(self.rbn_card_folder)
        self.rbn_sorting_group.addButton(self.rbn_file_folder)
        self.rbn_file_folder.setChecked(True)

        self.lbl_files_converted = QtWidgets.QLabel("Files converted:")

        self.lbl_counter = QtWidgets.QLabel(str(self.files_converted))
        self.lbl_counter.setAlignment(QtCore.Qt.AlignRight)

        self.lbl_status = QtWidgets.QLabel("Converting file:")
        self.lbl_current_file = QtWidgets.QLabel()
        self.lbl_current_file.setAlignment(QtCore.Qt.AlignRight)
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setAlignment(QtCore.Qt.AlignHCenter)

        self.txt_processed = QtWidgets.QTextEdit()

        self.btn_start_stop_watching = QtWidgets.QPushButton("Start")
        self.btn_start_stop_watching.setEnabled(False)

    def createLayout(self):
        print("creating layout")
        # Path input field
        self.folder_path_layout = QtWidgets.QHBoxLayout()
        self.folder_path_layout.addWidget(self.lne_watchfolder_path)
        self.folder_path_layout.addWidget(self.btn_set_folder)

        # Checkbox to toggle between folder watching or only present items
        self.watch_cb_layout = QtWidgets.QFormLayout()
        self.watch_cb_layout.addRow(self.lbl_watch, self.cb_watch)

        # Radio buttons for output format
        self.format_rbn_layout = QtWidgets.QVBoxLayout()
        self.format_rbn_layout.setAlignment(QtCore.Qt.AlignTop)
        self.format_rbn_layout.addWidget(self.lbl_format)
        self.format_rbn_layout.addWidget(self.rbn_h264)
        self.format_rbn_layout.addWidget(self.rbn_prores)

        # Radio buttons to set the proxy-file location
        self.sorting_rbn_layout = QtWidgets.QVBoxLayout()
        self.sorting_rbn_layout.addWidget(self.lbl_sorting)
        self.sorting_rbn_layout.addWidget(self.rbn_no_folder)
        self.sorting_rbn_layout.addWidget(self.rbn_card_folder)
        self.sorting_rbn_layout.addWidget(self.rbn_file_folder)

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
        self.btn_layout.addWidget(self.btn_start_stop_watching)

        self.option_layout = QtWidgets.QHBoxLayout()
        self.option_layout.addLayout(self.format_rbn_layout)
        self.option_layout.addLayout(self.sorting_rbn_layout)

        # top level layout gets self as parameter
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.addLayout(self.folder_layout)
        self.main_layout.addLayout(self.watch_cb_layout)
        self.main_layout.addWidget(QtWidgets.QLabel())  # Adds an empty line
        self.main_layout.addLayout(self.option_layout)
        self.main_layout.addWidget(QtWidgets.QLabel())  # Adds an empty line
        self.main_layout.addLayout(self.counter_layout)
        self.main_layout.addLayout(self.status_layout)
        self.main_layout.addWidget(self.progress_bar)
        self.main_layout.addWidget(self.txt_processed)
        self.main_layout.addLayout(self.btn_layout)

    def createConnections(self):
        print("create connetions")
        self.btn_set_folder.clicked.connect(self.clickSetFolder)
        self.btn_start_stop_watching.clicked.connect(self.clickStartStopWatcher)
        self.cb_watch.stateChanged.connect(self.updateWatch)
        self.rbn_prores.toggled.connect(self.proresToggled)
        self.rbn_h264.toggled.connect(self.h264Toggled)
        self.rbn_no_folder.toggled.connect(self.noFolderToggled)
        self.rbn_card_folder.toggled.connect(self.cardFolderToggled)
        self.rbn_file_folder.toggled.connect(self.fileFolderToggled)
        self.lne_watchfolder_path.editingFinished.connect(self.editPath)

    def proresToggled(self):
        if self.rbn_prores.isChecked():
            self.format = "prores"
            print(f"format is set to: {self.format}")

    def h264Toggled(self):
        if self.rbn_h264.isChecked():
            self.format = "h264"
            print(f"format is set to: {self.format}")

    def noFolderToggled(self):
        if self.rbn_no_folder.isChecked():
            self.sorted_per_card = None
            print("Folder sorting is None")

    def cardFolderToggled(self):
        if self.rbn_card_folder.isChecked():
            self.sorted_per_card = True
            print("Folder sorting is per card")

    def fileFolderToggled(self):
        if (self.rbn_file_folder.isChecked()):
            self.sorted_per_card = False
            print("Folder sorting is at file location")

    def addToCounter(self):
        self.files_converted +=1
        self.lbl_counter.setText(str(self.files_converted))

    def addToProccesed(self, input_string):
        txt = []
        txt.append(self.processed_files)
        txt.append("\n")
        txt.append(input_string)
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
            for root, dirs, files in os.walk(selected_folder):
                for x,file in enumerate(files):
                    self.existing_files.append((os.path.join(root, files[x])))

    def setFolderLabel(self, label):
        self.lne_watchfolder_path.setText(label)

    def updateWatch(self):
        self.watch = self.cb_watch.isChecked()
        print(f"watch = {self.cb_watch.isChecked()}")

    def clickStartStopWatcher(self):
        if not self.thread_running:
                self.btn_start_stop_watching.setText("Stop")
                self.thread_running = True
                self.startWatcher()
                self.progressbarWaiting()
                self.updateStatusLabel()
                self.disableInput()
        else:
            self.btn_start_stop_watching.setText("Start")
            self.thread_running = False
            self.progressbarStop()
            self.updateStatusLabel()
            self.enableInput()

    def disableInput(self):
        self.rbn_prores.setDisabled(True)
        self.rbn_h264.setDisabled(True)
        self.rbn_no_folder.setDisabled(True)
        self.rbn_file_folder.setDisabled(True)
        self.rbn_card_folder.setDisabled(True)
        self.lne_watchfolder_path.setDisabled(True)
        self.btn_set_folder.setDisabled(True)
        self.cb_watch.setDisabled(True)

    def enableInput(self):
        self.rbn_prores.setEnabled(True)
        self.rbn_h264.setEnabled(True)
        self.rbn_no_folder.setEnabled(True)
        self.rbn_file_folder.setEnabled(True)
        self.rbn_card_folder.setEnabled(True)
        self.lne_watchfolder_path.setEnabled(True)
        self.btn_set_folder.setEnabled(True)
        self.cb_watch.setEnabled(True)

    def validatePath(self, input_path):
        if os.path.isdir(input_path):
            return True
        else:
            return False

    # Update the Path line edit with the selected path or show message asking to change it.
    def editPath(self):
        if self.validatePath(self.lne_watchfolder_path.text()):
            self.btn_start_stop_watching.setEnabled(True)
            self.lne_watchfolder_path.setStyleSheet("color:black;")
        else:
            self.setFolderLabel(self.folder_message)
            self.btn_start_stop_watching.setEnabled(False)
            self.lne_watchfolder_path.setStyleSheet("color:red;")

    def connectSignals(self):
        self.signals = WatcherConnections()
        self.signals.progress_signal.connect(self.progressbarSetPercentage)
        self.signals.filename_signal.connect(self.updateStatusLabel)
        self.signals.waiting_signal.connect(self.progressbarWaiting)
        self.signals.count_signal.connect(self.addToCounter)
        self.signals.processed_signal.connect(self.addToProccesed)
        self.signals.queue_completed_signal.connect(self.stopWatcher)

    def startWatcher(self):
        self.watcher_thread = WatcherThread(self)
        self.watcher_thread.start()
        self.connectSignals()

    def stopWatcher(self):
        self.watcher_thread.stop()


class WatcherConnections(QtCore.QObject):
    progress_signal = QtCore.Signal(object)
    filename_signal = QtCore.Signal(object)
    waiting_signal = QtCore.Signal(object)
    count_signal = QtCore.Signal(object)
    processed_signal = QtCore.Signal(object)
    queue_completed_signal = QtCore.Signal(object)


class WatcherThread(QtCore.QThread):
    def __init__(self, gui):
        super(WatcherThread, self).__init__()
        self.gui = gui
        print("WatcherThread created")

    def run(self,):
        FolderWatcher(self.gui).run()

