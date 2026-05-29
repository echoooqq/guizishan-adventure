class Camera:
    def __init__(self, map_width, map_height):
        self.x = 0.0
        self.y = 0.0
        self.map_width = map_width
        self.map_height = map_height
        from config import INTERNAL_WIDTH, INTERNAL_HEIGHT
        self.view_width = INTERNAL_WIDTH
        self.view_height = INTERNAL_HEIGHT

    def update(self, target_x, target_y):
        self.x = target_x - self.view_width // 2
        self.y = target_y - self.view_height // 2

        self.x = max(0, min(self.x, self.map_width - self.view_width))
        self.y = max(0, min(self.y, self.map_height - self.view_height))

        if self.map_width < self.view_width:
            self.x = (self.map_width - self.view_width) // 2
        if self.map_height < self.view_height:
            self.y = (self.map_height - self.view_height) // 2

    def apply(self, x, y):
        return x - self.x, y - self.y

    def get_visible_tile_range(self, tile_size):
        start_col = max(0, int(self.x // tile_size))
        start_row = max(0, int(self.y // tile_size))
        end_col = min(self.map_width // tile_size, int((self.x + self.view_width) // tile_size) + 1)
        end_row = min(self.map_height // tile_size, int((self.y + self.view_height) // tile_size) + 1)
        return start_row, end_row, start_col, end_col
