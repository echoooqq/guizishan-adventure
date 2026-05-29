import pygame

ITEM_DATA = {
    "osmanthus_badge": {
        "name": "桂花徽章",
        "description": "金色的桂花徽章，散发着淡淡桂香",
        "color": (255, 200, 50),
        "usable": False,
        "stackable": True,
    },
    "campus_key": {
        "name": "校园钥匙",
        "description": "一把闪亮的钥匙，可以解锁新场景",
        "color": (220, 200, 50),
        "usable": True,
        "stackable": False,
    },
    "bookmark": {
        "name": "读书书签",
        "description": "精美的书签，使用后可查看谜题提示",
        "color": (180, 100, 200),
        "usable": True,
        "stackable": False,
    },
    "meal_card": {
        "name": "食堂饭卡",
        "description": "一张神秘的食堂饭卡，似乎有特殊用途",
        "color": (255, 150, 50),
        "usable": False,
        "stackable": False,
    },
    "treasure_chest": {
        "name": "秘境宝箱",
        "description": "最终秘境的宝箱，内含终极宝藏！",
        "color": (255, 215, 0),
        "usable": False,
        "stackable": False,
    },
}


class Item:
    def __init__(self, item_id, count=1):
        self.item_id = item_id
        data = ITEM_DATA.get(item_id, {})
        self.name = data.get("name", "未知道具")
        self.description = data.get("description", "")
        self.color = data.get("color", (200, 200, 200))
        self.usable = data.get("usable", False)
        self.stackable = data.get("stackable", False)
        self.count = count

    def add_count(self, n=1):
        if self.stackable:
            self.count += n
            return True
        return False

    def remove_count(self, n=1):
        if self.count >= n:
            self.count -= n
            return True
        return False

    def is_empty(self):
        return self.count <= 0

    def to_dict(self):
        return {"item_id": self.item_id, "count": self.count}

    @staticmethod
    def from_dict(data):
        return Item(data["item_id"], data.get("count", 1))


class Bag:
    def __init__(self):
        self.items = []
        self.selected_index = -1
        self.max_slots = 12

    def add_item(self, item_id, count=1):
        for item in self.items:
            if item.item_id == item_id and item.stackable:
                item.add_count(count)
                return True
        if len(self.items) < self.max_slots:
            self.items.append(Item(item_id, count))
            return True
        return False

    def remove_item(self, item_id, count=1):
        for item in self.items:
            if item.item_id == item_id:
                if item.remove_count(count):
                    if item.is_empty():
                        self.items.remove(item)
                        if self.selected_index >= len(self.items):
                            self.selected_index = len(self.items) - 1
                    return True
        return False

    def has_item(self, item_id, count=1):
        for item in self.items:
            if item.item_id == item_id and item.count >= count:
                return True
        return False

    def get_item_count(self, item_id):
        for item in self.items:
            if item.item_id == item_id:
                return item.count
        return 0

    def use_item(self, item_id):
        if self.has_item(item_id):
            item_data = ITEM_DATA.get(item_id, {})
            if item_data.get("usable", False):
                self.remove_item(item_id)
                return True
        return False

    def select_slot(self, index):
        if 0 <= index < len(self.items):
            self.selected_index = index
        else:
            self.selected_index = -1

    def get_selected_item(self):
        if 0 <= self.selected_index < len(self.items):
            return self.items[self.selected_index]
        return None

    def to_list(self):
        return [item.to_dict() for item in self.items]

    @staticmethod
    def from_list(data_list):
        bag = Bag()
        for d in data_list:
            bag.items.append(Item.from_dict(d))
        return bag

    def draw(self, surface, font_small, font_tiny, panel_rect):
        pw = panel_rect.width
        ph = panel_rect.height
        panel_surface = pygame.Surface((pw, ph), pygame.SRCALPHA)

        for y in range(ph):
            t = y / ph
            r = int(18 + t * 8)
            g = int(24 + t * 6)
            b = int(42 + t * 10)
            pygame.draw.line(panel_surface, (r, g, b), (0, y), (pw, y))

        pygame.draw.rect(panel_surface, (70, 110, 160),
                         (0, 0, pw, ph), 2)
        pygame.draw.line(panel_surface, (80, 130, 180),
                         (0, 32), (pw, 32), 1)

        title = font_small.render("背 包", True, (255, 220, 100))
        title_shadow = font_small.render("背 包", True, (30, 25, 15))
        panel_surface.blit(title_shadow, (12, 11))
        panel_surface.blit(title, (10, 9))

        slot_size = 48
        cols = 2
        margin = 6
        start_x = 10
        start_y = 42

        for i in range(self.max_slots):
            row = i // cols
            col = i % cols
            x = start_x + col * (slot_size + margin)
            y = start_y + row * (slot_size + margin)
            slot_rect = pygame.Rect(x, y, slot_size, slot_size)

            if i == self.selected_index:
                sel_glow = pygame.Surface((slot_size + 4, slot_size + 4), pygame.SRCALPHA)
                for gr in range(slot_size // 2, 0, -1):
                    ga = max(0, 35 - gr * 3)
                    pygame.draw.circle(sel_glow, (255, 210, 80, ga),
                                       (slot_size // 2 + 2, slot_size // 2 + 2), gr)
                panel_surface.blit(sel_glow, (x - 2, y - 2))
                pygame.draw.rect(panel_surface, (255, 210, 80), slot_rect, 2)
            else:
                bg_slot = pygame.Surface((slot_size, slot_size), pygame.SRCALPHA)
                bg_slot.fill((20, 28, 48, 140))
                panel_surface.blit(bg_slot, (x, y))
                pygame.draw.rect(panel_surface, (55, 75, 105), slot_rect, 1)

            if i < len(self.items):
                item = self.items[i]
                inner = pygame.Rect(x + 5, y + 5, slot_size - 10, slot_size - 10)
                ir, ig, ib = item.color
                for dy in range(inner.height):
                    shade = 1.0 - abs(dy - inner.height // 2) / (inner.height // 2) * 0.2
                    sc = (int(ir * shade), int(ig * shade), int(ib * shade))
                    pygame.draw.line(panel_surface, sc,
                                     (inner.left, inner.top + dy),
                                     (inner.right, inner.top + dy))
                pygame.draw.rect(panel_surface, (255, 255, 255, 120), inner, 1)

                name_short = item.name[:2]
                name_surf = font_tiny.render(name_short, True, (0, 0, 0))
                panel_surface.blit(name_surf, (x + 7, y + 7))

                if item.count > 1:
                    badge_w = 16
                    badge_h = 14
                    badge_surf = pygame.Surface((badge_w, badge_h), pygame.SRCALPHA)
                    badge_surf.fill((200, 50, 50, 220))
                    pygame.draw.rect(badge_surf, (255, 150, 150),
                                     (0, 0, badge_w, badge_h), 1, border_radius=3)
                    count_text = font_tiny.render(str(item.count), True, (255, 255, 255))
                    panel_surface.blit(badge_surf, (x + slot_size - badge_w - 2, y + slot_size - badge_h - 2))
                    panel_surface.blit(count_text, (x + slot_size - badge_w + 1, y + slot_size - badge_h))

        if 0 <= self.selected_index < len(self.items):
            item = self.items[self.selected_index]
            desc_y = start_y + (self.max_slots // cols) * (slot_size + margin) + 12

            desc_bg_w = pw - 20
            desc_bg_h = 62
            desc_bg = pygame.Surface((desc_bg_w, desc_bg_h), pygame.SRCALPHA)
            desc_bg.fill((10, 15, 30, 160))
            pygame.draw.rect(desc_bg, (60, 90, 130),
                             (0, 0, desc_bg_w, desc_bg_h), 1, border_radius=4)
            panel_surface.blit(desc_bg, (10, desc_y))

            name_surf = font_small.render(item.name, True, (255, 210, 100))
            panel_surface.blit(name_surf, (14, desc_y + 5))

            desc_line1 = item.description[:14] if len(item.description) > 14 else item.description
            desc_surf = font_tiny.render(desc_line1, True, (200, 205, 215))
            panel_surface.blit(desc_surf, (14, desc_y + 26))
            if len(item.description) > 14:
                desc_surf2 = font_tiny.render(item.description[14:], True, (200, 205, 215))
                panel_surface.blit(desc_surf2, (14, desc_y + 42))

            usable_tag = "可使用" if item.usable else ""
            if usable_tag:
                tag_surf = font_tiny.render(usable_tag, True, (100, 200, 140))
                panel_surface.blit(tag_surf, (desc_bg_w - 45, desc_y + 5))

        surface.blit(panel_surface, panel_rect.topleft)

    def handle_click(self, pos, panel_rect):
        if not panel_rect.collidepoint(pos):
            return None

        local_x = pos[0] - panel_rect.x
        local_y = pos[1] - panel_rect.y

        slot_size = 48
        cols = 2
        margin = 6
        start_x = 10
        start_y = 40

        for i in range(self.max_slots):
            row = i // cols
            col = i % cols
            x = start_x + col * (slot_size + margin)
            y = start_y + row * (slot_size + margin)
            slot_rect = pygame.Rect(x, y, slot_size, slot_size)
            if slot_rect.collidepoint(local_x, local_y):
                self.select_slot(i)
                if i < len(self.items):
                    return self.items[i]
                return None
        return None
