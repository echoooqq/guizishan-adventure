import math
import pygame
from config import DAY_DURATION


PERIOD_DAY = "day"
PERIOD_DUSK = "dusk"
PERIOD_NIGHT = "night"

DAY_START = 6.0
DUSK_START = 18.0
NIGHT_START = 19.5

REALM_DORMANT = "dormant"
REALM_AWAKENED = "awakened"
REALM_DISPELLED = "dispelled"

REALM_DORMANT_COLOR = (60, 160, 80)
REALM_DORMANT_ALPHA_DAY = 10
REALM_DORMANT_ALPHA_DUSK = 14
REALM_DORMANT_ALPHA_NIGHT = 18

REALM_AWAKENED_COLOR = (15, 80, 50)
REALM_AWAKENED_ALPHA_MIN = 12
REALM_AWAKENED_ALPHA_MAX = 18
REALM_AWAKENED_PULSE_SPEED = 0.15

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
        self.realm_state = None
        self._realm_pulse_timer = 0.0

    def get_period(self):
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

    def is_realm_active(self):
        return self.realm_state in (REALM_DORMANT, REALM_AWAKENED)

    def is_realm_awakened(self):
        return self.realm_state == REALM_AWAKENED

    def activate_realm(self):
        self.realm_state = REALM_DORMANT

    def dispel_realm(self):
        self.realm_state = REALM_DISPELLED

    def get_overlay_color(self):
        base = _interpolate_keyframes(self.game_time)

        if self.realm_state == REALM_DISPELLED or self.realm_state is None:
            return base

        if self.realm_state == REALM_DORMANT:
            period = self.get_period()
            if period == PERIOD_DAY:
                realm_alpha = REALM_DORMANT_ALPHA_DAY
            elif period == PERIOD_DUSK:
                realm_alpha = REALM_DORMANT_ALPHA_DUSK
            else:
                realm_alpha = REALM_DORMANT_ALPHA_NIGHT
            r = min(255, base[0] + int(REALM_DORMANT_COLOR[0] * realm_alpha / 255))
            g = min(255, base[1] + int(REALM_DORMANT_COLOR[1] * realm_alpha / 255))
            b = min(255, base[2] + int(REALM_DORMANT_COLOR[2] * realm_alpha / 255))
            a = min(255, base[3] + realm_alpha)
            return (r, g, b, a)

        if self.realm_state == REALM_AWAKENED:
            pulse = 0.5 + 0.5 * math.sin(self._realm_pulse_timer * REALM_AWAKENED_PULSE_SPEED * 2 * math.pi)
            realm_alpha = int(REALM_AWAKENED_ALPHA_MIN + (REALM_AWAKENED_ALPHA_MAX - REALM_AWAKENED_ALPHA_MIN) * pulse)
            r = min(255, base[0] + int(REALM_AWAKENED_COLOR[0] * realm_alpha / 255))
            g = min(255, base[1] + int(REALM_AWAKENED_COLOR[1] * realm_alpha / 255))
            b = min(255, base[2] + int(REALM_AWAKENED_COLOR[2] * realm_alpha / 255))
            a = min(255, base[3] + realm_alpha)
            return (r, g, b, a)

        return base

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

        if self.realm_state == REALM_AWAKENED:
            self._realm_pulse_timer += dt
        else:
            self._realm_pulse_timer = 0.0

        if self.is_realm_active():
            if self.is_night():
                self.realm_state = REALM_AWAKENED
            else:
                self.realm_state = REALM_DORMANT

    def set_secret_mode(self, enabled):
        self._secret_mode = enabled

    def get_state_dict(self):
        return {
            "game_time": self.game_time,
            "day_count": self.day_count,
            "realm_state": self.realm_state,
        }

    def load_state_dict(self, data):
        if data:
            self.game_time = data.get("game_time", 8.0)
            self.day_count = data.get("day_count", 1)
            self.realm_state = data.get("realm_state", None)

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
