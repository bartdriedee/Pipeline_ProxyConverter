import os, time
from watchdog.events import RegexMatchingEventHandler
from convert_to_prores_proxy import ProxyConverter


class ImagesEventHandler(RegexMatchingEventHandler):
    # exclude files with "proxy" in their name from the inputs
    IMAGES_REGEX = ["^((?!proxy).)*(mp4|mov|mxf)$"]

    def __init__(self, watchfolder):
        super(ImagesEventHandler,self).__init__(self.IMAGES_REGEX)
        self.watchfolder = watchfolder

    # Catch - all file system events
    def on_any_event(self, event):
        # print "any"
        pass

    # called when a file or directory is deleted
    def on_deleted(self, event):
        # print "delete"
        pass

    # called when a file or directory is changed
    def on_modified(self, event):
        # print "modified"
        pass

    # called when a file or a directory is moved or renamed
    def on_moved(self, event):
        # print "moved"
        pass

    # called when a file or a directory is created
    def on_created(self, event):
        file_size = -1
        while file_size != os.path.getsize(event.src_path):
            file_size = os.path.getsize(event.src_path)
            time.sleep(5)
        self.process(event)

    def process(self, event):
        ProxyConverter(event.src_path, self.watchfolder)
