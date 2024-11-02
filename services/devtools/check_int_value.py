import curses

def key_debugger(stdscr):
    """
    スクリプトの説明
    stdscr.getch(): キー入力を取得します。各キーには対応する整数値があり、この値を利用してキー判定が可能です。
    キーの情報を表示:
    押したキーが表示可能な文字（ASCII範囲内）であればその文字と整数値を表示します。
    特殊キー（矢印キーやEnterキーなど）については、条件分岐を追加してキー名を表示します。
    終了条件:
    qキーが押されたときにbreakでループを抜け、プログラムが終了します。
    """
    stdscr.clear()
    stdscr.addstr(0, 0, "Press any key to see its integer value. Press 'q' to quit.")
    stdscr.refresh()

    while True:
        key = stdscr.getch()  # キー入力を取得
        stdscr.clear()

        if key == ord('q'):
            break  # 'q'が押されたら終了

        # キーの文字列表現と整数値を表示
        stdscr.addstr(0, 0, f"Key pressed: {chr(key) if 32 <= key <= 126 else 'Special Key'}")
        stdscr.addstr(1, 0, f"Integer value: {key}")
        
        # 特殊キーの場合の追加情報
        if key == curses.KEY_UP:
            stdscr.addstr(2, 0, "Detected: UP Arrow Key")
        elif key == curses.KEY_DOWN:
            stdscr.addstr(2, 0, "Detected: DOWN Arrow Key")
        elif key == curses.KEY_LEFT:
            stdscr.addstr(2, 0, "Detected: LEFT Arrow Key")
        elif key == curses.KEY_RIGHT:
            stdscr.addstr(2, 0, "Detected: RIGHT Arrow Key")
        elif key == curses.KEY_ENTER or key == 10 or key == 13:
            stdscr.addstr(2, 0, "Detected: ENTER Key")

        stdscr.addstr(4, 0, "Press 'q' to quit.")
        stdscr.refresh()

curses.wrapper(key_debugger)
