import os, time
from watchdog.events import RegexMatchingEventHandler
from watchdog.events import FileSystemEvent
from convert_to_prores_proxy import ProxyConverter


class ManualEvent(FileSystemEvent):
    """User initiated event representing file presence on the file system."""
    event_type = 'created'

    def __init__(self, src_path):
        super(ManualEvent, self).__init__(src_path)
        self.is_synthetic = True

    def __repr__(self):
        return ("<%(class_name)s: src_path=%(src_path)r>"
                ) % (dict(class_name=self.__class__.__name__,
                          src_path=self.src_path))


class ImagesEventHandler(RegexMatchingEventHandler):
    # exclude files with "proxy" in their name from the inputs
    IMAGES_REGEX = ["^((?!proxy).)*(mp4|mov|mxf)$"]

    def __init__(self, gui):
        super(ImagesEventHandler,self).__init__(self.IMAGES_REGEX)
        self.existing_files = gui.existing_files
        self.watch = gui.watch
        self.watchfolder = gui.watchfolder_path
        self.signals = gui.signals
        self.codec = gui.format
        self.folder_sorting_per_card = gui.sorted_per_card
        self.existing_files_processed = 0
        for file in self.existing_files:
            self.queueExistingFiles(file)

    # Manually add file to event_queue
    def queueExistingFiles(self,path):
        self.dispatch(ManualEvent(path))

    # called when a file or a directory is created
    def on_created(self, event):
        # Synthetic events are always processed
        if event.is_synthetic:
            self.process(event)
            self.existing_files_processed += 1
        else:
            # File system event are only processed when watchfolder functionality is checked.
            if self.watch:
                if self.fileReady(event):
                    self.process(event)

    # Check is the file is done writing and there is no lock on the file
    def fileReady(self,event):
        file_path = event.src_path
        # See if the file size is still growing
        file_size = -1
        while file_size != os.path.getsize(file_path):
            file_size = os.path.getsize(file_path)
            time.sleep(1)
        # See if the file is being used by another process
        file_done = False
        while not file_done:
            try:
                os.rename(file_path, file_path)
                file_done = True
            except:
                return True

    # Process the file represented by the event
    def process(self, event):
        converter = ProxyConverter()
        filename, extension = os.path.splitext(event.src_path)
        output_filename = f"{os.path.basename(filename)}_proxy.mov"

        if self.folder_sorting_per_card is not None:
            # if True (per card) or false (at file location) make a proxy folder
            proxy_path = converter.make_folder(event.src_path, self.watchfolder, self.folder_sorting_per_card)
        else:
            # if None don't make a folder
            proxy_path = os.path.dirname(event.src_path)

        output_path = os.path.join(proxy_path, output_filename)

        converter.process(event.src_path, output_path, self.signals, self.codec)
        # if we're not using the watchfolder functionality, stop the process when all files are processed.
        if not self.watch:
            if self.existing_files_processed == len(self.existing_files):
                self.signals.queue_completed_signal.emit()
