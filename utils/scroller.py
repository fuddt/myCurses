class Scroller:
    def __init__(self, selected_index, offset, display_height):
        self.selected_index = selected_index
        self.offset = offset
        self.display_height = display_height

    def scroll_up(self):
        if self.selected_index > 0:
            self.selected_index -= 1
            if self.selected_index < self.offset:
                self.offset -= 1

    def scroll_down(self, files_length):
        if self.selected_index < files_length - 1:
            self.selected_index += 1
            if self.selected_index >= self.offset + self.display_height:
                self.offset += 1
