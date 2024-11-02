class Scroller:
    """
    Scrollerクラスは、リストのスクロール機能を提供します。
    """

    def __init__(self, selected_index: int, offset: int, display_height: int) -> None:
        """
        コンストラクタ。初期状態を設定します。

        :param selected_index: 選択されたインデックス
        :param offset: 表示オフセット
        :param display_height: 表示領域の高さ
        """
        self.selected_index = selected_index
        self.offset = offset
        self.display_height = display_height

    def scroll_up(self) -> None:
        """
        リストを1つ上にスクロールします。
        """
        if self.selected_index > 0:
            self.selected_index -= 1
            if self.selected_index < self.offset:
                self.offset -= 1

    def scroll_down(self, list_length: int) -> None:
        """
        リストを1つ下にスクロールします。

        :param list_length: リストの長さ
        """
        if self.selected_index < list_length - 1:
            self.selected_index += 1
            if self.selected_index >= self.offset + self.display_height:
                self.offset += 1
