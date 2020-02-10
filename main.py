import PySide2.QtWidgets as QtWidgets
import GUI
import sys, os

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    if len(sys.argv) > 1:
        src_path = sys.argv[1]
        if os.path.isdir(src_path):
            print("Watchfolder is set to: {}".format(src_path))
            gui = GUI.ConverterGui()
            gui.watchfolder_path = src_path
            gui.show()

            sys.exit(app.exec_())
    else:
        gui = GUI.ConverterGui()
        gui.show()
        sys.exit(app.exec_())
