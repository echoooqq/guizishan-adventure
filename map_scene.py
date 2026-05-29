import pygame
import random
import math

SCENE_WIDTH = 800
SCENE_HEIGHT = 600

COLOR_BG = {
    "guizhong_road": (180, 210, 140),
    "nanhu_building": (160, 180, 210),
    "library": (140, 120, 100),
    "boya_square": (200, 200, 160),
    "youming_gym": (170, 160, 190),
    "dining_hall": (210, 180, 150),
    "fountain_square": (150, 190, 220),
    "night_secret": (30, 20, 60),
}

SCENE_NAMES = {
    "guizhong_road": "桂中路",
    "nanhu_building": "南湖综合楼",
    "library": "校图书馆",
    "boya_square": "博雅广场",
    "youming_gym": "佑铭体育馆",
    "dining_hall": "学子食堂",
    "fountain_square": "喷泉广场",
    "night_secret": "桂子山夜景秘境",
}

SCENE_DESCRIPTIONS = {
    "guizhong_road": "桂中路两旁桂花飘香，传说秋日里散落的桂花瓣中隐藏着秘境的线索……",
    "nanhu_building": "南湖综合楼巍峨矗立，计算机学院的学子们在此求索，楼中藏着建校的古老记忆……",
    "library": "校图书馆书香四溢，千万卷藏书中暗藏着通往秘境的智慧钥匙……",
    "boya_square": "博雅广场开阔宁静，草坪上偶尔闪过奇异的光芒，似乎在指引着什么……",
    "youming_gym": "佑铭体育馆热血沸腾，运动健儿们挥洒汗水，这里也藏着考验智慧的关卡……",
    "dining_hall": "学子食堂烟火气十足，据说有同学在角落里捡到过一张神秘的饭卡……",
    "fountain_square": "喷泉广场水花飞溅，夜晚的灯光映照下，喷泉似乎在诉说着古老的校史……",
    "night_secret": "桂子山夜幕降临，月光洒落，一个隐藏的秘境缓缓浮现……",
}

SCENE_UNLOCK_RULES = {
    "guizhong_road": None,
    "nanhu_building": None,
    "library": "nanhu_building",
    "boya_square": "guizhong_road",
    "youming_gym": "boya_square",
    "dining_hall": "library",
    "fountain_square": "youming_gym",
    "night_secret": None,
}

SCENE_CONNECTIONS = {
    "guizhong_road": ["nanhu_building", "boya_square"],
    "nanhu_building": ["guizhong_road", "library"],
    "library": ["nanhu_building", "dining_hall"],
    "boya_square": ["guizhong_road", "youming_gym"],
    "youming_gym": ["boya_square", "fountain_square"],
    "dining_hall": ["library", "fountain_square"],
    "fountain_square": ["youming_gym", "dining_hall"],
    "night_secret": ["fountain_square"],
}

PUZZLE_DATA = {
    "nanhu_building": {
        "type": "choice",
        "question": "华中师范大学建校于哪一年？",
        "options": ["1903年", "1924年", "1952年", "1949年"],
        "answer": 0,
        "hint": "提示：华师的前身是中华大学，历史悠久……",
        "success_text": "正确！华中师范大学前身可追溯至1903年创办的文华大学！",
        "fail_text": "不对哦，再想想华师的悠久历史吧……",
    },
    "library": {
        "type": "choice",
        "question": "以下哪本书不是中国四大名著之一？",
        "options": ["《西游记》", "《聊斋志异》", "《红楼梦》", "《三国演义》"],
        "answer": 1,
        "hint": "提示：四大名著是哪四部？排除法试试……",
        "success_text": "正确！《聊斋志异》是志怪小说集，并非四大名著！",
        "fail_text": "不对哦，回忆一下四大名著都有哪些……",
    },
    "guizhong_road": {
        "type": "collect",
        "target_item": "osmanthus_badge",
        "target_count": 3,
        "success_text": "你收集齐了3枚桂花徽章！桂中路的秘境之门缓缓开启……",
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
    "boya_square": {
        "type": "choice",
        "question": "博雅一词出自哪部经典？",
        "options": ["《论语》", "《诗经》", "《楚辞》", "《尔雅》"],
        "answer": 3,
        "hint": "提示：博雅与'尔雅'有关，想想哪本书名含'雅'……",
        "success_text": "正确！博雅源自《尔雅》，寓意学识广博、品行端正！",
        "fail_text": "不对哦，博雅的出处是一部古代辞书……",
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


class InteractiveObject:
    def __init__(self, name, x, y, width, height, obj_type="decoration",
                 description="", item_id=None, color=(200, 200, 200)):
        self.name = name
        self.rect = pygame.Rect(x, y, width, height)
        self.obj_type = obj_type
        self.description = description
        self.item_id = item_id
        self.color = color
        self.interacted = False
        self.visible = True
        self.glow_timer = 0

    def update(self, dt):
        self.glow_timer += dt

    def draw(self, surface):
        if not self.visible:
            return
        glow = int(abs(pygame.math.Vector2(1, 0).rotate(self.glow_timer * 120).x * 40)
                   if self.obj_type in ("item", "puzzle") else 0)
        color = tuple(min(255, c + glow) for c in self.color)
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2)
        if self.obj_type == "item" and not self.interacted:
            star_y = self.rect.centery + int(abs(pygame.math.Vector2(1, 0).rotate(self.glow_timer * 180).y) * 5)
            pygame.draw.circle(surface, (255, 255, 100),
                               (self.rect.centerx, star_y), 4)

    def check_collision(self, player_rect):
        return self.rect.colliderect(player_rect)

    def check_click(self, pos):
        return self.rect.collidepoint(pos)


class Scene:
    def __init__(self, scene_id):
        self.scene_id = scene_id
        self.name = SCENE_NAMES.get(scene_id, "未知场景")
        self.description = SCENE_DESCRIPTIONS.get(scene_id, "")
        self.bg_color = COLOR_BG.get(scene_id, (100, 100, 100))
        self.unlocked = scene_id in ("guizhong_road", "nanhu_building")
        self.puzzle_solved = False
        self.objects = []
        self.npc_dialogues = []
        self.particles = []
        self._build_objects()

    def _build_objects(self):
        self.objects = []
        if self.scene_id == "guizhong_road":
            self._build_guizhong_road()
        elif self.scene_id == "nanhu_building":
            self._build_nanhu_building()
        elif self.scene_id == "library":
            self._build_library()
        elif self.scene_id == "boya_square":
            self._build_boy_square()
        elif self.scene_id == "youming_gym":
            self._build_youming_gym()
        elif self.scene_id == "dining_hall":
            self._build_dining_hall()
        elif self.scene_id == "fountain_square":
            self._build_fountain_square()
        elif self.scene_id == "night_secret":
            self._build_night_secret()

    def _build_guizhong_road(self):
        self.objects.append(InteractiveObject(
            "桂花树", 50, 80, 80, 120, "decoration",
            "金桂飘香，桂子山因此得名", color=(100, 160, 60)))
        self.objects.append(InteractiveObject(
            "桂花树", 650, 60, 80, 130, "decoration",
            "银桂如雪，清香四溢", color=(100, 160, 60)))
        self.objects.append(InteractiveObject(
            "桂花徽章", 200, 350, 30, 30, "item",
            "一枚闪着金光的桂花徽章", "osmanthus_badge", (255, 200, 50)))
        self.objects.append(InteractiveObject(
            "桂花徽章", 450, 250, 30, 30, "item",
            "一枚闪着金光的桂花徽章", "osmanthus_badge", (255, 200, 50)))
        self.objects.append(InteractiveObject(
            "桂花徽章", 600, 400, 30, 30, "item",
            "一枚闪着金光的桂花徽章", "osmanthus_badge", (255, 200, 50)))
        self.objects.append(InteractiveObject(
            "石碑", 350, 150, 60, 80, "puzzle",
            "桂中路石碑：收集3枚桂花徽章可开启秘境", color=(160, 160, 160)))
        self.objects.append(InteractiveObject(
            "长椅", 500, 380, 70, 30, "decoration",
            "一张安静的长椅，适合读书", color=(139, 90, 43)))

    def _build_nanhu_building(self):
        self.objects.append(InteractiveObject(
            "综合楼主楼", 250, 50, 300, 200, "decoration",
            "南湖综合楼，计算机学院所在地", color=(120, 140, 180)))
        self.objects.append(InteractiveObject(
            "校史展板", 100, 300, 80, 60, "puzzle",
            "展板上写着华师建校的历史……点击答题", color=(200, 180, 140)))
        self.objects.append(InteractiveObject(
            "校园钥匙", 600, 350, 30, 30, "item",
            "一把闪亮的校园钥匙，似乎能打开某处秘境", "campus_key", (220, 200, 50)))
        self.objects.append(InteractiveObject(
            "计算机", 400, 350, 50, 40, "decoration",
            "一台计算机，屏幕上闪烁着代码", color=(80, 80, 80)))

    def _build_library(self):
        self.objects.append(InteractiveObject(
            "书架", 50, 80, 60, 180, "decoration",
            "满满的书架，知识的海洋", color=(120, 80, 40)))
        self.objects.append(InteractiveObject(
            "书架", 680, 80, 60, 180, "decoration",
            "满满的书架，书香四溢", color=(120, 80, 40)))
        self.objects.append(InteractiveObject(
            "阅读台", 300, 200, 80, 50, "puzzle",
            "阅读台上放着一道文学题目……点击答题", color=(160, 120, 60)))
        self.objects.append(InteractiveObject(
            "读书书签", 500, 300, 30, 30, "item",
            "一枚精美的读书书签，可以解锁题库提示", "bookmark", (180, 100, 200)))
        self.objects.append(InteractiveObject(
            "自助借还机", 150, 350, 50, 60, "decoration",
            "自助借还书机，方便快捷", color=(100, 100, 120)))

    def _build_boy_square(self):
        self.objects.append(InteractiveObject(
            "草坪", 200, 200, 400, 200, "decoration",
            "碧绿的草坪，阳光正好", color=(80, 180, 80)))
        self.objects.append(InteractiveObject(
            "博雅石碑", 350, 150, 80, 60, "puzzle",
            "博雅石碑上刻着古老的文字……点击答题", color=(180, 180, 180)))
        self.objects.append(InteractiveObject(
            "桂花徽章", 250, 350, 30, 30, "item",
            "草坪上闪着微光的桂花徽章", "osmanthus_badge", (255, 200, 50)))
        self.objects.append(InteractiveObject(
            "路灯", 550, 100, 20, 100, "decoration",
            "一盏古典路灯，夜晚格外美丽", color=(100, 100, 100)))

    def _build_youming_gym(self):
        self.objects.append(InteractiveObject(
            "篮球架", 100, 100, 60, 120, "decoration",
            "标准的篮球架，随时可以投篮", color=(200, 100, 50)))
        self.objects.append(InteractiveObject(
            "跑道", 300, 400, 300, 40, "decoration",
            "红色的塑胶跑道", color=(200, 60, 60)))
        self.objects.append(InteractiveObject(
            "体育知识板", 400, 200, 80, 60, "puzzle",
            "体育知识问答板……点击答题", color=(180, 160, 200)))
        self.objects.append(InteractiveObject(
            "校园钥匙", 600, 300, 30, 30, "item",
            "跑道边遗落的校园钥匙", "campus_key", (220, 200, 50)))

    def _build_dining_hall(self):
        self.objects.append(InteractiveObject(
            "打饭窗口", 200, 80, 400, 60, "decoration",
            "热气腾腾的打饭窗口，菜香扑鼻", color=(200, 160, 100)))
        self.objects.append(InteractiveObject(
            "餐桌", 150, 250, 80, 50, "decoration",
            "一张餐桌，同学们正在用餐", color=(160, 120, 80)))
        self.objects.append(InteractiveObject(
            "餐桌", 350, 250, 80, 50, "decoration",
            "一张餐桌，上面摆着餐具", color=(160, 120, 80)))
        self.objects.append(InteractiveObject(
            "隐藏饭卡", 550, 380, 30, 30, "item",
            "角落里一张神秘的食堂饭卡", "meal_card", (255, 150, 50)))
        self.objects.append(InteractiveObject(
            "失物招领处", 600, 150, 80, 50, "puzzle",
            "失物招领处：找到隐藏的饭卡即可通关", color=(150, 150, 180)))

    def _build_fountain_square(self):
        self.objects.append(InteractiveObject(
            "喷泉", 300, 150, 200, 150, "decoration",
            "美丽的喷泉，水花在灯光下闪耀", color=(100, 160, 220)))
        self.objects.append(InteractiveObject(
            "校史碑", 100, 350, 70, 80, "puzzle",
            "校史碑上刻着华师的校训……点击答题", color=(160, 160, 160)))
        self.objects.append(InteractiveObject(
            "桂花徽章", 600, 250, 30, 30, "item",
            "喷泉边闪光的桂花徽章", "osmanthus_badge", (255, 200, 50)))
        self.objects.append(InteractiveObject(
            "夜景入口", 650, 400, 60, 80, "puzzle",
            "一扇若隐若现的光门，通往桂子山夜景秘境……", color=(80, 50, 120)))

    def _build_night_secret(self):
        self.objects.append(InteractiveObject(
            "月光台", 300, 200, 200, 100, "puzzle",
            "月光照耀的石台，上面刻着桂子山的秘密……点击答题",
            color=(60, 50, 100)))
        self.objects.append(InteractiveObject(
            "桂花树(夜)", 80, 100, 80, 150, "decoration",
            "月光下的桂花树，银光闪闪", color=(40, 80, 40)))
        self.objects.append(InteractiveObject(
            "桂花树(夜)", 620, 100, 80, 150, "decoration",
            "夜色中的桂花树，暗香浮动", color=(40, 80, 40)))
        self.objects.append(InteractiveObject(
            "宝箱", 380, 420, 50, 40, "item",
            "最终秘境宝箱！内含终极宝藏", "treasure_chest", (255, 215, 0)))

    def update(self, dt):
        for obj in self.objects:
            obj.update(dt)
        self._update_particles(dt)

    def _update_particles(self, dt):
        new_particles = []
        for p in self.particles:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["life"] -= dt
            if p["life"] > 0:
                new_particles.append(p)
        self.particles = new_particles

    def add_particle(self, x, y, color=(255, 255, 200)):
        for _ in range(8):
            self.particles.append({
                "x": x, "y": y,
                "vx": random.uniform(-60, 60),
                "vy": random.uniform(-80, 20),
                "life": random.uniform(0.3, 0.8),
                "color": color,
            })

    def draw(self, surface, font_small):
        surface.fill(self.bg_color)
        self._draw_scene_details(surface, font_small)
        for obj in self.objects:
            obj.draw(surface)
        self._draw_particles(surface)
        self._draw_scene_label(surface, font_small)

    def _draw_scene_details(self, surface, font):
        if self.scene_id == "guizhong_road":
            self._draw_guizhong_detailed(surface)
        elif self.scene_id == "nanhu_building":
            self._draw_nanhu_detailed(surface, font)
        elif self.scene_id == "library":
            self._draw_library_detailed(surface, font)
        elif self.scene_id == "boya_square":
            self._draw_boya_detailed(surface, font)
        elif self.scene_id == "youming_gym":
            self._draw_youming_detailed(surface, font)
        elif self.scene_id == "dining_hall":
            self._draw_dining_detailed(surface, font)
        elif self.scene_id == "fountain_square":
            self._draw_fountain_detailed(surface, font)
        elif self.scene_id == "night_secret":
            self._draw_night_detailed(surface, font)

    def _draw_guizhong_detailed(self, surface):
        sky = pygame.Surface((SCENE_WIDTH, 200), pygame.SRCALPHA)
        for i in range(200):
            r = int(135 + (i / 200) * 45)
            g = int(195 + (i / 200) * 20)
            b = int(120 + (i / 200) * 25)
            pygame.draw.line(sky, (r, g, b), (0, i), (SCENE_WIDTH, i))
        surface.blit(sky, (0, 0))

        ground = pygame.Surface((SCENE_WIDTH, 400), pygame.SRCALPHA)
        for i in range(400):
            v = int(160 + ((i % 60) / 60) * 20)
            pygame.draw.line(ground, (v + 15, v + 5, v - 10), (0, i), (SCENE_WIDTH, i))
        surface.blit(ground, (0, 200))

        pygame.draw.rect(surface, (170, 155, 120), (0, 440, SCENE_WIDTH, 10))
        for x in range(0, SCENE_WIDTH, 80):
            pygame.draw.line(surface, (150, 140, 110), (x, 445), (x + 50, 445), 2)

        tree_data = [(70, 100), (680, 80)]
        for tx, ty in tree_data:
            trunk_color = (90, 65, 35)
            pygame.draw.rect(surface, trunk_color, (tx + 22, ty + 90, 16, 55))
            for layer in range(3):
                cy = ty + 75 - layer * 28
                cr = 42 - layer * 7
                color = (70 + layer * 18, 145 - layer * 12, 50 + layer * 8)
                pygame.draw.ellipse(surface, color,
                                   (tx + 24 - cr, cy - cr // 2, cr * 2, cr + 10))

        lamp_positions = [(250, 380), (550, 380)]
        for lx, ly in lamp_positions:
            pole_color = (70, 70, 78)
            pygame.draw.rect(surface, pole_color, (lx + 4, ly, 6, 72))
            head_color = (210, 190, 130)
            pygame.draw.ellipse(surface, head_color, (lx - 2, ly - 8, 24, 16))
            glow_surf = pygame.Surface((36, 28), pygame.SRCALPHA)
            for gx in range(36):
                for gy in range(28):
                    dist = ((gx - 18) ** 2 + (gy - 14) ** 2) ** 0.5
                    alpha = max(0, int(30 - dist * 1.2))
                    if alpha > 0:
                        glow_surf.set_at((gx, gy), (255, 240, 180, alpha))
            surface.blit(glow_surf, (lx - 6, ly - 10))

        petal_colors = [(255, 215, 100), (255, 230, 150), (255, 200, 80)]
        for _ in range(18):
            px = random.randint(30, SCENE_WIDTH - 30)
            py = random.randint(420, 580)
            pc = random.choice(petal_colors)
            size = random.randint(2, 4)
            pygame.draw.ellipse(surface, pc, (px, py, size, size + 1))

    def _draw_nanhu_detailed(self, surface, font):
        sky = pygame.Surface((SCENE_WIDTH, 280), pygame.SRCALPHA)
        for i in range(280):
            t = i / 280.0
            r = int(115 + t * 50)
            g = int(140 + t * 45)
            b = int(185 + t * 25)
            pygame.draw.line(sky, (r, g, b), (0, i), (SCENE_WIDTH, i))
        surface.blit(sky, (0, 0))

        ground = pygame.Surface((SCENE_WIDTH, 320), pygame.SRCALPHA)
        for i in range(320):
            v = int(175 + ((i % 40) / 40) * 15)
            pygame.draw.line(ground, (v, v + 8, v + 20), (0, i), (SCENE_WIDTH, i))
        surface.blit(ground, (0, 280))

        bx, by, bw, bh = 220, 60, 360, 245

        shadow = pygame.Surface((bw + 20, 30), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 40))
        surface.blit(shadow, (bx - 10, by + bh + 5))

        base_color = (95, 112, 148)
        pygame.draw.rect(surface, base_color, (bx, by, bw, bh))
        roof_color = (75, 88, 118)
        pygame.draw.rect(surface, roof_color, (bx - 8, by - 12, bw + 16, 18))

        accent_line = (130, 152, 192)
        pygame.draw.line(surface, accent_line, (bx, by + bh - 8),
                         (bx + bw, by + bh - 8), 3)

        door_w, door_h = 48, 85
        door_x = bx + bw // 2 - door_w // 2
        door_y = by + bh - door_h
        pygame.draw.rect(surface, (62, 48, 32), (door_x, door_y, door_w, door_h))
        pygame.draw.circle(surface, (200, 170, 80), (door_x + door_w - 10, door_y + door_h // 2), 4)

        win_rows, win_cols = 5, 5
        win_w, win_h = 52, 34
        margin_x = (bw - win_cols * win_w) // (win_cols + 1)
        margin_y = 26
        for row in range(win_rows):
            for col in range(win_cols):
                wx = bx + margin_x + col * (win_w + margin_x)
                wy = by + 18 + row * (win_h + margin_y)
                frame = (58, 68, 92)
                pygame.draw.rect(surface, frame, (wx, wy, win_w, win_h))
                glass = (178, 212, 255) if (row + col) % 2 == 0 else (162, 198, 248)
                inner = 4
                pygame.draw.rect(surface, glass, (wx + inner, wy + inner,
                                                   win_w - inner * 2, win_h - inner * 2))

        sign_x, sign_y = bx + bw + 20, by + bh - 60
        pygame.draw.rect(surface, (142, 125, 95), (sign_x, sign_y, 56, 44))
        sign_text = font.render("南湖", True, (235, 225, 200))
        surface.blit(sign_text, (sign_x + 10, sign_y + 8))
        sign_text2 = font.render("综合楼", True, (235, 225, 200))
        surface.blit(sign_text2, (sign_x + 6, sign_y + 24))

        path_color = (158, 148, 128)
        pygame.draw.ellipse(surface, path_color, (320, 500, 160, 90))

    def _draw_library_detailed(self, surface, font):
        bg_top = pygame.Surface((SCENE_WIDTH, 260), pygame.SRCALPHA)
        for i in range(260):
            t = i / 260.0
            r = int(105 + t * 38)
            g = int(88 + t * 35)
            b = int(70 + t * 32)
            pygame.draw.line(bg_top, (r, g, b), (0, i), (SCENE_WIDTH, i))
        surface.blit(bg_top, (0, 0))

        bg_bot = pygame.Surface((SCENE_WIDTH, 340), pygame.SRCALPHA)
        for i in range(340):
            v = int(165 + ((i % 50) / 50) * 18)
            pygame.draw.line(bg_bot, (v - 5, v - 12, v - 20), (0, i), (SCENE_WIDTH, i))
        surface.blit(bg_bot, (0, 260))

        shelf_data = [(35, 70, 72, 210), (693, 70, 72, 210)]
        for sx, sy, sw, sh in shelf_data:
            wood_dark = (82, 54, 28)
            wood_light = (108, 74, 42)
            pygame.draw.rect(surface, wood_dark, (sx, sy, sw, sh))
            pygame.draw.rect(surface, wood_light, (sx + 2, sy + 2, sw - 4, 4))
            shelf_layers = 6
            for layer in range(shelf_layers):
                ly = sy + 12 + layer * (sh - 16) // shelf_layers
                pygame.draw.line(surface, wood_dark, (sx + 2, ly), (sx + sw - 2, ly), 2)
                book_start = sx + 6
                book_end = sx + sw - 6
                book_count = 8
                book_spacing = (book_end - book_start) // book_count
                for bk in range(book_count):
                    bxx = book_start + bk * book_spacing + random.randint(-1, 1)
                    bh_val = 18 + random.randint(0, 14)
                    colors = [(168, 42, 42), (42, 88, 168), (138, 118, 78),
                              (78, 128, 78), (148, 78, 128), (188, 158, 58)]
                    bc = random.choice(colors)
                    pygame.draw.rect(surface, bc, (bxx, ly + 3, book_spacing - 4, bh_val))

        table_rects = [(260, 300, 100, 55), (450, 310, 100, 55)]
        for tx, ty, tw, th in table_rects:
            table_top = (148, 108, 62)
            pygame.draw.ellipse(surface, table_top, (tx, ty, tw, th // 2))
            leg_color = (98, 72, 46)
            lw = 5
            pygame.draw.rect(surface, leg_color, (tx + 8, ty + th // 2, lw, th // 2 + 10))
            pygame.draw.rect(surface, leg_color, (tx + tw - 13, ty + th // 2, lw, th // 2 + 10))

        lamp_glow = pygame.Surface((SCENE_WIDTH, 200), pygame.SRCALPHA)
        for lx in [200, 400, 600]:
            for rad in range(60, 0, -2):
                a = max(0, 12 - rad // 5)
                pygame.draw.circle(lamp_glow, (255, 238, 180, a), (lx, 100), rad)
        surface.blit(lamp_glow, (0, 0))

        carpet_color = (132, 58, 48)
        pygame.draw.rect(surface, carpet_color, (180, 520, 440, 70))
        pygame.draw.rect(surface, (152, 78, 68), (180, 520, 440, 4))

        pillar_positions = [(180, 270), (618, 270)]
        for px_pos, py_pos in pillar_positions:
            p_color = (172, 158, 138)
            pygame.draw.rect(surface, p_color, (px_pos, py_pos, 18, 230))
            cap_color = (192, 182, 162)
            pygame.draw.rect(surface, cap_color, (px_pos - 4, py_pos, 26, 10))
            pygame.draw.rect(surface, cap_color, (px_pos - 4, py_pos + 222, 26, 10))

    def _draw_boya_detailed(self, surface, font):
        sky = pygame.Surface((SCENE_WIDTH, 240), pygame.SRCALPHA)
        for i in range(240):
            t = i / 240.0
            r = int(148 + t * 55)
            g = int(185 + t * 20)
            b = int(130 + t * 35)
            pygame.draw.line(sky, (r, g, b), (0, i), (SCENE_WIDTH, i))
        surface.blit(sky, (0, 0))

        grass_base = pygame.Surface((SCENE_WIDTH, 360), pygame.SRCALPHA)
        for i in range(360):
            stripe = (i // 25) % 2
            g1 = (72, 165, 72)
            g2 = (62, 152, 62)
            c = g1 if stripe == 0 else g2
            pygame.draw.line(grass_base, c, (0, i), (SCENE_WIDTH, i))
        surface.blit(grass_base, (0, 240))

        lawn_center = (SCENE_WIDTH // 2, 350)
        lawn_w, lawn_h = 420, 160
        for dy in range(lawn_h):
            shade = 1.0 - abs(dy - lawn_h // 2) / (lawn_h // 2) * 0.12
            gc = (int(68 * shade), int(158 * shade), int(62 * shade))
            pygame.draw.line(surface, gc,
                             (lawn_center[0] - lawn_w // 2, lawn_center[1] - lawn_h // 2 + dy),
                             (lawn_center[0] + lawn_w // 2, lawn_center[1] - lawn_h // 2 + dy))

        path_points = [(0, 480), (200, 430), (400, 440), (600, 420), (SCENE_WIDTH, 470)]
        for pi in range(len(path_points) - 1):
            p1 = path_points[pi]
            p2 = path_points[pi + 1]
            for offset in range(-25, 26):
                shade = 1.0 - abs(offset) / 28.0
                pc = (int(178 * shade), int(168 * shade), int(138 * shade))
                pygame.draw.line(surface, pc,
                                 (p1[0], p1[1] + offset), (p2[0], p2[1] + offset), 2)

        tree_spots = [(100, 260), (700, 250)]
        for ttx, tty in tree_spots:
            tc = (78, 58, 32)
            pygame.draw.rect(surface, tc, (ttx + 18, tty + 70, 14, 50))
            for lv in range(3):
                lcy = tty + 60 - lv * 25
                lcr = 38 - lv * 6
                lc = (48 + lv * 15, 125 - lv * 10, 42 + lv * 6)
                pygame.draw.ellipse(surface, lc, (ttx + 20 - lcr, lcy - lcr // 2, lcr * 2, lcr + 8))

        bench_positions = [(150, 395), (620, 390)]
        for bench_x, bench_y in bench_positions:
            seat_color = (138, 92, 48)
            pygame.draw.rect(surface, seat_color, (bench_x, bench_y, 64, 8))
            back_color = (122, 78, 38)
            pygame.draw.rect(surface, back_color, (bench_x, bench_y - 16, 64, 6))
            leg_c = (88, 62, 38)
            pygame.draw.rect(surface, leg_c, (bench_x + 4, bench_y + 8, 5, 18))
            pygame.draw.rect(surface, leg_c, (bench_x + 55, bench_y + 8, 5, 18))

        lamp_positions = [(380, 290)]
        for llx, lly in lamp_positions:
            pole_c = (68, 66, 74)
            pygame.draw.rect(surface, pole_c, (llx + 5, lly, 5, 65))
            head_c = (205, 188, 128)
            pygame.draw.ellipse(surface, head_c, (llx - 3, lly - 7, 26, 14))
            glow_s = pygame.Surface((34, 24), pygame.SRCALPHA)
            for ggx in range(34):
                for ggy in range(24):
                    d = ((ggx - 17) ** 2 + (ggy - 12) ** 2) ** 0.5
                    al = max(0, int(25 - d * 1.0))
                    if al > 0:
                        glow_s.set_at((ggx, ggy), (255, 240, 170, al))
            surface.blit(glow_s, (llx - 4, lly - 9))

        flower_spots = [(280, 370), (330, 385), (480, 365), (530, 380)]
        for ffx, ffy in flower_spots:
            fc = random.choice([(255, 120, 140), (255, 200, 80), (200, 140, 255)])
            fs = random.randint(3, 5)
            pygame.draw.circle(surface, fc, (ffx, ffy), fs)
            stem_c = (42, 118, 42)
            pygame.draw.line(surface, stem_c, (ffx, ffy), (ffx, ffy + 10), 1)

    def _draw_youming_detailed(self, surface, font):
        sky = pygame.Surface((SCENE_WIDTH, 260), pygame.SRCALPHA)
        for i in range(260):
            t = i / 260.0
            r = int(130 + t * 42)
            g = int(125 + t * 38)
            b = int(165 + t * 28)
            pygame.draw.line(sky, (r, g, b), (0, i), (SCENE_WIDTH, i))
        surface.blit(sky, (0, 0))

        field = pygame.Surface((SCENE_WIDTH, 340), pygame.SRCALPHA)
        for i in range(340):
            stripe = (i // 20) % 2
            f1 = (78, 158, 72)
            f2 = (68, 146, 62)
            c = f1 if stripe == 0 else f2
            pygame.draw.line(field, c, (0, i), (SCENE_WIDTH, i))
        surface.blit(field, (0, 260))

        track_outer = pygame.Rect(180, 340, 440, 80)
        track_inner = pygame.Rect(210, 355, 380, 50)
        pygame.draw.ellipse(surface, (185, 62, 52), track_outer)
        pygame.draw.ellipse(surface, (72, 148, 68), track_inner)
        for li in range(0, 440, 35):
            angle = li / 440.0 * 3.14159
            mx = 295 + int((440 // 2) * math.cos(angle))
            my = 380 + int(40 * math.sin(angle))
            pygame.draw.line(surface, (200, 75, 65), (mx, my), (mx + 15, my), 2)

        hoop_x, hoop_y = 90, 130
        pole_c = (72, 72, 82)
        pygame.draw.rect(surface, pole_c, (hoop_x + 14, hoop_y + 70, 8, 200))
        backboard_c = (218, 218, 228)
        pygame.draw.rect(surface, backboard_c, (hoop_x, hoop_y, 56, 75), border_radius=3)
        rim_c = (232, 148, 42)
        pygame.draw.ellipse(surface, rim_c, (hoop_x + 8, hoop_y + 75, 40, 10), 2)
        net_c = (232, 232, 232)
        for ni in range(8):
            ny = hoop_y + 83 + ni * 10
            nw = 36 - ni * 3
            if nw > 0:
                pygame.draw.line(surface, net_c, (hoop_x + 10 + (36 - nw) // 2, ny),
                                 (hoop_x + 10 + (36 - nw) // 2 + nw, ny), 1)

        goal_posts = [(620, 180), (720, 175)]
        for gpx, gpy in goal_posts:
            post_c = (192, 192, 192)
            pygame.draw.rect(surface, post_c, (gpx, gpy, 6, 120))
            cross_c = (192, 192, 192)
            pygame.draw.rect(surface, cross_c, (gpx - 25, gpy, 56, 6))

        bleacher_x = 500
        bleacher_y = 260
        for bi in range(5):
            seat_y = bleacher_y + bi * 14
            sc = (168 + bi * 12, 72 + bi * 8, 62 + bi * 6)
            pygame.draw.rect(surface, sc, (bleacher_x, seat_y, 180, 10), border_radius=2)

        score_text = font.render("YOU MING", True, (220, 220, 230))
        surface.blit(score_text, (340, 290))
        score_sub = font.render("GYMNASIUM", True, (180, 180, 195))
        surface.blit(score_sub, (352, 308))

    def _draw_dining_detailed(self, surface, font):
        wall = pygame.Surface((SCENE_WIDTH, 200), pygame.SRCALPHA)
        for i in range(200):
            t = i / 200.0
            r = int(208 + t * 18)
            g = int(178 + t * 15)
            b = int(138 + t * 12)
            pygame.draw.line(wall, (r, g, b), (0, i), (SCENE_WIDTH, i))
        surface.blit(wall, (0, 0))

        floor = pygame.Surface((SCENE_WIDTH, 400), pygame.SRCALPHA)
        for i in range(400):
            tile = (i // 35) % 2
            f1 = (195, 168, 138)
            f2 = (182, 156, 126)
            c = f1 if tile == 0 else f2
            pygame.draw.line(floor, c, (0, i), (SCENE_WIDTH, i))
        surface.blit(floor, (0, 200))

        counter_bg = (162, 138, 102)
        pygame.draw.rect(surface, counter_bg, (80, 80, 640, 55), border_radius=4)
        counter_top = (188, 162, 122)
        pygame.draw.rect(surface, counter_top, (80, 80, 640, 12), border_radius=4)

        steam_positions = [(150, 60), (300, 55), (450, 62), (580, 58)]
        for stx, sty in steam_positions:
            for si in range(3):
                sox = stx + random.randint(-8, 8)
                soy = sty - si * 12
                sa = 80 - si * 22
                ss = pygame.Surface((16, 20), pygame.SRCALPHA)
                pygame.draw.ellipse(ss, (255, 255, 255, sa), (0, 0, 16, 20))
                surface.blit(ss, (sox, soy))

        window_x, window_y = 650, 30
        pygame.draw.rect(surface, (180, 210, 240), (window_x, window_y, 100, 70), border_radius=3)
        pygame.draw.line(surface, (140, 170, 210), (window_x + 50, window_y),
                         (window_x + 50, window_y + 70), 2)
        pygame.draw.line(surface, (140, 170, 210), (window_x, window_y + 35),
                         (window_x + 100, window_y + 35), 2)

        menu_board_x, menu_board_y = 580, 170
        pygame.draw.rect(surface, (218, 195, 158), (menu_board_x, menu_board_y, 120, 80))
        pygame.draw.rect(surface, (178, 155, 118), (menu_board_x, menu_board_y, 120, 80), 2)
        mtext1 = font.render("今日菜单", True, (82, 58, 32))
        surface.blit(mtext1, (menu_board_x + 22, menu_board_y + 10))
        mtext2 = font.render("红烧肉 12元", True, (102, 72, 42))
        surface.blit(mtext2, (menu_board_x + 14, menu_board_y + 32))
        mtext3 = font.render("糖醋鱼 15元", True, (102, 72, 42))
        surface.blit(mtext3, (menu_board_x + 14, menu_board_y + 50))

        table_data = [
            (120, 320, 76, 42),
            (320, 340, 76, 42),
            (520, 325, 76, 42),
        ]
        for tbx, tby, tbw, tbh in table_data:
            top_c = (162, 132, 92)
            pygame.draw.ellipse(surface, top_c, (tbx, tby, tbw, tbh // 2))
            leg_c = (112, 86, 56)
            pygame.draw.rect(surface, leg_c, (tbx + 6, tby + tbh // 2, 5, tbh // 2 + 8))
            pygame.draw.rect(surface, leg_c, (tbx + tbw - 11, tby + tbh // 2, 5, tbh // 2 + 8))

        chair_positions = [(110, 360), (180, 365), (310, 380), (390, 378),
                           (510, 365), (590, 368)]
        for chx, chy in chair_positions:
            ch_c = (148, 82, 58)
            pygame.draw.rect(surface, ch_c, (chx, chy, 22, 24), border_radius=3)
            back_c = (132, 68, 48)
            pygame.draw.rect(surface, back_c, (chx, chy - 14, 22, 14), border_radius=2)

        trash_x, trash_y = 700, 420
        pygame.draw.rect(surface, (72, 118, 72), (trash_x, trash_y, 28, 38), border_radius=3)
        pygame.draw.rect(surface, (58, 98, 58), (trash_x, trash_y, 28, 8), border_radius=2)

    def _draw_fountain_detailed(self, surface, font):
        sky = pygame.Surface((SCENE_WIDTH, 250), pygame.SRCALPHA)
        for i in range(250):
            t = i / 250.0
            r = int(115 + t * 42)
            g = int(155 + t * 38)
            b = int(200 + t * 22)
            pygame.draw.line(sky, (r, g, b), (0, i), (SCENE_WIDTH, i))
        surface.blit(sky, (0, 0))

        plaza = pygame.Surface((SCENE_WIDTH, 350), pygame.SRCALPHA)
        for i in range(350):
            ring = (i // 40) % 2
            p1 = (175, 195, 165)
            p2 = (162, 182, 152)
            c = p1 if ring == 0 else p2
            pygame.draw.line(plaza, c, (0, i), (SCENE_WIDTH, i))
        surface.blit(plaza, (0, 250))

        pool_x, pool_y, pool_w, pool_h = 260, 160, 280, 140
        pool_shadow = pygame.Surface((pool_w + 20, 20), pygame.SRCALPHA)
        pool_shadow.fill((0, 0, 0, 35))
        surface.blit(pool_shadow, (pool_x - 10, pool_y + pool_h + 5))

        water_deep = (55, 125, 185)
        pygame.draw.ellipse(surface, water_deep, (pool_x, pool_y, pool_w, pool_h))
        water_mid = (78, 152, 210)
        pygame.draw.ellipse(surface, water_mid, (pool_x + 15, pool_y + 15, pool_w - 30, pool_h - 25))
        water_light = (110, 180, 235)
        pygame.draw.ellipse(surface, water_light, (pool_x + 35, pool_y + 30, pool_w - 70, pool_h - 50))

        center_x = pool_x + pool_w // 2
        center_y = pool_y + pool_h // 2 - 10
        base_c = (138, 138, 148)
        pygame.draw.polygon(surface, base_c, [
            (center_x, center_y - 50),
            (center_x - 35, center_y + 20),
            (center_x + 35, center_y + 20),
        ])
        tier_c = (158, 158, 168)
        pygame.draw.polygon(surface, tier_c, [
            (center_x, center_y - 65),
            (center_x - 25, center_y - 5),
            (center_x + 25, center_y - 5),
        ])
        top_c = (178, 178, 188)
        pygame.draw.circle(surface, top_c, (center_x, center_y - 72), 12)

        spray_angles = [-60, -30, 0, 30, 60]
        for ang in spray_angles:
            rad = math.radians(ang)
            for step in range(8):
                sx = center_x + int(math.cos(rad) * step * 5)
                sy = center_y - 78 - int(math.sin(rad) * step * 5) - step * 3
                sp_size = max(1, 4 - step // 2)
                sp_alpha = 180 - step * 18
                sp_s = pygame.Surface((sp_size * 2, sp_size * 2), pygame.SRCALPHA)
                pygame.draw.circle(sp_s, (200, 228, 255, sp_alpha),
                                   (sp_size, sp_size), sp_size)
                surface.blit(sp_s, (sx - sp_size, sy - sp_size))

        ripple_data = [(center_x - 40, center_y + 30), (center_x + 35, center_y + 25),
                        (center_x - 15, center_y + 45), (center_x + 20, center_y + 40)]
        for rx, ry in ripple_data:
            rr = random.randint(12, 22)
            rc = (140, 190, 235)
            pygame.draw.ellipse(surface, rc, (rx - rr, ry - rr // 2, rr * 2, rr), 1)

        monument_x, monument_y = 100, 280
        mono_base = (145, 140, 132)
        pygame.draw.rect(surface, mono_base, (monument_x, monument_y, 50, 120))
        mono_top = (162, 158, 148)
        pygame.draw.polygon(surface, mono_top, [
            (monument_x - 8, monument_y),
            (monument_x + 58, monument_y),
            (monument_x + 25, monument_y - 30),
        ])
        mono_text = font.render("校训碑", True, (72, 62, 52))
        surface.blit(mono_text, (monument_x + 4, monument_y + 50))

        bush_positions = [(50, 480), (180, 495), (600, 485), (730, 490)]
        for bush_x, bush_y in bush_positions:
            bush_c = (52, 118, 52)
            pygame.draw.ellipse(surface, bush_c, (bush_x, bush_y, 45, 28))
            bush_h = (42, 105, 42)
            pygame.draw.ellipse(surface, bush_h, (bush_x + 5, bush_y - 8, 35, 22))

        flower_bed = pygame.Rect(300, 500, 200, 60)
        bed_border = (118, 85, 52)
        pygame.draw.ellipse(surface, bed_border, flower_bed)
        bed_fill = (72, 128, 58)
        pygame.draw.ellipse(surface, bed_fill,
                            (flower_bed.x + 5, flower_bed.y + 5, flower_bed.width - 10, flower_bed.height - 10))
        for fi in range(12):
            fx = flower_bed.x + 15 + fi * 15
            fy = flower_bed.y + 15 + random.randint(-5, 5)
            fc = random.choice([(255, 100, 120), (255, 180, 60), (255, 220, 80), (220, 120, 200)])
            pygame.draw.circle(surface, fc, (fx, fy), 4)

    def _draw_night_detailed(self, surface, font):
        night_bg = pygame.Surface((SCENE_WIDTH, SCENE_HEIGHT), pygame.SRCALPHA)
        for y in range(SCENE_HEIGHT):
            t = y / SCENE_HEIGHT
            r = int(8 + t * 18)
            g = int(4 + t * 12)
            b = int(28 + t * 25)
            pygame.draw.line(night_bg, (r, g, b), (0, y), (SCENE_WIDTH, y))
        surface.blit(night_bg, (0, 0))

        moon_x, moon_y = 640, 55
        moon_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
        for mr in range(60, 0, -2):
            ma = max(0, 18 - mr // 4)
            pygame.draw.circle(moon_glow, (240, 235, 180, ma), (60, 60), mr)
        surface.blit(moon_glow, (moon_x - 60, moon_y - 60))
        pygame.draw.circle(surface, (245, 242, 200), (moon_x, moon_y), 38)
        pygame.draw.circle(surface, (30, 18, 50), (moon_x + 12, moon_y - 8), 32)

        if not hasattr(self, '_night_stars'):
            self._night_stars = []
            for _ in range(50):
                sx = random.randint(10, SCENE_WIDTH - 10)
                sy = random.randint(5, 200)
                ssize = random.choice([1, 1, 1, 2])
                sbright = random.randint(180, 255)
                self._night_stars.append((sx, sy, ssize, sbright))
        for sx, sy, ssize, sbright in self._night_stars:
            twinkle = int(abs(random.random() * 55))
            star_c = (min(255, sbright + twinkle), min(255, sbright + twinkle), min(255, 240 + twinkle // 2))
            pygame.draw.circle(surface, star_c, (sx, sy), ssize)

        ground_night = pygame.Surface((SCENE_WIDTH, 400), pygame.SRCALPHA)
        for i in range(400):
            gt = i / 400.0
            gr = int(18 + gt * 22)
            gg = int(28 + gt * 18)
            gb = int(15 + gt * 12)
            pygame.draw.line(ground_night, (gr, gg, gb), (0, i), (SCENE_WIDTH, i))
        surface.blit(ground_night, (0, 200))

        path_night = pygame.Rect(200, 450, 400, 130)
        pygame.draw.ellipse(surface, (38, 32, 48), path_night)
        for pi in range(0, 400, 50):
            px = path_night.x + pi
            pygame.draw.circle(surface, (48, 42, 58), (px, path_night.centery), 3)

        night_tree_data = [(70, 140), (700, 130)]
        for ntx, nty in night_tree_data:
            nt_trunk = (28, 22, 18)
            pygame.draw.rect(surface, nt_trunk, (ntx + 20, nty + 80, 14, 55))
            for nlv in range(3):
                ncy = nty + 70 - nlv * 25
                ncr = 36 - nlv * 6
                nc = (18 + nlv * 8, 35 + nlv * 10, 22 + nlv * 5)
                pygame.draw.ellipse(surface, nc, (ntx + 21 - ncr, ncy - ncr // 2, ncr * 2, ncr + 8))

        platform_x, platform_y = 300, 220
        plat_w, plat_h = 200, 100
        plat_shadow = pygame.Surface((plat_w + 16, 16), pygame.SRCALPHA)
        plat_shadow.fill((0, 0, 0, 50))
        surface.blit(plat_shadow, (platform_x - 8, platform_y + plat_h + 8))
        plat_base = (48, 38, 68)
        pygame.draw.rect(surface, plat_base, (platform_x, platform_y, plat_w, plat_h), border_radius=8)
        plat_rim = (88, 72, 128)
        pygame.draw.rect(surface, plat_rim, (platform_x, platform_y, plat_w, plat_h), 3, border_radius=8)
        plat_inner = (35, 28, 52)
        pygame.draw.rect(surface, plat_inner, (platform_x + 8, platform_y + 8, plat_w - 16, plat_h - 16), border_radius=4)
        glow_core = pygame.Surface((plat_w - 24, plat_h - 24), pygame.SRCALPHA)
        for gx in range(plat_w - 24):
            for gy in range(plat_h - 24):
                cx = (plat_w - 24) // 2
                cy = (plat_h - 24) // 2
                dist = ((gx - cx) ** 2 + (gy - cy) ** 2) ** 0.5
                ga = max(0, int(35 - dist * 0.4))
                if ga > 0:
                    glow_core.set_at((gx, gy), (180, 150, 255, ga))
        surface.blit(glow_core, (platform_x + 12, platform_y + 12))

        firefly_positions = [(150, 350), (250, 420), (500, 380), (600, 440), (350, 480)]
        for ffx, ffy in firefly_positions:
            ff_glow = pygame.Surface((20, 20), pygame.SRCALPHA)
            for fr in range(10, 0, -2):
                fa = 25 - fr * 2
                pygame.draw.circle(ff_glow, (180, 255, 120, fa), (10, 10), fr)
            surface.blit(ff_glow, (ffx - 10, ffy - 10))
            pygame.draw.circle(surface, (220, 255, 160), (ffx, ffy), 2)

        secret_text = font.render("SECRET REALM", True, (160, 140, 220))
        surface.blit(secret_text, (platform_x + 42, platform_y + plat_h + 20))

    def _draw_particles(self, surface):
        for p in self.particles:
            alpha = max(0, min(255, int(p["life"] * 400)))
            color = tuple(min(255, c) for c in p["color"])
            pygame.draw.circle(surface, color, (int(p["x"]), int(p["y"])), 3)

    def _draw_scene_label(self, surface, font):
        name_surf = font.render(self.name, True, (255, 255, 255))
        bg_rect = pygame.Rect(10, 10, name_surf.get_width() + 20, name_surf.get_height() + 10)
        s = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 140))
        surface.blit(s, bg_rect.topleft)
        surface.blit(name_surf, (20, 15))

    def get_puzzle_object(self):
        for obj in self.objects:
            if obj.obj_type == "puzzle":
                return obj
        return None

    def get_item_objects(self):
        return [obj for obj in self.objects if obj.obj_type == "item" and not obj.interacted]

    def reset_items(self):
        for obj in self.objects:
            if obj.obj_type == "item":
                obj.interacted = False
