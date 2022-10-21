import os
import sys
from PySide6 import QtWidgets

from app.gui.GUI import MainGUI
from app.utils.Constants import Constants
from app.utils.PathManager import PathManager

if __name__ == '__main__':
    PathManager.set_root_path(os.path.dirname(os.path.realpath(__file__)))

    app = QtWidgets.QApplication([])
    app.setApplicationDisplayName(f'{Constants.WINDOW_NAME} v{Constants.VERSION}')
    app.setApplicationName(Constants.WINDOW_NAME)

    widget = MainGUI()
    widget.setFixedSize(800, 600)
    widget.show()

    sys.exit(app.exec())
