import logging
import sys

from PyQt5.QtWidgets import QApplication

from PyMultibound.gui.mainwindow import MainWindow

if __name__ == '__main__':
    logging.info("Running GUI")
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
