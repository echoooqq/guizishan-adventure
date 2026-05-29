import pygame
import math
import random

TILE_SIZE = 40
MAP_WIDTH = 2400
MAP_HEIGHT = 1800
COLS = MAP_WIDTH // TILE_SIZE
ROWS = MAP_HEIGHT // TILE_SIZE

NANHU_MAP_WIDTH = 800
NANHU_MAP_HEIGHT = 600


class CollisionMap:
    def __init__(self, width, height, tile_size):
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.cols = width // tile_size
        self.rows = height // tile_size
        self.grid = [[0] * self.cols for _ in range(self.rows)]

    def set_tile(self, col, row, value=1):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.grid[row][col] = value

    def set_rect(self, x, y, w, h, value=1):
        start_col = max(0, x // self.tile_size)
        start_row = max(0, y // self.tile_size)
        end_col = min(self.cols, (x + w) // self.tile_size + 1)
        end_row = min(self.rows, (y + h) // self.tile_size + 1)
        for r in range(start_row, end_row):
            for c in range(start_col, end_col):
                self.grid[r][c] = value

    def collides(self, rect):
        start_col = max(0, rect.left // self.tile_size)
        start_row = max(0, rect.top // self.tile_size)
        end_col = min(self.cols, rect.right // self.tile_size + 1)
        end_row = min(self.rows, rect.bottom // self.tile_size + 1)
        for r in range(start_row, end_row):
            for c in range(start_col, end_col):
                if self.grid[r][c] == 1:
                    return True
        return False

    def is_solid(self, col, row):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.grid[row][col] == 1
        return True

    def draw_debug(self, surface, camera_x=0, camera_y=0):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == 1:
                    x = c * TILE_SIZE - camera_x
                    y = r * TILE_SIZE - camera_y
                    if -TILE_SIZE < x < surface.get_width() + TILE_SIZE and \
                       -TILE_SIZE < y < surface.get_height() + TILE_SIZE:
                        s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                        s.fill((255, 0, 0, 40))
                        surface.blit(s, (x, y))


class WorldObject:
    def __init__(self, name, x, y, w, h, obj_type="decoration",
                 description="", item_id=None, color=(200, 200, 200),
                 interaction_range=35):
        self.name = name
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.obj_type = obj_type
        self.description = description
        self.item_id = item_id
        self.color = color
        self.interacted = False
        self.visible = True
        self.glow_timer = 0
        self.interaction_range = interaction_range
        self.triggered_dialog = False

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    @property
    def center(self):
        return (self.x + self.w // 2, self.y + self.h // 2)

    def update(self, dt):
        self.glow_timer += dt

    def distance_to(self, px, py):
        cx, cy = self.center
        return math.sqrt((px - cx) ** 2 + (py - cy) ** 2)

    def is_in_range(self, px, py):
        return self.distance_to(px, py) < self.interaction_range

    def draw(self, surface, camera_x=0, camera_y=0):
        if not self.visible:
            return
        sx = self.x - camera_x
        sy = self.y - camera_y
        if sx + self.w < 0 or sx > surface.get_width() or \
           sy + self.h < 0 or sy > surface.get_height():
            return

        glow = int(abs(math.cos(self.glow_timer * 120).real * 40)
                   if self.obj_type in ("item", "puzzle", "portal") else 0)
        color = tuple(min(255, c + glow) for c in self.color)
        pygame.draw.rect(surface, color, (int(sx), int(sy), self.w, self.h))
        pygame.draw.rect(surface, (255, 255, 255), (int(sx), int(sy), self.w, self.h), 2)

        if self.obj_type == "item" and not self.interacted:
            star_y = sy + self.h // 2 + int(abs(math.sin(self.glow_timer * 180)) * 5)
            pygame.draw.circle(surface, (255, 255, 100),
                               (int(sx + self.w // 2), int(star_y)), 4)

        if self.obj_type == "portal":
            pulse = abs(math.sin(self.glow_timer * 3))
            ring_r = int(20 + pulse * 10)
            ring_surf = pygame.Surface((ring_r * 2, ring_r * 2), pygame.SRCALPHA)
            alpha = int(80 + pulse * 60)
            pygame.draw.circle(ring_surf, (100, 180, 255, alpha),
                               (ring_r, ring_r), ring_r, 2)
            surface.blit(ring_surf,
                         (int(sx + self.w // 2 - ring_r),
                          int(sy + self.h // 2 - ring_r)))

    def check_click(self, pos, camera_x=0, camera_y=0):
        world_pos = (pos[0] + camera_x, pos[1] + camera_y)
        return self.rect.collidepoint(world_pos)


class Area:
    def __init__(self, area_id, name, bounds, color_hint=(100, 150, 100)):
        self.area_id = area_id
        self.name = name
        self.bounds = bounds
        self.color_hint = color_hint
        self.puzzle_solved = False
        self.unlocked = True

    def contains(self, x, y):
        return self.bounds.collidepoint(x, y)


class MainWorld:
    def __init__(self):
        self.width = MAP_WIDTH
        self.height = MAP_HEIGHT
        self.collision = CollisionMap(MAP_WIDTH, MAP_HEIGHT, TILE_SIZE)
        self.objects = []
        self.areas = {}
        self.current_area_id = "guizhong_road"
        self.particles = []
        self.portal_pos = None
        self._build_areas()
        self._build_collision()
        self._build_objects()

    def _build_areas(self):
        self.areas["guizhong_road"] = Area(
            "guizhong_road", "桂中路",
            pygame.Rect(50, 700, 900, 500), (140, 180, 120))
        self.areas["library"] = Area(
            "library", "校图书馆",
            pygame.Rect(1050, 50, 650, 550), (130, 110, 90))
        self.areas["boya_square"] = Area(
            "boya_square", "博雅广场",
            pygame.Rect(1050, 680, 700, 480), (130, 175, 110))
        self.areas["youming_gym"] = Area(
            "youming_gym", "佑铭体育馆",
            pygame.Rect(50, 1250, 750, 450), (145, 135, 165))
        self.areas["dining_hall"] = Area(
            "dining_hall", "学子食堂",
            pygame.Rect(950, 1180, 600, 500), (190, 165, 130))
        self.areas["fountain_square"] = Area(
            "fountain_square", "喷泉广场",
            pygame.Rect(1700, 700, 600, 550), (130, 175, 210))
        self.areas["night_secret"] = Area(
            "night_secret", "桂子山夜景秘境",
            pygame.Rect(1600, 1300, 700, 400), (60, 40, 90))

    def _build_collision(self):
        self.collision.set_rect(0, 0, MAP_WIDTH, 30, 1)
        self.collision.set_rect(0, MAP_HEIGHT - 30, MAP_WIDTH, 30, 1)
        self.collision.set_rect(0, 0, 30, MAP_HEIGHT, 1)
        self.collision.set_rect(MAP_WIDTH - 30, 0, 30, MAP_HEIGHT, 1)

        self.collision.set_rect(80, 760, 280, 25, 1)
        self.collision.set_rect(440, 760, 200, 25, 1)
        self.collision.set_rect(720, 760, 200, 25, 1)
        self.collision.set_rect(60, 80, 22, 130, 1)
        self.collision.set_rect(668, 60, 22, 130, 1)
        self.collision.set_rect(1070, 70, 28, 230, 1)
        self.collision.set_rect(1692, 70, 28, 230, 1)
        self.collision.set_rect(55, 280, 18, 55, 1)
        self.collision.set_rect(685, 280, 18, 55, 1)
        self.collision.set_rect(1080, 300, 60, 205, 1)
        self.collision.set_rect(1680, 300, 60, 205, 1)
        self.collision.set_rect(148, 395, 72, 8, 1)
        self.collision.set_rect(498, 395, 72, 8, 1)
        self.collision.set_rect(618, 380, 72, 8, 1)
        self.collision.set_rect(95, 1280, 24, 195, 1)
        self.collision.set_rect(695, 1275, 24, 200, 1)
        self.collision.set_rect(317, 1325, 78, 42, 1)
        self.collision.set_rect(537, 1325, 78, 42, 1)
        self.collision.set_rect(967, 1330, 76, 38, 1)
        self.collision.set_rect(109, 1365, 22, 26, 1)
        self.collision.set_rect(179, 1365, 22, 26, 1)
        self.collision.set_rect(309, 1370, 22, 21, 1)
        self.collision.set_rect(389, 1370, 22, 21, 1)
        self.collision.set_rect(85, 1410, 260, 15, 1)
        self.collision.set_rect(1065, 190, 28, 115, 1)
        self.collision.set_rect(1675, 190, 28, 115, 1)
        self.collision.set_rect(1720, 340, 56, 82, 1)
        self.collision.set_rect(88, 410, 16, 52, 1)
        self.collision.set_rect(692, 410, 16, 52, 1)
        self.collision.set_rect(1715, 850, 45, 250, 1)
        self.collision.set_rect(2155, 850, 45, 250, 1)
        self.collision.set_rect(1740, 1120, 220, 20, 1)
        self.collision.set_rect(1650, 1340, 40, 40, 1)
        self.collision.set_rect(1900, 1340, 40, 40, 1)
        self.collision.set_rect(1720, 1440, 100, 20, 1)

    def _build_objects(self):
        guizhong = self.areas["guizhong_road"]
        gx, gy = guizhong.bounds.x, guizhong.bounds.y
        self.objects.append(WorldObject("桂花树", gx + 100, gy + 150, 80, 120,
                                        "decoration", "金桂飘香，桂子山因此得名",
                                        color=(100, 160, 60)))
        self.objects.append(WorldObject("桂花树", gx + 750, gy + 150, 80, 130,
                                        "decoration", "银桂如雪，清香四溢",
                                        color=(100, 160, 60)))
        self.objects.append(WorldObject("桂花徽章", gx + 200, gy + 250, 30, 30,
                                        "item", "一枚闪着金光的桂花徽章",
                                        "osmanthus_badge", (255, 200, 50)))
        self.objects.append(WorldObject("桂花徽章", gx + 400, gy + 150, 30, 30,
                                        "item", "一枚闪着金光的桂花徽章",
                                        "osmanthus_badge", (255, 200, 50)))
        self.objects.append(WorldObject("桂花徽章", gx + 600, gy + 350, 30, 30,
                                        "item", "一枚闪着金光的桂花徽章",
                                        "osmanthus_badge", (255, 200, 50)))
        self.objects.append(WorldObject("石碑", gx + 350, gy + 120, 60, 80,
                                        "puzzle", "桂中路石碑：收集3枚桂花徽章可开启秘境",
                                        color=(160, 160, 160)))
        self.objects.append(WorldObject("长椅", gx + 500, gy + 330, 70, 30,
                                        "decoration", "一张安静的长椅，适合读书",
                                        color=(139, 90, 43)))

        lib = self.areas["library"]
        lx, ly = lib.bounds.x, lib.bounds.y
        self.objects.append(WorldObject("书架", lx + 120, ly + 80, 60, 180,
                                       "decoration", "满满的书架，知识的海洋",
                                       color=(120, 80, 40)))
        self.objects.append(WorldObject("书架", lx + 400, ly + 80, 60, 180,
                                       "decoration", "满满的书架，书香四溢",
                                       color=(120, 80, 40)))
        self.objects.append(WorldObject("阅读台", lx + 250, ly + 150, 80, 50,
                                       "puzzle", "阅读台上放着一道文学题目……接近答题",
                                       color=(160, 120, 60)))
        self.objects.append(WorldObject("读书书签", lx + 450, ly + 250, 30, 30,
                                       "item", "一枚精美的读书书签，可以解锁题库提示",
                                       "bookmark", (180, 100, 200)))

        boya = self.areas["boya_square"]
        bx, by = boya.bounds.x, boya.bounds.y
        self.objects.append(WorldObject("博雅石碑", bx + 310, by + 50, 80, 60,
                                       "puzzle", "博雅石碑上刻着古老的文字……接近答题",
                                       color=(180, 180, 180)))
        self.objects.append(WorldObject("桂花徽章", bx + 200, by + 200, 30, 30,
                                       "item", "草坪上闪着微光的桂花徽章",
                                       "osmanthus_badge", (255, 200, 50)))

        youming = self.areas["youming_gym"]
        yx, yy = youming.bounds.x, youming.bounds.y
        self.objects.append(WorldObject("体育知识板", yx + 350, yy + 50, 80, 60,
                                       "puzzle", "体育知识问答板……接近答题",
                                       color=(180, 160, 200)))
        self.objects.append(WorldObject("校园钥匙", yx + 450, yy + 200, 30, 30,
                                       "item", "跑道边遗落的校园钥匙",
                                       "campus_key", (220, 200, 50)))

        dining = self.areas["dining_hall"]
        dx, dy = dining.bounds.x, dining.bounds.y
        self.objects.append(WorldObject("隐藏饭卡", dx + 450, dy + 300, 30, 30,
                                       "item", "角落里一张神秘的食堂饭卡",
                                       "meal_card", (255, 150, 50)))

        fountain = self.areas["fountain_square"]
        fx, fy = fountain.bounds.x, fountain.bounds.y
        self.objects.append(WorldObject("校训碑", fx + 200, fy + 250, 70, 80,
                                       "puzzle", "校训碑上刻着华师的校训……接近答题",
                                       color=(160, 160, 160)))
        self.objects.append(WorldObject("桂花徽章", fx + 350, fy + 250, 30, 30,
                                       "item", "喷泉边闪光的桂花徽章",
                                       "osmanthus_badge", (255, 200, 50)))
        self.objects.append(WorldObject("南湖传送门", fx + 520, fy + 420, 60, 80,
                                       "portal", "通往南湖综合楼的传送门，点击或按E进入",
                                       color=(80, 120, 200)))
        self.portal_pos = (fx + 520 + 30, fy + 420 + 40)

        night = self.areas["night_secret"]
        nx, ny = night.bounds.x, night.bounds.y
        self.objects.append(WorldObject("月光台", nx + 150, ny + 80, 150, 80,
                                       "puzzle", "月光照耀的石台，上面刻着桂子山的秘密……",
                                       color=(60, 50, 100)))
        self.objects.append(WorldObject("宝箱", nx + 320, ny + 270, 50, 40,
                                       "item", "最终秘境宝箱！内含终极宝藏",
                                       "treasure_chest", (255, 215, 0)))

    def get_area_at(self, x, y):
        for aid, area in self.areas.items():
            if area.contains(x, y):
                return area
        return None

    def update(self, dt):
        for obj in self.objects:
            obj.update(dt)
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

    def draw(self, surface, font_small, camera_x=0, camera_y=0):
        self._draw_background(surface, camera_x, camera_y)
        self._draw_details(surface, font_small, camera_x, camera_y)
        for obj in self.objects:
            obj.draw(surface, camera_x, camera_y)
        self._draw_particles(surface, camera_x, camera_y)

    def _draw_background(self, surface, cx, cy):
        bg = pygame.Surface((MAP_WIDTH, MAP_HEIGHT))

        for y in range(MAP_HEIGHT):
            t = y / MAP_HEIGHT
            base_g = int(155 + t * 15)
            stripe = (y // 50) % 2
            g1 = (base_g + 12, base_g + 5, base_g - 8)
            g2 = (base_g + 5, base_g - 2, base_g - 15)
            c = g1 if stripe == 0 else g2
            pygame.draw.line(bg, c, (0, y), (MAP_WIDTH, y))

        for area in self.areas.values():
            hint_surf = pygame.Surface((area.bounds.width, area.bounds.height), pygame.SRCALPHA)
            r, g, b = area.color_hint
            for dy in range(area.bounds.height):
                factor = 1.0 - abs(dy - area.bounds.height // 2) / (area.bounds.height // 2) * 0.06
                hc = (int(r * factor), int(g * factor), int(b * factor))
                pygame.draw.line(hint_surf, hc, (0, dy), (area.bounds.width, dy))
            bg.blit(hint_surf, (area.bounds.x, area.bounds.y))

        path_points = [(400, 950), (700, 900), (1100, 950), (1500, 900),
                       (1850, 980), (1700, 1150), (1200, 1200), (800, 1150)]
        for pi in range(len(path_points) - 1):
            p1 = path_points[pi]
            p2 = path_points[pi + 1]
            for offset in range(-30, 31):
                shade = 1.0 - abs(offset) / 32.0
                pc = (int(175 * shade), int(165 * shade), int(138 * shade))
                pygame.draw.line(bg, pc,
                                 (p1[0], p1[1] + offset), (p2[0], p2[1] + offset), 3)

        lib_path = [(1100, 950), (1100, 700), (1300, 600)]
        for pi in range(len(lib_path) - 1):
            p1 = lib_path[pi]
            p2 = lib_path[pi + 1]
            for offset in range(-20, 21):
                shade = 1.0 - abs(offset) / 22.0
                pc = (int(165 * shade), int(155 * shade), int(128 * shade))
                pygame.draw.line(bg, pc,
                                 (p1[0], p1[1] + offset), (p2[0], p2[1] + offset), 2)

        surface.blit(bg, (-int(cx), -int(cy)))

    def _draw_details(self, surface, font, cx, cy):
        tree_data = [
            (130, 780), (780, 760),
            (1130, 100), (1730, 80),
            (1110, 750), (80, 1310), (720, 1300),
        ]
        for tx, ty in tree_data:
            sx = tx - cx
            sy = ty - cy
            if -60 < sx < surface.get_width() + 60 and -160 < sy < surface.get_height() + 160:
                trunk_color = (90, 65, 35)
                pygame.draw.rect(surface, trunk_color, (sx + 22, ty + 90 - cy, 16, 55))
                for layer in range(3):
                    lcy = ty + 75 - layer * 28 - cy
                    lcr = 42 - layer * 7
                    lc = (70 + layer * 18, 145 - layer * 12, 50 + layer * 8)
                    pygame.draw.ellipse(surface, lc,
                                       (tx + 24 - lcr - cx, lcy, lcr * 2, lcr + 10))

        lamp_positions = [(500, 880), (900, 860), (1350, 900), (1800, 920)]
        for llx, lly in lamp_positions:
            sx = llx - cx
            sy = lly - cy
            if -20 < sx < surface.get_width() + 20 and -20 < sy < surface.get_height() + 20:
                pole_color = (70, 70, 78)
                pygame.draw.rect(surface, pole_color, (sx + 4, sy, 6, 72))
                head_color = (210, 190, 130)
                pygame.draw.ellipse(surface, head_color, (sx - 2, sy - 8, 24, 16))

        building_data = [
            (1080, 100, 580, 200, (95, 112, 148)),
            (1680, 100, 580, 200, (95, 112, 148)),
            (980, 1220, 540, 200, (162, 138, 102)),
            (1740, 880, 360, 280, (75, 88, 118)),
        ]
        for bld_x, bld_y, bw, bh, bcolor in building_data:
            sx = bld_x - cx
            sy = bld_y - cy
            if -bw < sx < surface.get_width() + bw and -bh < sy < surface.get_height() + bh:
                shadow = pygame.Surface((bw + 14, 18), pygame.SRCALPHA)
                shadow.fill((0, 0, 0, 35))
                surface.blit(shadow, (sx - 7, sy + bh + 5))
                pygame.draw.rect(surface, bcolor, (sx, sy, bw, bh))
                accent = tuple(min(255, c + 35) for c in bcolor)
                pygame.draw.line(surface, accent, (sx, sy + bh - 6), (sx + bw, sy + bh - 6), 2)

        if self.portal_pos:
            px = self.portal_pos[0] - cx
            py = self.portal_pos[1] - cy
            if -40 < px < surface.get_width() + 40 and -40 < py < surface.get_height() + 40:
                pulse = abs(math.sin(pygame.time.get_ticks() * 0.003))
                for r in range(35, 5, -5):
                    alpha = int((1 - r / 35) * (60 + pulse * 40))
                    s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                    pygame.draw.circle(s, (100, 180, 255, alpha), (r, r), r)
                    surface.blit(s, (int(px - r), int(py - r)))

    def _draw_particles(self, surface, cx, cy):
        for p in self.particles:
            sx = p["x"] - cx
            sy = p["y"] - cy
            if 0 < sx < surface.get_width() and 0 < sy < surface.get_height():
                pygame.draw.circle(surface, p["color"], (int(sx), int(sy)), 3)

    def get_nearby_objects(self, px, py, max_dist=50):
        nearby = []
        for obj in self.objects:
            if obj.visible and obj.distance_to(px, py) < max_dist:
                nearby.append(obj)
        return sorted(nearby, key=lambda o: o.distance_to(px, py))

    def get_puzzle_object_for_area(self, area_id):
        area = self.areas.get(area_id)
        if not area or area.puzzle_solved:
            return None
        for obj in self.objects:
            if obj.obj_type == "puzzle" and area.contains(obj.center[0], obj.center[1]):
                return obj
        return None

    def reset_items(self):
        for obj in self.objects:
            if obj.obj_type == "item":
                obj.interacted = False

    def save_state(self):
        state = {
            "unlocked_areas": [aid for aid, a in self.areas.items() if a.unlocked],
            "solved_areas": [aid for aid, a in self.areas.items() if a.puzzle_solved],
            "interacted_objects": [],
        }
        for obj in self.objects:
            if obj.interacted:
                state["interacted_objects"].append(obj.name)
        return state

    def load_state(self, state):
        for aid in state.get("unlocked_areas", []):
            if aid in self.areas:
                self.areas[aid].unlocked = True
        for aid in state.get("solved_areas", []):
            if aid in self.areas:
                self.areas[aid].puzzle_solved = True
        interacted = state.get("interacted_objects", [])
        for obj in self.objects:
            if obj.name in interacted:
                obj.interacted = True


class NanhuWorld:
    def __init__(self):
        self.width = NANHU_MAP_WIDTH
        self.height = NANHU_MAP_HEIGHT
        self.collision = CollisionMap(NANHU_MAP_WIDTH, NANHU_MAP_HEIGHT, TILE_SIZE)
        self.objects = []
        self.return_portal = None
        self._build_collision()
        self._build_objects()

    def _build_collision(self):
        self.collision.set_rect(0, 0, NANHU_MAP_WIDTH, 25, 1)
        self.collision.set_rect(0, NANHU_MAP_HEIGHT - 25, NANHU_MAP_WIDTH, 25, 1)
        self.collision.set_rect(0, 0, 25, NANHU_MAP_HEIGHT, 1)
        self.collision.set_rect(NANHU_MAP_WIDTH - 25, 0, 25, NANHU_MAP_HEIGHT, 1)
        self.collision.set_rect(200, 80, 400, 250, 1)

    def _build_objects(self):
        self.objects.append(WorldObject("南湖综合楼主楼", 200, 80, 400, 250,
                                       "decoration", "南湖综合楼，计算机学院所在地",
                                       color=(95, 112, 148)))
        self.objects.append(WorldObject("校史展板", 80, 320, 80, 60,
                                       "puzzle", "展板上写着华师建校的历史……接近答题",
                                       color=(200, 180, 140)))
        self.objects.append(WorldObject("校园钥匙", 550, 370, 30, 30,
                                       "item", "一把闪亮的校园钥匙",
                                       "campus_key", (220, 200, 50)))
        self.objects.append(WorldObject("返回传送门", 350, 500, 60, 80,
                                       "portal", "返回本部校园的传送门",
                                       color=(200, 120, 80)))
        self.return_portal = (380, 540)

    def update(self, dt):
        for obj in self.objects:
            obj.update(dt)

    def draw(self, surface, font_small):
        bg = pygame.Surface((NANHU_MAP_WIDTH, NANHU_MAP_HEIGHT))
        for i in range(NANHU_MAP_HEIGHT):
            t = i / NANHU_MAP_HEIGHT
            r = int(115 + t * 50)
            g = int(140 + t * 45)
            b = int(185 + t * 25)
            pygame.draw.line(bg, (r, g, b), (0, i), (NANHU_MAP_WIDTH, i))
        surface.blit(bg, (0, 0))

        ground = pygame.Surface((NANHU_MAP_WIDTH, NANHU_MAP_HEIGHT - 280), pygame.SRCALPHA)
        for i in range(NANHU_MAP_HEIGHT - 280):
            v = int(175 + ((i % 40) / 40) * 15)
            pygame.draw.line(ground, (v, v + 8, v + 20), (0, i), (NANHU_MAP_WIDTH, i))
        surface.blit(ground, (0, 280))

        bx, by, bw, bh = 200, 80, 400, 250
        pygame.draw.rect(surface, (95, 112, 148), (bx, by, bw, bh))
        pygame.draw.rect(surface, (75, 88, 118), (bx - 8, by - 12, bw + 16, 18))
        pygame.draw.line(surface, (130, 152, 192), (bx, by + bh - 8), (bx + bw, by + bh - 8), 3)
        sign_text = font_small.render("南湖综合楼", True, (235, 225, 200))
        surface.blit(sign_text, (bx + bw + 20, by + bh - 60))

        for obj in self.objects:
            obj.draw(surface)

        if self.return_portal:
            px, py = self.return_portal
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.003))
            for r in range(35, 5, -5):
                alpha = int((1 - r / 35) * (60 + pulse * 40))
                s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (220, 160, 80, alpha), (r, r), r)
                surface.blit(s, (int(px - r), int(py - r)))

    def get_nearby_objects(self, px, py, max_dist=50):
        nearby = []
        for obj in self.objects:
            if obj.visible and obj.distance_to(px, py) < max_dist:
                nearby.append(obj)
        return sorted(nearby, key=lambda o: o.distance_to(px, py))
