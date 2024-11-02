import curses
import os

class FileNavigator:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.current_dir = os.getcwd()
        self.files = ['..'] + os.listdir(self.current_dir)
        self.selected_index = 0
        self.offset = 0
        self.height, self.width = self.stdscr.getmaxyx()
        self.display_height = self.height - 3

    def refresh_file_list(self):
        self.files = ['..'] + os.listdir(self.current_dir)
        self.selected_index = 0
        self.offset = 0

    def display_files(self):
        self.stdscr.clear()
        for i in range(self.display_height):
            file_index = i + self.offset
            if file_index >= len(self.files):
                break
            file = self.files[file_index]
            display_name = file[:self.width - 4]
            if file_index == self.selected_index:
                self.stdscr.addstr(i, 0, f"> {display_name}", curses.A_REVERSE)
            else:
                self.stdscr.addstr(i, 0, f"  {display_name}")
        self.stdscr.refresh()

    def handle_key_press(self, key):
        if key == curses.KEY_UP:
            if self.selected_index > 0:
                self.selected_index -= 1
                if self.selected_index < self.offset:
                    self.offset -= 1
        elif key == curses.KEY_DOWN:
            if self.selected_index < len(self.files) - 1:
                self.selected_index += 1
                if self.selected_index >= self.offset + self.display_height:
                    self.offset += 1
        elif key == ord('\n'):
            selected_file = self.files[self.selected_index]
            if os.path.isdir(selected_file):
                self.current_dir = os.path.abspath(selected_file)
                os.chdir(self.current_dir)
                self.refresh_file_list()
            else:
                file_size = os.path.getsize(selected_file)
                self.stdscr.addstr(self.display_height + 1, 0, f"Selected file: {selected_file[:self.width - 15]}")
                self.stdscr.addstr(self.display_height + 2, 0, f"File size: {file_size} bytes")
                self.stdscr.refresh()
                self.stdscr.getch()
        elif key == ord('q'):
            return False
        return True

def list_files(stdscr):
    stdscr.clear()
    stdscr.keypad(True)
    navigator = FileNavigator(stdscr)

    while True:
        navigator.display_files()
        key = stdscr.getch()
        if not navigator.handle_key_press(key):
            break

curses.wrapper(list_files)
