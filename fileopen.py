import curses
import os

def list_files(stdscr):
    # Clear screen
    stdscr.clear()

    # Get list of files in the current directory
    files = os.listdir('.')
    selected_index = 0  # 初期選択位置
    offset = 0  # スクロールオフセット

    # Enable keypad mode to capture special keys
    stdscr.keypad(True)

    # Get screen dimensions
    height, width = stdscr.getmaxyx()
    display_height = height - 3  # ファイルリスト表示エリアの高さ

    while True:
        # Display files with an indicator for the selected file
        stdscr.clear()
        for i in range(display_height):
            file_index = i + offset
            if file_index >= len(files):
                break
            file = files[file_index]
            display_name = file[:width - 4]  # 横幅に収めるために切り詰め
            if file_index == selected_index:
                stdscr.addstr(i, 0, f"> {display_name}", curses.A_REVERSE)  # 選択中のファイルを反転表示
            else:
                stdscr.addstr(i, 0, f"  {display_name}")
        
        # Refresh the screen to show the files
        stdscr.refresh()

        # Wait for user to select a file
        key = stdscr.getch()

        # Handle key press for navigation
        if key == curses.KEY_UP:
            if selected_index > 0:
                selected_index -= 1
                if selected_index < offset:
                    offset -= 1  # スクロールアップ
        elif key == curses.KEY_DOWN:
            if selected_index < len(files) - 1:
                selected_index += 1
                if selected_index >= offset + display_height:
                    offset += 1  # スクロールダウン
        elif key == ord('\n'):  # Enterキーでファイルの詳細を表示
            selected_file = files[selected_index]
            file_size = os.path.getsize(selected_file)
            stdscr.addstr(display_height + 1, 0, f"Selected file: {selected_file[:width - 15]}")
            stdscr.addstr(display_height + 2, 0, f"File size: {file_size} bytes")
            stdscr.refresh()
            stdscr.getch()  # ユーザーがもう一度キーを押すまで待機
        elif key == ord('q'):  # 'q'キーで終了
            break

# Initialize curses
curses.wrapper(list_files)
