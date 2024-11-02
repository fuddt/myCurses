import curses
import os
from utils.scroller import Scroller
from services.states import State, get_initial_state

class FileNavigator:
    """
    FileNavigatorクラスは、ファイルナビゲーションのロジックを管理します。
    cursesライブラリを使用して、ターミナル上でファイルの一覧表示や操作を行います。
    """

    def __init__(self, stdscr: curses.window) -> None:
        """
        コンストラクタ。初期状態を設定します。

        :param stdscr: cursesウィンドウオブジェクト
        """
        self.stdscr = stdscr
        self.current_dir = os.getcwd()
        self.files = [".."] + os.listdir(self.current_dir)
        self.selected_option = 0
        self.scroller = Scroller(0, 0, self.stdscr.getmaxyx()[0] - 4)  # 表示領域を少し下げる
        self.state = get_initial_state()  # 初期状態を設定
        self.exit_flag = False

    def set_state(self, state: State) -> None:
        """
        状態を設定します。

        :param state: 新しい状態
        """
        self.state = state

    def refresh_file_list(self) -> None:
        """
        ファイルリストを更新します。
        """
        self.files = [".."] + os.listdir(self.current_dir)

    def display_files(self) -> None:
        """
        ファイル一覧を表示します。
        """
        self.stdscr.clear()
        for i in range(self.scroller.display_height):
            file_index = i + self.scroller.offset
            if file_index >= len(self.files):
                break
            file = self.files[file_index]
            display_name = file[: self.stdscr.getmaxyx()[1] - 4]
            if file_index == self.scroller.selected_index:
                self.stdscr.addstr(i, 0, f"> {display_name}", curses.A_REVERSE)
            else:
                self.stdscr.addstr(i, 0, f"  {display_name}")
        # 常に q の説明を表示
        self.stdscr.addstr(self.scroller.display_height + 1, 0, "Press 'n' to create a new file.")
        self.stdscr.addstr(self.scroller.display_height + 2, 0, "Press 'q' to quit.")
        self.stdscr.refresh()

    def display_menu(self) -> None:
        """
        メニューを表示します。
        """
        self.stdscr.clear()
        menu_options = ["view", "edit", "remove", "back"]
        for i, option in enumerate(menu_options):
            if i == self.selected_option:
                self.stdscr.addstr(i, 0, f"> {option}", curses.A_REVERSE)
            else:
                self.stdscr.addstr(i, 0, f"  {option}")
        # メニュー画面にも q の説明を追加
        self.stdscr.addstr(len(menu_options), 0, "Press 'q' to quit.")
        self.stdscr.refresh()

    def run(self) -> None:
        """
        メインループを実行します。ユーザーの入力を処理し、状態を更新します。
        """
        while not self.exit_flag:
            self.state.display(self)
            key = self.stdscr.getch()
            # q が押されたらアプリ終了
            if key == ord('q'):
                self.exit()
            else:
                self.state.handle_input(self, key)

    def exit(self) -> None:
        """
        アプリケーションを終了します。
        """
        self.exit_flag = True

# cursesアプリケーションのエントリーポイント
def list_files(stdscr: curses.window) -> None:
    """
    cursesアプリケーションのエントリーポイント。FileNavigatorを初期化し、実行します。

    :param stdscr: cursesウィンドウオブジェクト
    """
    stdscr.clear()
    stdscr.keypad(True)
    navigator = FileNavigator(stdscr)
    navigator.run()

curses.wrapper(list_files)
