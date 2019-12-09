import os, time
from watchdog.events import RegexMatchingEventHandler
from convert_to_prores_proxy import ProxyConverter


class ImagesEventHandler(RegexMatchingEventHandler):
    # exclude files with "proxy" in their name from the inputs
    IMAGES_REGEX = ["^((?!proxy).)*(mp4|mov|mxf)$"]

    def __init__(self, gui):
        super(ImagesEventHandler,self).__init__(self.IMAGES_REGEX)
        self.watchfolder = gui.watchfolder_path
        self.signals = gui.signals
        self.codec = gui.format

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
            time.sleep(1)
        file_done = False
        while not file_done:
            try:
                os.rename(event.src_path, event.src_path)
                file_done = True
            except:
                pass
        self.process(event)

    def process(self, event):
        converter = ProxyConverter()
        filename, extension = os.path.splitext(event.src_path)
        self.output_filename = "{0}_proxy.mov".format(os.path.basename(filename))

        proxy_path = converter.make_folder(event.src_path, self.watchfolder)
        print("proxy path = ", proxy_path)

        output_path = os.path.join(proxy_path, self.output_filename)
        print("output path = ", output_path)

        converter.process(event.src_path, output_path, self.signals, self.codec)
