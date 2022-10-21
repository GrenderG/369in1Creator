from pathlib import Path

from app.utils.Constants import Constants
from app.utils.PathManager import PathManager


class Generator:
    SELECTED_ROMS = set()

    @staticmethod
    def generate(title: str, selector_char: str, pagination: bool, path: str, roms: dict):
        if not title.strip():
            title = Constants.DEFAULT_TITLE
        if not selector_char.strip():
            selector_char = Constants.DEFAULT_SELECTOR_CHAR

        menu_name = 'BLOCK0.GBA' if pagination else 'BLOCK0_NOPAGE.GBA'
        menu_path = Path(PathManager.get_root_path() + '/etc/base', menu_name)
        with open(menu_path, 'rb') as menu_file:
            menu_bytes = bytearray(menu_file.read())
            title_bytes = bytearray(title.encode()) + bytearray(Constants.MAX_NAME_SIZE - len(title))
            selector_char_bytes = bytearray(selector_char.encode())
            title_offset = Constants.NAME_ADDRESS if pagination else Constants.NAME_ADDRESS_NO_PAGE
            selector_char_offset = Constants.SELECTOR_CHAR_ADDRESS if pagination else \
                Constants.SELECTOR_CHAR_ADDRESS_NO_PAGE

            menu_bytes[title_offset:title_offset + Constants.MAX_NAME_SIZE] = title_bytes
            menu_bytes[selector_char_offset:selector_char_offset + Constants.MAX_SELECTOR_CHAR_SIZE] = \
                selector_char_bytes

            rom_menu_titles = list(roms.keys())
            if len(rom_menu_titles) > 0:
                for i in range(0, Constants.MAX_ROMS + 1):
                    current_offset = Constants.MENU_LIST_ADDRESS + (32 * i)
                    menu_item_bytes = bytearray(b'\x00' * Constants.MAX_MENU_TITLE_SIZE)
                    if i < len(rom_menu_titles):
                        menu_item_title = rom_menu_titles[i]
                        if not menu_item_title.strip():
                            menu_item_title = f'{Constants.DEFAULT_MENU_ITEM} {i}'
                        menu_item_bytes[:len(menu_item_title)] = menu_item_title.encode()
                    else:
                        menu_item_bytes += bytearray(b'\x00' * (Constants.MENU_TITLE_CHUNK_SIZE -
                                                     Constants.MAX_MENU_TITLE_SIZE))
                    menu_bytes[current_offset:current_offset + len(menu_item_bytes)] = menu_item_bytes
        merged_bytes = menu_bytes

        for index, rom_path in enumerate(roms.values()):
            with open(rom_path, 'rb') as rom_file:
                rom_bytes = rom_file.read()
                rom_bytes = bytearray(rom_bytes) + (bytearray(b'\xFF') * (Constants.HALF_BLOCK_SIZE - len(rom_bytes)))
                merged_bytes[Constants.HALF_BLOCK_SIZE + (Constants.HALF_BLOCK_SIZE * index):] = rom_bytes

        with open(path, 'wb') as merged_rom:
            merged_rom.write(merged_bytes)

        print('Finished writing.')
