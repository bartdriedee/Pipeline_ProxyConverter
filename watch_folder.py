import sys, os, time
from watchdog.observers import Observer
from events import ImagesEventHandler


class FolderWatcher:
    def __init__(self, watchfolder):
        self.__src_path = watchfolder
        self.__event_handler = ImagesEventHandler(watchfolder)
        self.__event_observer = Observer()
        print("Watching folder: {}".format(watchfolder))

    def run(self):
        self.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def start(self):
        self.__schedule()
        self.__event_observer.start()

    def stop(self):
        self.__event_observer.stop()
        self.__event_observer.join()

    def __schedule(self):
        self.__event_observer.schedule(
            self.__event_handler,
            self.__src_path,
            recursive=True
        )


if __name__ == "__main__":
    if len(sys.argv) > 1:
        src_path = sys.argv[1]
        if os.path.isdir(src_path):
            print("Watching folder: {}".format(src_path))
            FolderWatcher(src_path).run()
    else:
        print("Please specify a folder to watch")
        FolderWatcher(r"C:\Users\Surface\Desktop\TEST_FOLDER\RUSHES").run()
