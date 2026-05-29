import pygame
import json
import os

PUZZLE_DATA = {
    "library": {
        "type": "choice",
        "question": "以下哪本书不是中国四大名著之一？",
        "options": ["《西游记》", "《聊斋志异》", "《红楼梦》", "《三国演义》"],
        "answer": 1,
        "hint": "提示：四大名著是哪四部？排除法试试……",
        "success_text": "正确！《聊斋志异》是志怪小说集，并非四大名著！",
        "fail_text": "不对哦，回忆一下四大名著都有哪些……",
    },
    "boya_square": {
        "type": "choice",
        "question": "博雅一词出自哪部经典？",
        "options": ["《论语》", "《诗经》", "《楚辞》", "《尔雅》"],
        "answer": 3,
        "hint": "提示：博雅与'尔雅'有关，想想哪本书名含'雅'……",
        "success_text": "正确！博雅源自《尔雅》，寓意学识广博、品行端正！",
        "fail_text": "不对哦，博雅的出处是一部古代辞书……",
    },
    "youming_gym": {
        "type": "true_false",
        "questions": [
            {"question": "篮球比赛中，每队上场5人。", "answer": True},
            {"question": "马拉松全程是42.195公里。", "answer": True},
            {"question": "足球比赛每半场45分钟。", "answer": True},
        ],
        "hint": "提示：这些都是体育常识，仔细想想！",
        "success_text": "全部答对！你是体育达人！佑铭体育馆的秘境已解锁！",
        "fail_text": "有题目答错了，再试一次吧！",
    },
    "dining_hall": {
        "type": "find_item",
        "target_item": "meal_card",
        "success_text": "你找到了隐藏的食堂饭卡！学子食堂的秘境已解锁！",
    },
    "fountain_square": {
        "type": "choice",
        "question": "华中师范大学的校训是什么？",
        "options": ["求实创新、立德树人", "厚德博学、求实创新", "自强不息、厚德载物", "博学笃行、明德至善"],
        "answer": 1,
        "hint": "提示：华师校训强调品德与学识并重……",
        "success_text": "正确！华师校训'厚德博学、求实创新'！喷泉广场秘境已解锁！",
        "fail_text": "不对哦，华师的校训和品德、学识有关……",
    },
    "guizhong_road": {
        "type": "collect",
        "target_item": "osmanthus_badge",
        "target_count": 3,
        "success_text": "你收集齐了3枚桂花徽章！桂中路的秘境之门缓缓开启……",
    },
    "nanhu_building": {
        "type": "choice",
        "question": "华中师范大学建校于哪一年？",
        "options": ["1903年", "1924年", "1952年", "1949年"],
        "answer": 0,
        "hint": "提示：华师的前身是中华大学，历史悠久……",
        "success_text": "正确！华中师范大学前身可追溯至1903年创办的文华大学！",
        "fail_text": "不对哦，再想想华师的悠久历史吧……",
    },
    "night_secret": {
        "type": "choice",
        "question": "桂子山得名于什么？",
        "options": ["山上种满了桂花树", "一位叫桂子的人", "山形似桂花", "古人的诗句"],
        "answer": 0,
        "hint": "提示：秋天华师校园什么花最香？",
        "success_text": "正确！桂子山因满山桂花而得名，秋日飘香十里！你发现了最终秘境！",
        "fail_text": "不对哦，想想桂子山和桂花的关系……",
    },
}

ITEM_DATA = {
    "osmanthus_badge": {"name": "桂花徽章", "description": "金色的桂花徽章，散发着淡淡桂香", "color": (255, 200, 50), "usable": False, "stackable": True},
    "campus_key": {"name": "校园钥匙", "description": "一把闪亮的钥匙，可以解锁新场景", "color": (220, 200, 50), "usable": True, "stackable": False},
    "bookmark": {"name": "读书书签", "description": "精美的书签，使用后可查看谜题提示", "color": (180, 100, 200), "usable": True, "stackable": False},
    "meal_card": {"name": "食堂饭卡", "description": "一张神秘的食堂饭卡，似乎有特殊用途", "color": (255, 150, 50), "usable": False, "stackable": False},
    "treasure_chest": {"name": "秘境宝箱", "description": "最终秘境的宝箱，内含终极宝藏！", "color": (255, 215, 0), "usable": False, "stackable": False},
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
        return [{"item_id": i.item_id, "count": i.count} for i in self.items]

    @staticmethod
    def from_list(data_list):
        bag = Bag()
        for d in data_list:
            bag.items.append(Item(d["item_id"], d.get("count", 1)))
        return bag

    def draw(self, surface, font_small, font_tiny, panel_rect):
        pw, ph = panel_rect.width, panel_rect.height
        panel_surface = pygame.Surface((pw, ph), pygame.SRCALPHA)
        for y in range(ph):
            t = y / ph
            r = int(18 + t * 8)
            g = int(24 + t * 6)
            b = int(42 + t * 10)
            pygame.draw.line(panel_surface, (r, g, b), (0, y), (pw, y))
        pygame.draw.rect(panel_surface, (70, 110, 160), (0, 0, pw, ph), 2)
        pygame.draw.line(panel_surface, (80, 130, 180), (0, 32), (pw, 32), 1)

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

            if i == self.selected_index:
                sel_glow = pygame.Surface((slot_size + 4, slot_size + 4), pygame.SRCALPHA)
                for gr in range(slot_size // 2, 0, -2):
                    ga = max(0, 35 - gr * 3)
                    pygame.draw.circle(sel_glow, (255, 210, 80, ga),
                                       (slot_size // 2 + 2, slot_size // 2 + 2), gr)
                panel_surface.blit(sel_glow, (x - 2, y - 2))
                pygame.draw.rect(panel_surface, (255, 210, 80), (x, y, slot_size, slot_size), 2)
            else:
                bg_slot = pygame.Surface((slot_size, slot_size), pygame.SRCALPHA)
                bg_slot.fill((20, 28, 48, 140))
                panel_surface.blit(bg_slot, (x, y))
                pygame.draw.rect(panel_surface, (55, 75, 105), (x, y, slot_size, slot_size), 1)

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
                    badge_w, badge_h = 16, 14
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
            pygame.draw.rect(desc_bg, (60, 90, 130), (0, 0, desc_bg_w, desc_bg_h), 1, border_radius=4)
            panel_surface.blit(desc_bg, (10, desc_y))
            name_surf = font_small.render(item.name, True, (255, 210, 100))
            panel_surface.blit(name_surf, (14, desc_y + 5))
            desc_line1 = item.description[:14] if len(item.description) > 14 else item.description
            desc_surf = font_tiny.render(desc_line1, True, (200, 205, 215))
            panel_surface.blit(desc_surf, (14, desc_y + 26))
            if len(item.description) > 14:
                desc_surf2 = font_tiny.render(item.description[14:], True, (200, 205, 215))
                panel_surface.blit(desc_surf2, (14, desc_y + 42))
            if item.usable:
                tag_surf = font_tiny.render("可使用", True, (100, 200, 140))
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
        start_y = 42
        for i in range(self.max_slots):
            row = i // cols
            col = i % cols
            x = start_x + col * (slot_size + margin)
            y = start_y + row * (slot_size + margin)
            if pygame.Rect(x, y, slot_size, slot_size).collidepoint(local_x, local_y):
                self.select_slot(i)
                if i < len(self.items):
                    return self.items[i]
                return None
        return None


class PuzzleManager:
    def __init__(self):
        self.current_puzzle = None
        self.current_area_id = None
        self.tf_index = 0
        self.tf_correct = 0
        self.puzzle_active = False

    def start_puzzle(self, area_id):
        puzzle = PUZZLE_DATA.get(area_id)
        if puzzle is None:
            return False
        self.current_puzzle = puzzle
        self.current_area_id = area_id
        self.puzzle_active = True
        self.tf_index = 0
        self.tf_correct = 0
        return True

    def check_choice_answer(self, option_index):
        if self.current_puzzle is None or self.current_puzzle["type"] != "choice":
            return None
        return option_index == self.current_puzzle["answer"]

    def check_true_false(self, answer):
        if self.current_puzzle is None or self.current_puzzle["type"] != "true_false":
            return None
        questions = self.current_puzzle["questions"]
        if self.tf_index < len(questions):
            if answer == questions[self.tf_index]["answer"]:
                self.tf_correct += 1
            self.tf_index += 1
            if self.tf_index >= len(questions):
                return self.tf_correct == len(questions)
            return None
        return None

    def get_tf_question(self):
        if self.current_puzzle is None or self.current_puzzle["type"] != "true_false":
            return None
        questions = self.current_puzzle["questions"]
        if self.tf_index < len(questions):
            return questions[self.tf_index]
        return None

    def close_puzzle(self):
        self.current_puzzle = None
        self.current_area_id = None
        self.puzzle_active = False
        self.tf_index = 0
        self.tf_correct = 0


class ScoreSystem:
    def __init__(self):
        self.score = 0
        self.items_collected = 0
        self.areas_unlocked = 6
        self.puzzles_solved = 0

    def add_score(self, points):
        self.score += points

    def on_item_collected(self):
        self.items_collected += 1
        self.add_score(10)

    def on_puzzle_solved(self):
        self.puzzles_solved += 1
        self.add_score(50)

    def on_area_unlocked(self):
        self.areas_unlocked += 1
        self.add_score(30)

    def reset(self):
        self.score = 0
        self.items_collected = 0
        self.areas_unlocked = 6
        self.puzzles_solved = 0


SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "save_data.json")


class SaveSystem:
    @staticmethod
    def save_game(score_system, bag, world, player_pos, current_map="main"):
        data = {
            "score": score_system.score,
            "items_collected": score_system.items_collected,
            "areas_unlocked": score_system.areas_unlocked,
            "puzzles_solved": score_system.puzzles_solved,
            "bag": bag.to_list(),
            "player_x": player_pos[0],
            "player_y": player_pos[1],
            "current_map": current_map,
            "world_state": world.save_state() if hasattr(world, 'save_state') else {},
        }
        try:
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    @staticmethod
    def load_game():
        if not os.path.exists(SAVE_FILE):
            return None
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    @staticmethod
    def has_save():
        return os.path.exists(SAVE_FILE)

    @staticmethod
    def delete_save():
        if os.path.exists(SAVE_FILE):
            os.remove(SAVE_FILE)


SCENE_UNLOCK_CHAINS = {
    "library": "nanhu_building",
    "boya_square": "guizhong_road",
    "youming_gym": "boya_square",
    "dining_hall": "library",
    "fountain_square": "youming_gym",
}
