import sys, os, time
from watchdog.observers import Observer
from events import ImagesEventHandler


class FolderWatcher:
    def __init__(self, gui):
        self.gui = gui
        print ("Folderwatcher", gui)
        print("Watching folder: {}".format(self.gui.watchfolder_path))
        self.__src_path = gui.watchfolder_path
        self.__event_handler = ImagesEventHandler(gui)
        self.__event_observer = Observer()

    def run(self):
        self.start()
        try:
            while True and self.gui.thread_running:
                time.sleep(1)
            self.stop()
        except KeyboardInterrupt:
            self.stop()


    def start(self):
        self.__schedule()
        self.__event_observer.start()

    def stop(self):
        print("Watcher stopped")
        self.__event_observer.stop()
        self.__event_observer.join()


    def __schedule(self):
        self.__event_observer.schedule(
            self.__event_handler,
            self.__src_path,
            recursive=True
        )
