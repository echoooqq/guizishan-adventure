import pygame
from config import DAY_DURATION


PERIOD_DAY = "day"
PERIOD_DUSK = "dusk"
PERIOD_NIGHT = "night"

DAY_START = 6.0
DUSK_START = 18.0
NIGHT_START = 19.5

DUSK_DURATION = NIGHT_START - DUSK_START

COLOR_DAY_OVERLAY = (0, 0, 0, 0)
COLOR_DUSK_OVERLAY = (200, 100, 50)
COLOR_NIGHT_OVERLAY = (20, 20, 80)
COLOR_SECRET_OVERLAY = (30, 120, 60)

MAX_DUSK_ALPHA = 80
MAX_NIGHT_ALPHA = 120
MAX_SECRET_ALPHA = 80


class GameClock:
    def __init__(self):
        self.game_time = 8.0
        self.day_count = 1
        self.time_speed = 24.0 / DAY_DURATION
        self._secret_mode = False

    def get_period(self):
        if self._secret_mode:
            return PERIOD_NIGHT
        if DAY_START <= self.game_time < DUSK_START:
            return PERIOD_DAY
        elif DUSK_START <= self.game_time < NIGHT_START:
            return PERIOD_DUSK
        else:
            return PERIOD_NIGHT

    def is_night(self):
        return self.get_period() == PERIOD_NIGHT

    def is_day(self):
        return self.get_period() == PERIOD_DAY

    def is_dusk(self):
        return self.get_period() == PERIOD_DUSK

    def get_overlay_color(self):
        if self._secret_mode:
            return (*COLOR_SECRET_OVERLAY, MAX_SECRET_ALPHA)

        period = self.get_period()

        if period == PERIOD_DAY:
            return COLOR_DAY_OVERLAY

        elif period == PERIOD_DUSK:
            progress = (self.game_time - DUSK_START) / DUSK_DURATION
            alpha = int(MAX_DUSK_ALPHA * progress)
            return (*COLOR_DUSK_OVERLAY, alpha)

        else:
            if self.game_time >= NIGHT_START:
                night_progress = (self.game_time - NIGHT_START) / (24.0 - NIGHT_START)
            else:
                night_progress = (self.game_time + 24.0 - NIGHT_START) / (24.0 - NIGHT_START)
            alpha = min(MAX_NIGHT_ALPHA, int(MAX_NIGHT_ALPHA * min(night_progress * 3, 1.0)))
            return (*COLOR_NIGHT_OVERLAY, alpha)

    def get_time_string(self):
        hours = int(self.game_time)
        minutes = int((self.game_time - hours) * 60)
        return f"{hours:02d}:{minutes:02d}"

    def get_period_name(self):
        period = self.get_period()
        if period == PERIOD_DAY:
            return "白天"
        elif period == PERIOD_DUSK:
            return "黄昏"
        else:
            return "夜晚"

    def update(self, dt):
        self.game_time += self.time_speed * dt
        if self.game_time >= 24.0:
            self.game_time -= 24.0
            self.day_count += 1

    def set_secret_mode(self, enabled):
        self._secret_mode = enabled

    def get_state_dict(self):
        return {
            "game_time": self.game_time,
            "day_count": self.day_count,
        }

    def load_state_dict(self, data):
        if data:
            self.game_time = data.get("game_time", 8.0)
            self.day_count = data.get("day_count", 1)

    def should_npc_appear(self, npc_id):
        period = self.get_period()
        npc_schedule = NPC_SCHEDULES.get(npc_id)
        if npc_schedule is None:
            return True
        return period in npc_schedule


NPC_SCHEDULES = {
    "librarian": [PERIOD_DAY, PERIOD_DUSK],
    "dancing_auntie": [PERIOD_NIGHT],
    "pe_teacher": [PERIOD_DAY, PERIOD_DUSK],
    "cafeteria_auntie": [PERIOD_DAY, PERIOD_DUSK, PERIOD_NIGHT],
    "senior_student": [PERIOD_DAY, PERIOD_DUSK, PERIOD_NIGHT],
    "passing_student": [PERIOD_DAY, PERIOD_DUSK, PERIOD_NIGHT],
    "guardian": [PERIOD_DAY, PERIOD_DUSK, PERIOD_NIGHT],
}
