from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fileopen import FileNavigator

import curses
import os
import subprocess
from abc import ABC, abstractmethod


# コマンドの基底クラス
class Command(ABC):
    """
    Commandクラスは、各コマンドの基底クラスであり、executeメソッドを実装する必要があります。
    """
    @abstractmethod
    def execute(self) -> None:
        """コマンドを実行します。"""
        pass


class ViewCommand(Command):
    """
    指定されたファイルをlessコマンドで表示するコマンド。

    Attributes:
        filename (str): 表示するファイルの名前。
    """
    def __init__(self, filename: str) -> None:
        self.filename = filename

    def execute(self) -> None:
        """lessコマンドを使ってファイルを表示します。"""
        curses.endwin()
        subprocess.run(["less", self.filename])
        curses.doupdate()


class EditCommand(Command):
    """
    指定されたファイルをvimエディタで編集するコマンド。

    Attributes:
        filename (str): 編集するファイルの名前。
    """
    def __init__(self, filename: str) -> None:
        self.filename = filename

    def execute(self) -> None:
        """vimを使ってファイルを編集します。"""
        curses.endwin()
        subprocess.run(["vim", self.filename])
        curses.doupdate()


class RemoveCommand(Command):
    """
    指定されたファイルを削除するコマンド。

    Attributes:
        filename (str): 削除するファイルの名前。
        stdscr (curses.window): cursesのウィンドウオブジェクト。
    """
    def __init__(self, filename: str, stdscr: curses.window) -> None:
        self.filename = filename
        self.stdscr = stdscr

    def execute(self) -> None:
        """
        ファイルを削除するかどうかの確認を表示し、ユーザーが'y'を押した場合はファイルを削除します。
        """
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
    """
    新しいファイルを作成するコマンド。
    """
    def execute(self) -> None:
        """
        ファイル名を入力して、新しいファイルをvimで作成します。
        """
        curses.endwin()
        filename = input("Enter the new filename: ")
        if filename:
            subprocess.run(["vim", filename])
        curses.doupdate()


# 状態管理の基底クラス
class State(ABC):
    """
    Stateクラスは、各状態の基底クラスであり、handle_inputとdisplayメソッドを実装する必要があります。
    """
    @abstractmethod
    def handle_input(self, navigator: FileNavigator, key: int) -> None:
        """
        キー入力を処理するメソッド。

        Args:
            navigator (FileNavigator): ファイルナビゲーターのインスタンス。
            key (int): ユーザーが押したキー。
        """
        pass

    @abstractmethod
    def display(self, navigator: FileNavigator) -> None:
        """
        状態に応じた表示を行うメソッド。

        Args:
            navigator (FileNavigator): ファイルナビゲーターのインスタンス。
        """
        pass


class FileListState(State):
    """
    ファイルリストの表示状態を管理するクラス。

    Attributes:
        State (ABC): 基底クラスのState。
    """
    def handle_input(self, navigator: FileNavigator, key: int) -> None:
        """
        ファイルリスト状態でのキー入力を処理します。

        Args:
            navigator (FileNavigator): ファイルナビゲーターのインスタンス。
            key (int): ユーザーが押したキー。
        """
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
        """
        ファイルリストを表示します。

        Args:
            navigator (FileNavigator): ファイルナビゲーターのインスタンス。
        """
        navigator.display_files()


class MenuState(State):
    """
    メニューの表示状態を管理するクラス。

    Attributes:
        filename (str): 操作対象のファイルの名前。
        options (dict): コマンド名をキー、コマンドオブジェクトを値とする辞書。
        option_keys (list): メニューオプションのキーリスト。
        selected_option (int): 現在選択されているメニューオプションのインデックス。
    """
    def __init__(self, filename: str) -> None:
        self.filename = filename
        # コマンドとメニュー項目をペアで保持
        self.options = {
            "view": ViewCommand(self.filename),
            "edit": EditCommand(self.filename),
            "remove": RemoveCommand(self.filename, curses.initscr()),
            "back": None  # 'back' は特別な処理として扱う
        }
        self.option_keys = list(self.options.keys())
        self.selected_option = 0

    def handle_input(self, navigator: FileNavigator, key: int) -> None:
        """
        メニュー状態でのキー入力を処理します。

        Args:
            navigator (FileNavigator): ファイルナビゲーターのインスタンス。
            key (int): ユーザーが押したキー。
        """
        match key:
            case curses.KEY_UP:
                self.selected_option = (self.selected_option - 1) % len(self.option_keys)
            case curses.KEY_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.option_keys)
            case 10:  # Enterキー（ord('\n') の結果が 10）
                selected_key = self.option_keys[self.selected_option]
                if self.options[selected_key] is None:  # 'back' が選択された場合
                    navigator.set_state(FileListState())
                else:
                    self.options[selected_key].execute()
                    navigator.refresh_file_list()
                    navigator.set_state(FileListState())
            case 98:  # 'b'キーのASCIIコードは98
                navigator.set_state(FileListState())

    def display(self, navigator: FileNavigator) -> None:
        """
        メニューオプションを表示します。

        Args:
            navigator (FileNavigator): ファイルナビゲーターのインスタンス。
        """
        navigator.display_menu(self.options)


class NewFileState(State):
    """
    新しいファイル作成状態を管理するクラス。

    Attributes:
        State (ABC): 基底クラスのState。
    """
    def handle_input(self, navigator: FileNavigator, key: int) -> None:
        """
        新しいファイル作成状態でのキー入力を処理します。

        Args:
            navigator (FileNavigator): ファイルナビゲーターのインスタンス。
            key (int): ユーザーが押したキー。
        """
        command = NewFileCommand()
        command.execute()
        navigator.refresh_file_list()
        navigator.set_state(FileListState())

    def display(self, navigator: FileNavigator) -> None:
        """
        新しいファイル作成画面を表示します（何も表示しない）。
        """
        pass


def get_initial_state() -> State:
    """
    初期状態としてFileListStateを返します。

    Returns:
        State: 初期状態のFileListStateオブジェクト。
    """
    return FileListState()
