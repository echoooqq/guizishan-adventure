"""音频管理器 — BGM切换、音量控制、音效播放

负责背景音乐和音效的加载、播放和音量控制。
支持场景BGM自动切换、淡入淡出、音量独立调节。
"""

import os
import pygame

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BGM_DIR = os.path.join(PROJECT_ROOT, "assets", "audio", "bgm")
SFX_DIR = os.path.join(PROJECT_ROOT, "assets", "audio", "sfx")

# 场景与BGM的映射关系
SCENE_BGM_MAP = {
    "title": "title",
    "intro": "intro",
    "main_campus_day": "campus_day",
    "main_campus_night": "campus_night",
    "nanhu_campus_day": "campus_day",
    "nanhu_campus_night": "campus_night",
    "library": "library",
    "gym": "gym",
    "dining_hall": "dining_hall",
    "nanhulou": "nanhulou",
    "nanhulou_secret": "nanhulou_secret",
    "puzzle": "puzzle",
    "outro": "outro",
}

# 音效名称定义
SFX_NAMES = [
    "footstep",       # 脚步声
    "pickup",         # 拾取道具
    "door_open",      # 开门
    "door_close",     # 关门
    "puzzle_correct", # 解谜正确
    "puzzle_wrong",   # 解谜错误
    "puzzle_solve",   # 谜题完成
    "ui_select",      # UI选择
    "ui_confirm",     # UI确认
    "ui_cancel",      # UI取消
    "dialog_next",    # 对话翻页
    "badge_get",      # 获得徽章
    "sprint",         # 冲刺
    "item_use",       # 使用道具
    "item_combine",   # 组合道具
]


class AudioManager:
    """音频管理器

    管理背景音乐(BGM)和音效(SFX)的加载与播放。
    当音频文件不存在时静默跳过，不影响游戏运行。
    """

    def __init__(self):
        # 音量（0.0-1.0）
        self._bgm_volume = 0.5
        self._sfx_volume = 0.7
        self._master_volume = 1.0

        # 当前播放的BGM场景ID
        self._current_bgm_scene = None

        # 已加载的音效缓存
        self._sfx_cache = {}

        # 淡入淡出状态
        self._fading = False
        self._fade_target_volume = 0.0
        self._fade_speed = 0.0
        self._fade_callback = None
        self._pending_scene = None

        # 初始化pygame音频模块
        self._initialized = False
        self._init_audio()

    def _init_audio(self):
        """初始化pygame音频模块"""
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self._initialized = True
        except pygame.error:
            self._initialized = False

    def _get_bgm_path(self, scene_id):
        """获取场景BGM文件路径"""
        filename = SCENE_BGM_MAP.get(scene_id, scene_id)
        # 尝试多种音频格式
        for ext in (".ogg", ".wav", ".mp3"):
            path = os.path.join(BGM_DIR, f"{filename}{ext}")
            if os.path.exists(path):
                return path
        return None

    def _get_sfx_path(self, sfx_name):
        """获取音效文件路径"""
        for ext in (".ogg", ".wav", ".mp3"):
            path = os.path.join(SFX_DIR, f"{sfx_name}{ext}")
            if os.path.exists(path):
                return path
        return None

    def _load_sfx(self, sfx_name):
        """加载音效到缓存"""
        if sfx_name in self._sfx_cache:
            return self._sfx_cache[sfx_name]

        path = self._get_sfx_path(sfx_name)
        if path is None:
            self._sfx_cache[sfx_name] = None
            return None

        try:
            sound = pygame.mixer.Sound(path)
            sound.set_volume(self._sfx_volume * self._master_volume)
            self._sfx_cache[sfx_name] = sound
            return sound
        except pygame.error:
            self._sfx_cache[sfx_name] = None
            return None

    def play_bgm(self, scene_id, fade_in=True):
        """播放场景BGM

        Args:
            scene_id: 场景标识符，如"main_campus_day"
            fade_in: 是否淡入
        """
        if not self._initialized:
            return

        # 相同场景不重复切换
        if scene_id == self._current_bgm_scene:
            return

        bgm_path = self._get_bgm_path(scene_id)
        if bgm_path is None:
            # 没有对应的BGM文件，停止当前BGM
            self.stop_bgm()
            self._current_bgm_scene = scene_id
            return

        try:
            if fade_in and pygame.mixer.music.get_busy():
                # 先淡出当前BGM，再淡入新BGM
                self._pending_scene = scene_id
                self._fade_out(0.5, callback=lambda: self._start_bgm(scene_id, bgm_path))
            else:
                self._start_bgm(scene_id, bgm_path, fade_in=fade_in)
        except pygame.error:
            pass

    def _start_bgm(self, scene_id, bgm_path, fade_in=True):
        """开始播放BGM"""
        try:
            pygame.mixer.music.load(bgm_path)
            pygame.mixer.music.set_volume(
                self._bgm_volume * self._master_volume
            )
            pygame.mixer.music.play(-1)  # 循环播放

            if fade_in:
                # 淡入效果
                pygame.mixer.music.set_volume(0)
                self._fade_in(1.0)

            self._current_bgm_scene = scene_id
        except pygame.error:
            pass

    def stop_bgm(self, fade_out=True):
        """停止BGM播放"""
        if not self._initialized:
            return

        if fade_out and pygame.mixer.music.get_busy():
            self._fade_out(0.5, callback=lambda: pygame.mixer.music.stop())
        else:
            try:
                pygame.mixer.music.stop()
            except pygame.error:
                pass

        self._current_bgm_scene = None

    def play_sfx(self, sfx_name):
        """播放音效

        Args:
            sfx_name: 音效名称，如"footstep"、"pickup"等
        """
        if not self._initialized:
            return

        sound = self._load_sfx(sfx_name)
        if sound is not None:
            try:
                sound.set_volume(self._sfx_volume * self._master_volume)
                sound.play()
            except pygame.error:
                pass

    def set_bgm_volume(self, volume):
        """设置BGM音量

        Args:
            volume: 音量值 0.0-1.0
        """
        self._bgm_volume = max(0.0, min(1.0, volume))
        if self._initialized and pygame.mixer.music.get_busy():
            try:
                pygame.mixer.music.set_volume(
                    self._bgm_volume * self._master_volume
                )
            except pygame.error:
                pass

    def set_sfx_volume(self, volume):
        """设置音效音量

        Args:
            volume: 音量值 0.0-1.0
        """
        self._sfx_volume = max(0.0, min(1.0, volume))
        # 更新已缓存音效的音量
        for sound in self._sfx_cache.values():
            if sound is not None:
                sound.set_volume(self._sfx_volume * self._master_volume)

    def set_master_volume(self, volume):
        """设置主音量

        Args:
            volume: 音量值 0.0-1.0
        """
        self._master_volume = max(0.0, min(1.0, volume))
        # 更新BGM音量
        if self._initialized and pygame.mixer.music.get_busy():
            try:
                pygame.mixer.music.set_volume(
                    self._bgm_volume * self._master_volume
                )
            except pygame.error:
                pass
        # 更新音效音量
        for sound in self._sfx_cache.values():
            if sound is not None:
                sound.set_volume(self._sfx_volume * self._master_volume)

    def get_bgm_volume(self):
        """获取BGM音量"""
        return self._bgm_volume

    def get_sfx_volume(self):
        """获取音效音量"""
        return self._sfx_volume

    def get_master_volume(self):
        """获取主音量"""
        return self._master_volume

    def _fade_out(self, duration, callback=None):
        """淡出BGM"""
        self._fading = True
        self._fade_target_volume = 0.0
        self._fade_speed = self._bgm_volume / max(duration, 0.01)
        self._fade_callback = callback

    def _fade_in(self, duration):
        """淡入BGM"""
        self._fading = True
        self._fade_target_volume = self._bgm_volume * self._master_volume
        self._fade_speed = self._fade_target_volume / max(duration, 0.01)

    def update(self, dt):
        """更新淡入淡出状态，每帧调用"""
        if not self._fading or not self._initialized:
            return

        try:
            current_vol = pygame.mixer.music.get_volume()
        except pygame.error:
            self._fading = False
            return

        if current_vol < self._fade_target_volume:
            # 淡入
            new_vol = min(current_vol + self._fade_speed * dt, self._fade_target_volume)
        else:
            # 淡出
            new_vol = max(current_vol - self._fade_speed * dt, self._fade_target_volume)

        try:
            pygame.mixer.music.set_volume(new_vol)
        except pygame.error:
            self._fading = False
            return

        # 检查是否完成
        if abs(new_vol - self._fade_target_volume) < 0.01:
            try:
                pygame.mixer.music.set_volume(self._fade_target_volume)
            except pygame.error:
                pass
            self._fading = False
            if self._fade_callback:
                callback = self._fade_callback
                self._fade_callback = None
                callback()

    def get_current_bgm_scene(self):
        """获取当前BGM场景ID"""
        return self._current_bgm_scene

    def to_dict(self):
        """序列化音频设置"""
        return {
            "bgm_volume": self._bgm_volume,
            "sfx_volume": self._sfx_volume,
            "master_volume": self._master_volume,
        }

    def from_dict_data(self, data):
        """从字典恢复音频设置"""
        self.set_bgm_volume(data.get("bgm_volume", 0.5))
        self.set_sfx_volume(data.get("sfx_volume", 0.7))
        self.set_master_volume(data.get("master_volume", 1.0))

    def get_scene_bgm_key(self, map_id, is_night=False):
        """根据地图ID和时段获取BGM场景键

        Args:
            map_id: 地图ID，如"main_campus"、"library_f1"等
            is_night: 是否夜晚
        Returns:
            BGM场景键字符串
        """
        # 室内地图使用室内BGM
        indoor_bgm = {
            "library_f1": "library",
            "library_f2": "library",
            "gym": "gym",
            "dining_hall_f1": "dining_hall",
            "dining_hall_f2": "dining_hall",
            "nanhulou_f1": "nanhulou",
            "nanhulou_f2": "nanhulou",
            "nanhulou_secret": "nanhulou_secret",
        }
        if map_id in indoor_bgm:
            return indoor_bgm[map_id]

        # 室外地图根据时段选择
        if map_id == "main_campus":
            return "main_campus_night" if is_night else "main_campus_day"
        elif map_id == "nanhu_campus":
            return "nanhu_campus_night" if is_night else "nanhu_campus_day"

        # 默认
        return "main_campus_day"
