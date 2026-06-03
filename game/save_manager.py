"""存档管理器 — JSON序列化存档系统

负责自动存档和手动存档的读写，采用"写临时文件→重命名"策略防止数据损坏。
存档槽位：1个自动存档 + 2个手动存档
"""

import json
import os
import tempfile
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAVES_DIR = os.path.join(PROJECT_ROOT, "saves")

AUTO_SAVE_SLOT = "auto"
MANUAL_SLOTS = ["slot_1", "slot_2"]
SLOT_DISPLAY_NAMES = {
    AUTO_SAVE_SLOT: "自动存档",
    "slot_1": "存档槽 1",
    "slot_2": "存档槽 2",
}

SAVE_VERSION = 1


class SaveData:
    """存档数据结构"""

    def __init__(self):
        self.player = {}
        self.current_map = "main_campus"
        self.spawn_point = "default"
        self.inventory = []
        self.puzzles = {}
        self.clock = {}
        self.dialog_flags = {}
        self.visited_nanhu = False
        self.realm_triggered = False
        self.realm_first_night_shown = False
        self.tutorial_shown = False
        self.explored_areas = {}
        self.save_time = ""
        self.version = SAVE_VERSION
        self.play_time = 0.0

    def to_dict(self):
        return {
            "version": self.version,
            "save_time": self.save_time,
            "play_time": self.play_time,
            "player": self.player,
            "current_map": self.current_map,
            "spawn_point": self.spawn_point,
            "inventory": self.inventory,
            "puzzles": self.puzzles,
            "clock": self.clock,
            "dialog_flags": self.dialog_flags,
            "visited_nanhu": self.visited_nanhu,
            "realm_triggered": self.realm_triggered,
            "realm_first_night_shown": self.realm_first_night_shown,
            "tutorial_shown": self.tutorial_shown,
            "explored_areas": self.explored_areas,
        }

    @staticmethod
    def from_dict(data):
        sd = SaveData()
        sd.version = data.get("version", SAVE_VERSION)
        sd.save_time = data.get("save_time", "")
        sd.play_time = data.get("play_time", 0.0)
        sd.player = data.get("player", {})
        sd.current_map = data.get("current_map", "main_campus")
        sd.spawn_point = data.get("spawn_point", "default")
        sd.inventory = data.get("inventory", [])
        sd.puzzles = data.get("puzzles", {})
        sd.clock = data.get("clock", {})
        sd.dialog_flags = data.get("dialog_flags", {})
        sd.visited_nanhu = data.get("visited_nanhu", False)
        sd.realm_triggered = data.get("realm_triggered", False)
        sd.realm_first_night_shown = data.get("realm_first_night_shown", False)
        sd.tutorial_shown = data.get("tutorial_shown", False)
        sd.explored_areas = data.get("explored_areas", {})
        return sd


class SaveManager:
    """存档管理器"""

    def __init__(self):
        os.makedirs(SAVES_DIR, exist_ok=True)
        self._play_time_accumulator = 0.0

    def _slot_path(self, slot_id):
        """获取存档槽位文件路径"""
        return os.path.join(SAVES_DIR, f"{slot_id}.json")

    def has_save(self, slot_id):
        """检查指定槽位是否有存档"""
        path = self._slot_path(slot_id)
        return os.path.exists(path)

    def get_save_info(self, slot_id):
        """获取存档摘要信息（用于显示存档列表）"""
        path = self._slot_path(slot_id)
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return {
                "slot_id": slot_id,
                "display_name": SLOT_DISPLAY_NAMES.get(slot_id, slot_id),
                "save_time": data.get("save_time", ""),
                "current_map": data.get("current_map", ""),
                "day_count": data.get("clock", {}).get("day_count", 1),
                "badge_count": sum(
                    1 for s in data.get("puzzles", {}).values()
                    if s == "solved"
                ),
                "play_time": data.get("play_time", 0.0),
            }
        except (json.JSONDecodeError, IOError):
            return None

    def get_all_save_info(self):
        """获取所有存档槽位的信息"""
        result = []
        for slot_id in [AUTO_SAVE_SLOT] + MANUAL_SLOTS:
            info = self.get_save_info(slot_id)
            if info is None:
                result.append({
                    "slot_id": slot_id,
                    "display_name": SLOT_DISPLAY_NAMES.get(slot_id, slot_id),
                    "empty": True,
                })
            else:
                info["empty"] = False
                result.append(info)
        return result

    def save(self, slot_id, game_manager):
        """保存游戏到指定槽位

        采用"写临时文件→重命名"策略，避免写入中断导致数据损坏。
        """
        save_data = self._collect_save_data(game_manager)
        save_data.save_time = time.strftime("%Y-%m-%d %H:%M:%S")
        save_data.play_time = self._play_time_accumulator

        data_dict = save_data.to_dict()

        path = self._slot_path(slot_id)
        try:
            dir_name = os.path.dirname(path)
            fd, tmp_path = tempfile.mkstemp(suffix=".tmp", dir=dir_name)
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    json.dump(data_dict, f, ensure_ascii=False, indent=2)
                # 原子性重命名（Windows下需先删除目标文件）
                if os.path.exists(path):
                    os.remove(path)
                os.rename(tmp_path, path)
            except Exception:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                raise
            return True
        except (IOError, OSError) as e:
            print(f"存档失败: {e}")
            return False

    def auto_save(self, game_manager):
        """自动存档"""
        return self.save(AUTO_SAVE_SLOT, game_manager)

    def load(self, slot_id):
        """从指定槽位加载存档"""
        path = self._slot_path(slot_id)
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            save_data = SaveData.from_dict(data)
            self._play_time_accumulator = save_data.play_time
            return save_data
        except (json.JSONDecodeError, IOError) as e:
            print(f"读档失败: {e}")
            return None

    def delete_save(self, slot_id):
        """删除指定槽位的存档"""
        path = self._slot_path(slot_id)
        if os.path.exists(path):
            try:
                os.remove(path)
                return True
            except OSError:
                return False
        return True

    def has_any_save(self):
        """检查是否存在任何存档"""
        return self.has_save(AUTO_SAVE_SLOT) or any(
            self.has_save(s) for s in MANUAL_SLOTS
        )

    def update_play_time(self, dt):
        """累计游戏时间"""
        self._play_time_accumulator += dt

    def _collect_save_data(self, game_manager):
        """从游戏管理器收集存档数据"""
        sd = SaveData()

        # 玩家数据
        player = game_manager.player
        sd.player = {
            "x": player.x,
            "y": player.y,
            "direction": player.direction,
            "stamina": player.stamina,
        }

        # 当前地图
        sd.current_map = game_manager.current_map_id
        sd.spawn_point = "default"

        # 背包
        sd.inventory = player.inventory.to_dict()

        # 谜题状态
        sd.puzzles = game_manager.puzzle_manager.to_dict()

        # 时钟
        sd.clock = game_manager.game_clock.get_state_dict()

        # 对话标记
        sd.dialog_flags = dict(game_manager._dialog_flags)

        # 游戏进度标记
        sd.visited_nanhu = game_manager._visited_nanhu
        sd.realm_triggered = game_manager._realm_triggered
        sd.realm_first_night_shown = game_manager._realm_first_night_shown
        sd.tutorial_shown = game_manager._tutorial_shown

        # 已探索区域（从小地图模块获取）
        sd.explored_areas = game_manager.minimap.get_explored_data()

        return sd

    def apply_save_data(self, save_data, game_manager):
        """将存档数据应用到游戏管理器"""
        # 恢复玩家状态
        player = game_manager.player
        player.stamina = save_data.player.get("stamina", 100)
        player.direction = save_data.player.get("direction", "down")

        # 先恢复谜题状态（必须在_load_map之前，因为_setup_*_entities依赖谜题状态）
        game_manager.puzzle_manager.from_dict_data(save_data.puzzles)

        # 加载地图
        target_map = save_data.current_map
        game_manager._load_map(target_map, save_data.spawn_point)

        # 重新设置玩家位置（地图加载后重置了位置）
        player.x = save_data.player.get("x", player.x)
        player.y = save_data.player.get("y", player.y)

        # 恢复背包
        player.inventory.from_dict_data(save_data.inventory)

        # 恢复时钟
        game_manager.game_clock.load_state_dict(save_data.clock)

        # 恢复对话标记
        game_manager._dialog_flags = dict(save_data.dialog_flags)

        # 恢复游戏进度标记
        game_manager._visited_nanhu = save_data.visited_nanhu
        game_manager._realm_triggered = save_data.realm_triggered
        game_manager._realm_first_night_shown = save_data.realm_first_night_shown
        game_manager._tutorial_shown = save_data.tutorial_shown
        # 从谜题状态推导徽章收集进度
        game_manager._all_badges_collected = game_manager.puzzle_manager.is_fountain_unlocked()

        # 恢复已探索区域到小地图模块
        game_manager.minimap.load_explored_data(save_data.explored_areas)
        game_manager.minimap.invalidate_cache()

        # 更新摄像机
        from config import PLAYER_HEIGHT
        game_manager.camera.update(player.x, player.y - PLAYER_HEIGHT / 2)

        # 更新NPC可见性
        game_manager._update_npc_visibility()
