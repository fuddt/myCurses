import curses
import os
import subprocess
from abc import ABC, abstractmethod
from utils.scroller import Scroller

class Command(ABC):
    @abstractmethod
    def execute(self) -> None:
        pass

class ViewCommand(Command):
    def __init__(self, filename: str) -> None:
        self.filename = filename

    def execute(self) -> None:
        curses.endwin()
        subprocess.run(['less', self.filename])
        curses.doupdate()

class EditCommand(Command):
    def __init__(self, filename: str) -> None:
        self.filename = filename

    def execute(self) -> None:
        curses.endwin()
        subprocess.run(['vim', self.filename])
        curses.doupdate()

class RemoveCommand(Command):
    def __init__(self, filename: str) -> None:
        self.filename = filename

    def execute(self) -> None:
        os.remove(self.filename)

class NewFileCommand(Command):
    def execute(self) -> None:
        curses.endwin()
        filename = input("Enter the new filename: ")
        if filename:
            subprocess.run(['vim', filename])
        curses.doupdate()

class State(ABC):
    @abstractmethod
    def handle_input(self, navigator: "FileNavigator", key: int) -> None:
        pass

    @abstractmethod
    def display(self, navigator: "FileNavigator") -> None:
        pass

class FileListState(State):
    def handle_input(self, navigator: "FileNavigator", key: int) -> None:
        if key == curses.KEY_UP:
            navigator.scroller.scroll_up()
        elif key == curses.KEY_DOWN:
            navigator.scroller.scroll_down(len(navigator.files))
        elif key == ord('\n'):
            selected_file = navigator.files[navigator.scroller.selected_index]
            if os.path.isdir(selected_file):
                navigator.current_dir = os.path.abspath(selected_file)
                os.chdir(navigator.current_dir)
                navigator.refresh_file_list()
            else:
                navigator.set_state(MenuState(selected_file))
        elif key == ord('n'):
            navigator.set_state(NewFileState())
        elif key == ord('q'):
            navigator.exit()

    def display(self, navigator: "FileNavigator") -> None:
        navigator.display_files()

class MenuState(State):
    def __init__(self, filename: str) -> None:
        self.filename = filename

    def handle_input(self, navigator: "FileNavigator", key: int) -> None:
        commands = [ViewCommand(self.filename), EditCommand(self.filename), RemoveCommand(self.filename)]
        if key == curses.KEY_UP:
            navigator.selected_option = (navigator.selected_option - 1) % len(commands)
        elif key == curses.KEY_DOWN:
            navigator.selected_option = (navigator.selected_option + 1) % len(commands)
        elif key == ord('\n'):
            commands[navigator.selected_option].execute()
            navigator.refresh_file_list()
            navigator.set_state(FileListState())
        elif key == ord('b'):
            navigator.set_state(FileListState())

    def display(self, navigator: "FileNavigator") -> None:
        navigator.display_menu()

class NewFileState(State):
    def handle_input(self, navigator: "FileNavigator", key: int) -> None:
        command = NewFileCommand()
        command.execute()
        navigator.refresh_file_list()
        navigator.set_state(FileListState())

    def display(self, navigator: "FileNavigator") -> None:
        pass

class FileNavigator:
    def __init__(self, stdscr: curses.window) -> None:
        self.stdscr = stdscr
        self.current_dir = os.getcwd()
        self.files = ['..'] + os.listdir(self.current_dir)
        self.selected_option = 0
        self.scroller = Scroller(0, 0, self.stdscr.getmaxyx()[0] - 3)
        self.state = FileListState()
        self.exit_flag = False

    def set_state(self, state: State) -> None:
        self.state = state

    def refresh_file_list(self) -> None:
        self.files = ['..'] + os.listdir(self.current_dir)

    def display_files(self) -> None:
        pass

    def display_menu(self) -> None:
        pass

    def run(self) -> None:
        while not self.exit_flag:
            self.state.display(self)
            key = self.stdscr.getch()
            self.state.handle_input(self, key)

    def exit(self) -> None:
        self.exit_flag = True

def list_files(stdscr: curses.window) -> None:
    stdscr.clear()
    stdscr.keypad(True)
    navigator = FileNavigator(stdscr)

    while not navigator.exit_flag:
        navigator.run()

curses.wrapper(list_files)
