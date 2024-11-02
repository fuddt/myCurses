import curses
import os
import subprocess
from utils.scroller import Scroller

class Option:
    def __init__(self, display_name: str, action) -> None:
        """
        オプションクラスの初期化

        :param display_name: 表示名
        :param action: 実行関数
        """
        self.display_name = display_name
        self.action = action

class FileNavigator:
    def __init__(self, stdscr: curses.window) -> None:
        """
        指定されたcursesウィンドウでFileNavigatorを初期化します。

        :param stdscr: cursesウィンドウオブジェクト。
        """
        self.stdscr = stdscr
        self.current_dir = os.getcwd()  # 現在のディレクトリを取得
        self.files = ['..'] + os.listdir(self.current_dir)  # ファイルリストを取得
        self.selected_index = 0  # 選択されたファイルのインデックス
        self.offset = 0  # 表示オフセット
        self.height, self.width = self.stdscr.getmaxyx()  # ウィンドウの高さと幅を取得
        self.display_height = self.height - 3  # 表示可能な高さを設定
        self.scroller = Scroller(self.selected_index, self.offset, self.display_height)
        self.menu_options = [
            Option("view", self.view_file),
            Option("edit", self.edit_file),
            Option("remove", self.remove_file),
            Option("new", self.new_file)
        ]

    def clear_and_refresh_window(self) -> None:
        """
        ウィンドウをクリアして更新します。
        """
        self.stdscr.clear()
        self.stdscr.refresh()

    def run_subprocess(self, command: list) -> None:
        """
        サブプロセスを実行します。

        :param command: 実行するコマンドのリスト。
        """
        self.clear_and_refresh_window()
        curses.endwin()  # cursesモードを終了
        subprocess.run(command)  # コマンドを実行
        curses.doupdate()  # cursesモードを再開

    def update_file_list(self) -> None:
        """
        現在のディレクトリのファイルリストを更新します。
        """
        self.files = ['..'] + os.listdir(self.current_dir)  # ファイルリストを再取得
        self.selected_index = 0  # 選択インデックスをリセット
        self.offset = 0  # オフセットをリセット

    def display_files(self) -> None:
        """
        cursesウィンドウにファイルリストを表示します。
        """
        self.stdscr.clear()  # ウィンドウをクリア
        for i in range(self.display_height):
            file_index = i + self.offset  # 表示するファイルのインデックスを計算
            if file_index >= len(self.files):
                break  # ファイルリストの終わりに達したらループを終了
            file = self.files[file_index]
            display_name = file[:self.width - 4]  # 表示名をウィンドウ幅に合わせて切り詰め
            if file_index == self.selected_index:
                self.stdscr.addstr(i, 0, f"> {display_name}", curses.A_REVERSE)  # 選択されたファイルを反転表示
            else:
                self.stdscr.addstr(i, 0, f"  {display_name}")  # 通常表示
        self.stdscr.refresh()  # ウィンドウを更新

    def display_menu(self) -> str:
        """
        メニューを表示し、選択されたオプションを返します。

        :return: 選択されたオプション（view, edit, remove, new）。
        """
        selected_option = 0

        while True:
            self.clear_and_refresh_window()
            for i, option in enumerate(self.menu_options):
                if i == selected_option:
                    self.stdscr.addstr(i, 0, f"> {option.display_name}", curses.A_REVERSE)
                else:
                    self.stdscr.addstr(i, 0, f"  {option.display_name}")
            self.stdscr.refresh()

            key = self.stdscr.getch()
            if key == curses.KEY_UP and selected_option > 0:
                selected_option -= 1
            elif key == curses.KEY_DOWN and selected_option < len(self.menu_options) - 1:
                selected_option += 1
            elif key == ord('\n'):
                return self.menu_options[selected_option]

    def add_option(self, option: Option) -> None:
        """
        メニューオプションを追加します。

        :param option: 追加するオプション。
        """
        self.menu_options.append(option)

    def handle_key_press(self, key: int) -> bool:
        """
        キー押下イベントを処理します。

        :param key: 押されたキーのコード。
        :return: 'q'キーが押された場合はFalse、それ以外はTrue。
        """
        if key == curses.KEY_UP:
            self.scroller.scroll_up()
        elif key == curses.KEY_DOWN:
            self.scroller.scroll_down(len(self.files))
        elif key == ord('\n'):
            selected_file = self.files[self.selected_index]
            if os.path.isdir(selected_file):
                self.current_dir = os.path.abspath(selected_file)  # ディレクトリを変更
                os.chdir(self.current_dir)  # カレントディレクトリを変更
                self.update_file_list()  # ファイルリストを更新
            else:
                option = self.display_menu()
                option.action(selected_file)
        elif key == ord('q'):
            return False  # 'q'キーが押されたら終了
        return True

    def view_file(self, selected_file: str) -> None:
        """
        ファイルを表示します。

        :param selected_file: 表示するファイル。
        """
        self.run_subprocess(['less', selected_file])  # lessコマンドでファイルを表示

    def edit_file(self, selected_file: str) -> None:
        """
        ファイルを編集します。

        :param selected_file: 編集するファイル。
        """
        self.run_subprocess(['vim', selected_file])  # vimでファイルを編集

    def remove_file(self, selected_file: str) -> None:
        """
        ファイルを削除します。

        :param selected_file: 削除するファイル。
        """
        self.clear_and_refresh_window()
        self.stdscr.addstr(0, 0, f"Are you sure you want to remove {selected_file}? (y/n)")
        self.stdscr.refresh()
        confirm_key = self.stdscr.getch()
        if confirm_key == ord('y'):
            os.remove(selected_file)  # ファイルを削除
            self.update_file_list()  # ファイルリストを更新

    def new_file(self, selected_file: str) -> None:
        """
        新しいファイルを作成します。

        :param selected_file: 作成するファイル。
        """
        self.clear_and_refresh_window()
        self.stdscr.addstr(0, 0, "Enter the new filename: ")
        curses.echo()
        filename = self.stdscr.getstr().decode('utf-8')
        curses.noecho()
        self.run_subprocess(['vim', filename])  # vimで新しいファイルを作成

def list_files(stdscr: curses.window) -> None:
    """
    cursesを使用してファイルをリスト表示するメイン関数。

    :param stdscr: cursesウィンドウオブジェクト。
    """
    stdscr.clear()  # ウィンドウをクリア
    stdscr.keypad(True)  # キーパッドモードを有効にする
    navigator = FileNavigator(stdscr)  # FileNavigatorオブジェクトを作成

    while True:
        navigator.display_files()  # ファイルリストを表示
        key = stdscr.getch()  # キー入力を取得
        if not navigator.handle_key_press(key):
            break  # 'q'キーが押されたらループを終了

curses.wrapper(list_files)  # cursesアプリケーションを実行
