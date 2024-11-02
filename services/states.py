from __future__ import annotations  # Python 3.7以上でクラス名の型ヒントを許容
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fileopen import FileNavigator

import curses
import os
import subprocess
from abc import ABC, abstractmethod


# コマンドの基底クラス
class Command(ABC):
    @abstractmethod
    def execute(self) -> None:
        pass


class ViewCommand(Command):
    def __init__(self, filename: str) -> None:
        self.filename = filename

    def execute(self) -> None:
        curses.endwin()
        subprocess.run(["less", self.filename])
        curses.doupdate()


class EditCommand(Command):
    def __init__(self, filename: str) -> None:
        self.filename = filename

    def execute(self) -> None:
        curses.endwin()
        subprocess.run(["vim", self.filename])
        curses.doupdate()


class RemoveCommand(Command):
    def __init__(self, filename: str, stdscr: curses.window) -> None:
        self.filename = filename
        self.stdscr = stdscr

    def execute(self) -> None:
        self.stdscr.clear()
        self.stdscr.addstr(0, 0, f"Are you sure you want to remove {self.filename}? (y/n)")
        self.stdscr.refresh()

        key = self.stdscr.getch()
        if key == ord("y"):
            os.remove(self.filename)
            self.stdscr.addstr(1, 0, "File removed.")
        else:
            self.stdscr.addstr(1, 0, "Operation cancelled.")
        self.stdscr.refresh()
        self.stdscr.getch()  # ユーザーが何かキーを押すまで待機


class NewFileCommand(Command):
    def execute(self) -> None:
        curses.endwin()
        filename = input("Enter the new filename: ")
        if filename:
            subprocess.run(["vim", filename])
        curses.doupdate()


# 状態管理の基底クラス
class State(ABC):
    @abstractmethod
    def handle_input(self, navigator: FileNavigator, key: int) -> None:
        pass

    @abstractmethod
    def display(self, navigator: FileNavigator) -> None:
        pass


# ファイルリストの表示状態
class FileListState(State):
    def handle_input(self, navigator: FileNavigator, key: int) -> None:
        if key == curses.KEY_UP:
            navigator.scroller.scroll_up()
        elif key == curses.KEY_DOWN:
            navigator.scroller.scroll_down(len(navigator.files))
        elif key == ord("\n"):
            selected_file = navigator.files[navigator.scroller.selected_index]
            if os.path.isdir(selected_file):
                navigator.current_dir = os.path.abspath(selected_file)
                os.chdir(navigator.current_dir)
                navigator.refresh_file_list()
            else:
                navigator.set_state(MenuState(selected_file))
        elif key == ord("n"):
            navigator.set_state(NewFileState())
        elif key == ord("q"):
            navigator.exit()

    def display(self, navigator: FileNavigator) -> None:
        navigator.display_files()


# メニュー表示状態
class MenuState(State):
    def __init__(self, filename: str) -> None:
        self.filename = filename

    def handle_input(self, navigator: FileNavigator, key: int) -> None:
        commands = [
            ViewCommand(self.filename),
            EditCommand(self.filename),
            RemoveCommand(self.filename, navigator.stdscr),
            None,  # 'back' のためのダミーエントリー
        ]
        match key:
            case curses.KEY_UP:
                navigator.selected_option = (navigator.selected_option - 1) % len(commands)
            case curses.KEY_DOWN:
                navigator.selected_option = (navigator.selected_option + 1) % len(commands)
            case 10:  # Enterキー（ord('\n') の結果が 10）
                if commands[navigator.selected_option] is None:  # 'back' が選択された場合
                    navigator.set_state(FileListState())
                else:
                    commands[navigator.selected_option].execute()
                    navigator.refresh_file_list()
                    navigator.set_state(FileListState())
            case 98:  # 'b'キーのASCIIコードは98
                navigator.set_state(FileListState())

    def display(self, navigator: FileNavigator) -> None:
        navigator.display_menu()


# 新規ファイル作成状態
class NewFileState(State):
    def handle_input(self, navigator: FileNavigator, key: int) -> None:
        command = NewFileCommand()
        command.execute()
        navigator.refresh_file_list()
        navigator.set_state(FileListState())

    def display(self, navigator: FileNavigator) -> None:
        pass


# 初期状態を返すファクトリ関数
def get_initial_state() -> State:
    return FileListState()
