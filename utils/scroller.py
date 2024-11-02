class Scroller:
    def __init__(self, selected_index: int, offset: int, display_height: int) -> None:
        self.selected_index = selected_index
        self.offset = offset
        self.display_height = display_height

    def scroll_up(self) -> None:
        if self.selected_index > 0:
            self.selected_index -= 1
            if self.selected_index < self.offset:
                self.offset -= 1

    def scroll_down(self, list_length: int) -> None:
        if self.selected_index < list_length - 1:
            self.selected_index += 1
            if self.selected_index >= self.offset + self.display_height:
                self.offset += 1
