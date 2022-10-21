import os
import sys

from PySide6 import QtWidgets, QtCore, QtGui

from app.generator.Generator import Generator
from app.utils.Constants import Constants
from app.utils.PathManager import PathManager


class FinishDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('Finished writing')

        self.buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self.accept)

        self.layout = QtWidgets.QVBoxLayout()
        message = QtWidgets.QLabel('Finished writing the merged ROM, the program will now close.')
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.setLayout(self.layout)

        self.setWindowFlags(
            QtCore.Qt.Dialog |
            QtCore.Qt.WindowTitleHint
        )

    # override
    def closeEvent(self, event) -> None:
        sys.exit(0)


class MainGUI(QtWidgets.QWidget):
    ROM_DICT = {}
    LAST_SELECTED_PATH = ''

    def __init__(self):
        super().__init__()

        # Main window settings.
        self.setWindowIcon(QtGui.QIcon(PathManager.get_root_path() + '/etc/icon/icon.png'))

        # Create the main layout that holds the rest.
        self.layout = QtWidgets.QGridLayout()
        self.layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.layout_left = QtWidgets.QVBoxLayout()
        self.layout_right = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(-1, 8, -1, 8)

        # Group boxes and other layouts.
        self._create_basic_info()
        self._create_rom_select()
        self.layout_left.addWidget(self.basic_info_box)
        self.layout_right.addWidget(self.rom_selection_box)

        self._create_bottom_layout()

        # Add secondary layouts to the main one.
        self.layout.addLayout(self.layout_left, 0, 0)
        self.layout.addLayout(self.layout_right, 0, 1)
        self.layout.addLayout(self.bottom_layout, 1, 0, 1, 0)

        self.setLayout(self.layout)

    def _create_basic_info(self):
        self.basic_info_box = QtWidgets.QGroupBox('Basic Information')
        self.basic_info_box.setMinimumWidth(256)
        group_layout = QtWidgets.QVBoxLayout()
        group_layout.setContentsMargins(-1, 5, -1, -1)

        title_layout = QtWidgets.QHBoxLayout()
        label_title = QtWidgets.QLabel('Title: ')
        self.edit_title = QtWidgets.QLineEdit()
        self.edit_title.setText(Constants.DEFAULT_TITLE)
        self.edit_title.setMaxLength(Constants.MAX_NAME_SIZE)
        title_layout.addWidget(label_title)
        title_layout.addWidget(self.edit_title)

        selector_char_layout = QtWidgets.QHBoxLayout()
        label_selector_char = QtWidgets.QLabel('Selector char: ')
        self.edit_selector_char = QtWidgets.QLineEdit()
        self.edit_selector_char.setText(Constants.DEFAULT_SELECTOR_CHAR)
        self.edit_selector_char.setMaxLength(Constants.MAX_SELECTOR_CHAR_SIZE)
        selector_char_layout.addWidget(label_selector_char)
        selector_char_layout.addWidget(self.edit_selector_char)

        no_page_layout = QtWidgets.QHBoxLayout()
        label_no_page = QtWidgets.QLabel('Page text: ')
        self.cb_no_page = QtWidgets.QCheckBox()
        self.cb_no_page.setChecked(True)
        no_page_layout.addWidget(label_no_page)
        no_page_layout.addWidget(self.cb_no_page)

        group_layout.addLayout(title_layout)
        group_layout.addLayout(selector_char_layout)
        group_layout.addLayout(no_page_layout)
        group_layout.addStretch()

        self.basic_info_box.setLayout(group_layout)

    def _create_rom_select(self):
        self.rom_selection_box = QtWidgets.QGroupBox(f'ROM selection (0/{Constants.MAX_ROMS})')
        self.rom_selection_box.setMinimumWidth(256)
        self.rom_selection_group_layout = QtWidgets.QVBoxLayout()
        self.rom_selection_group_layout.setContentsMargins(-1, 5, -1, -1)

        self.add_rom_button = QtWidgets.QPushButton('Add ROM(s)')
        self.add_rom_button.clicked.connect(self.on_rom_select_click)

        self.rom_selection_group_layout.addWidget(self.add_rom_button)

        self.rom_selection_box.setLayout(self.rom_selection_group_layout)

    def _create_bottom_layout(self):
        self.bottom_layout = QtWidgets.QHBoxLayout()
        generate_button = QtWidgets.QPushButton('Generate')
        generate_button.clicked.connect(self.on_generate_click)
        self.bottom_layout.addWidget(generate_button)
        # self.bottom_layout.addStretch()

    def _generate_rom_layout(self, path):
        rom_layout = QtWidgets.QHBoxLayout()
        label_rom = QtWidgets.QLabel(path.split('/')[-1])
        edit_rom = QtWidgets.QLineEdit()
        edit_rom.setMaxLength(Constants.MAX_MENU_TITLE_SIZE)
        rom_layout.addWidget(label_rom)
        rom_layout.addWidget(edit_rom)

        return rom_layout, edit_rom

    # Actions.

    @QtCore.Slot()
    def on_generate_click(self):
        path = QtWidgets.QFileDialog.getSaveFileName(self, 'Create merged ROM', 'merged.gba', '.gba files (*.gba)')[0]
        if not path:
            return

        # Generate new dict containing only rom menu name and rom path.
        generator_rom_dict = {}
        for rom_path, edit_rom in MainGUI.ROM_DICT.items():
            generator_rom_dict[edit_rom.text()] = rom_path

        Generator.generate(
            title=self.edit_title.text(),
            selector_char=self.edit_selector_char.text(),
            pagination=self.cb_no_page.isChecked(),
            path=path,
            roms=generator_rom_dict
        )

        finish_dialog = FinishDialog()
        if finish_dialog.exec_():
            sys.exit(0)

    def _add_rom(self, path):
        if not path.strip():
            return None

        if path not in MainGUI.ROM_DICT:
            layout, edit_rom = self._generate_rom_layout(path)
            MainGUI.ROM_DICT[path] = edit_rom
            return layout
        return None

    @QtCore.Slot()
    def on_rom_select_click(self):
        files = QtWidgets.QFileDialog.getOpenFileNames(self, 'Select ROM(s)', MainGUI.LAST_SELECTED_PATH,
                                                       '.gba files (*.gba)')[0]
        if len(files) > 0:
            MainGUI.LAST_SELECTED_PATH = os.path.dirname(files[0])

        for file in files:
            layout = self._add_rom(file)
            # A layout will only be given if it was possible to add this rom.
            if layout:
                selected_roms_length = len(MainGUI.ROM_DICT)
                self.rom_selection_group_layout.addLayout(layout)
                self.rom_selection_box.setTitle(f'ROM selection ({selected_roms_length}/{Constants.MAX_ROMS})')
                if selected_roms_length == Constants.MAX_ROMS:
                    self.add_rom_button.setEnabled(False)
