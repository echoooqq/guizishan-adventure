import pygame
from config import DAY_DURATION


PERIOD_DAY = "day"
PERIOD_DUSK = "dusk"
PERIOD_NIGHT = "night"

DAY_START = 6.0
DUSK_START = 18.0
NIGHT_START = 19.5

COLOR_SECRET_OVERLAY = (30, 120, 60)
MAX_SECRET_ALPHA = 80

LIGHT_KEYFRAMES = [
    (3.0,   10, 15, 55, 155),
    (4.5,   20, 25, 65, 130),
    (5.5,   80, 60, 80, 70),
    (6.5,   200, 140, 80, 18),
    (8.0,   0, 0, 0, 0),
    (12.0,  0, 0, 0, 0),
    (16.0,  180, 130, 60, 8),
    (17.5,  200, 120, 50, 28),
    (18.5,  200, 100, 50, 60),
    (19.5,  80, 50, 110, 100),
    (21.0,  10, 15, 55, 150),
]


def _lerp(a, b, t):
    return a + (b - a) * t


def _interpolate_keyframes(game_time):
    kf = LIGHT_KEYFRAMES
    n = len(kf)

    if game_time < kf[0][0]:
        t0, r0, g0, b0, a0 = kf[-1]
        t1, r1, g1, b1, a1 = kf[0]
        t0_adj = t0 - 24.0
        t_adj = game_time
    elif game_time >= kf[-1][0]:
        t0, r0, g0, b0, a0 = kf[-1]
        t1, r1, g1, b1, a1 = kf[0]
        t1_adj = t1 + 24.0
        t0_adj = t0
        t_adj = game_time
        progress = (t_adj - t0_adj) / (t1_adj - t0_adj)
        r = int(_lerp(r0, r1, progress))
        g = int(_lerp(g0, g1, progress))
        b = int(_lerp(b0, b1, progress))
        a = int(_lerp(a0, a1, progress))
        return (r, g, b, a)
    else:
        for i in range(n - 1):
            if kf[i][0] <= game_time < kf[i + 1][0]:
                t0, r0, g0, b0, a0 = kf[i]
                t1, r1, g1, b1, a1 = kf[i + 1]
                break
        else:
            return (0, 0, 0, 0)

    if game_time < kf[0][0]:
        progress = (game_time - t0_adj) / (t1 - t0_adj)
    else:
        progress = (game_time - t0) / (t1 - t0)

    r = int(_lerp(r0, r1, progress))
    g = int(_lerp(g0, g1, progress))
    b = int(_lerp(b0, b1, progress))
    a = int(_lerp(a0, a1, progress))
    return (r, g, b, a)


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
        return _interpolate_keyframes(self.game_time)

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
