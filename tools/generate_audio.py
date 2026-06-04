"""程序化生成占位音频文件

为游戏生成简单的背景音乐和音效占位文件。
使用 numpy + pygame 生成简单的合成音频。
如果 numpy 不可用，则跳过生成。
"""

import os
import struct
import math
import array

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BGM_DIR = os.path.join(PROJECT_ROOT, "assets", "audio", "bgm")
SFX_DIR = os.path.join(PROJECT_ROOT, "assets", "audio", "sfx")

SAMPLE_RATE = 22050


def _generate_wave(frequency, duration, volume=0.3, wave_type="sine"):
    """生成波形数据"""
    n_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        if wave_type == "sine":
            value = math.sin(2 * math.pi * frequency * t)
        elif wave_type == "square":
            value = 1.0 if math.sin(2 * math.pi * frequency * t) >= 0 else -1.0
        elif wave_type == "triangle":
            value = 2.0 * abs(2.0 * (t * frequency - math.floor(t * frequency + 0.5))) - 1.0
        else:
            value = math.sin(2 * math.pi * frequency * t)

        # 应用包络
        attack = min(1.0, i / (SAMPLE_RATE * 0.01))
        release = min(1.0, (n_samples - i) / (SAMPLE_RATE * 0.01))
        envelope = attack * release

        sample = int(value * volume * envelope * 32767)
        sample = max(-32767, min(32767, sample))
        samples.append(sample)
    return samples


def _generate_melody(notes, volume=0.25):
    """根据音符列表生成旋律

    Args:
        notes: [(频率, 时长), ...] 列表
    """
    all_samples = []
    for freq, dur in notes:
        if freq == 0:
            # 休止符
            n = int(SAMPLE_RATE * dur)
            all_samples.extend([0] * n)
        else:
            all_samples.extend(_generate_wave(freq, dur, volume))
    return all_samples


def _save_wav(filepath, samples, channels=1):
    """将采样数据保存为WAV文件"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    n_samples = len(samples)
    data_size = n_samples * channels * 2  # 16-bit

    with open(filepath, 'wb') as f:
        # WAV文件头
        f.write(b'RIFF')
        f.write(struct.pack('<I', 36 + data_size))
        f.write(b'WAVE')
        f.write(b'fmt ')
        f.write(struct.pack('<I', 16))  # 子块大小
        f.write(struct.pack('<H', 1))   # PCM格式
        f.write(struct.pack('<H', channels))
        f.write(struct.pack('<I', SAMPLE_RATE))
        f.write(struct.pack('<I', SAMPLE_RATE * channels * 2))
        f.write(struct.pack('<H', channels * 2))
        f.write(struct.pack('<H', 16))  # 位深度
        f.write(b'data')
        f.write(struct.pack('<I', data_size))

        # 写入采样数据
        for s in samples:
            s = max(-32767, min(32767, int(s)))
            f.write(struct.pack('<h', s))


def _note_freq(note_name):
    """将音符名转换为频率"""
    notes_map = {
        'C3': 130.81, 'D3': 146.83, 'E3': 164.81, 'F3': 174.61,
        'G3': 196.00, 'A3': 220.00, 'B3': 246.94,
        'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F4': 349.23,
        'G4': 392.00, 'A4': 440.00, 'B4': 493.88,
        'C5': 523.25, 'D5': 587.33, 'E5': 659.25, 'F5': 698.46,
        'G5': 783.99, 'A5': 880.00,
    }
    return notes_map.get(note_name, 440)


def generate_title_bgm():
    """标题画面BGM — 神秘悠扬"""
    melody = [
        (_note_freq('E4'), 0.5), (_note_freq('G4'), 0.5),
        (_note_freq('A4'), 0.75), (_note_freq('G4'), 0.25),
        (_note_freq('E4'), 0.5), (_note_freq('D4'), 0.5),
        (_note_freq('C4'), 1.0), (0, 0.5),
        (_note_freq('E4'), 0.5), (_note_freq('G4'), 0.5),
        (_note_freq('A4'), 0.75), (_note_freq('B4'), 0.25),
        (_note_freq('C5'), 1.0), (0, 0.25),
        (_note_freq('B4'), 0.5), (_note_freq('A4'), 0.5),
        (_note_freq('G4'), 0.75), (_note_freq('E4'), 0.25),
        (_note_freq('D4'), 1.0), (0, 0.5),
    ]
    samples = _generate_melody(melody, 0.2)
    _save_wav(os.path.join(BGM_DIR, "title.wav"), samples)


def generate_intro_bgm():
    """开场BGM — 温柔校园风"""
    melody = [
        (_note_freq('C4'), 0.4), (_note_freq('E4'), 0.4),
        (_note_freq('G4'), 0.4), (_note_freq('C5'), 0.8),
        (0, 0.2), (_note_freq('B4'), 0.4),
        (_note_freq('A4'), 0.4), (_note_freq('G4'), 0.8),
        (0, 0.2), (_note_freq('F4'), 0.4),
        (_note_freq('E4'), 0.4), (_note_freq('D4'), 0.4),
        (_note_freq('C4'), 1.0), (0, 0.5),
    ]
    samples = _generate_melody(melody, 0.18)
    _save_wav(os.path.join(BGM_DIR, "intro.wav"), samples)


def generate_campus_day_bgm():
    """校园白天BGM — 明快活泼"""
    melody = [
        (_note_freq('C4'), 0.3), (_note_freq('D4'), 0.3),
        (_note_freq('E4'), 0.3), (_note_freq('G4'), 0.6),
        (_note_freq('E4'), 0.3), (_note_freq('C4'), 0.3),
        (_note_freq('D4'), 0.6), (0, 0.2),
        (_note_freq('G4'), 0.3), (_note_freq('A4'), 0.3),
        (_note_freq('G4'), 0.3), (_note_freq('E4'), 0.6),
        (_note_freq('D4'), 0.3), (_note_freq('C4'), 0.3),
        (_note_freq('D4'), 0.6), (0, 0.2),
    ]
    samples = _generate_melody(melody, 0.2)
    _save_wav(os.path.join(BGM_DIR, "campus_day.wav"), samples)


def generate_campus_night_bgm():
    """校园夜晚BGM — 神秘幽静"""
    melody = [
        (_note_freq('A3'), 0.6), (_note_freq('C4'), 0.4),
        (_note_freq('E4'), 0.8), (0, 0.3),
        (_note_freq('D4'), 0.4), (_note_freq('C4'), 0.4),
        (_note_freq('A3'), 1.0), (0, 0.5),
        (_note_freq('E4'), 0.4), (_note_freq('D4'), 0.4),
        (_note_freq('C4'), 0.6), (_note_freq('A3'), 0.4),
        (_note_freq('C4'), 0.8), (0, 0.5),
    ]
    samples = _generate_melody(melody, 0.15)
    _save_wav(os.path.join(BGM_DIR, "campus_night.wav"), samples)


def generate_library_bgm():
    """图书馆BGM — 安静书卷气"""
    melody = [
        (_note_freq('E4'), 0.5), (_note_freq('G4'), 0.5),
        (_note_freq('A4'), 1.0), (0, 0.3),
        (_note_freq('G4'), 0.5), (_note_freq('E4'), 0.5),
        (_note_freq('D4'), 1.0), (0, 0.3),
        (_note_freq('C4'), 0.5), (_note_freq('E4'), 0.5),
        (_note_freq('G4'), 0.8), (_note_freq('E4'), 0.4),
        (_note_freq('C4'), 1.0), (0, 0.5),
    ]
    samples = _generate_melody(melody, 0.12)
    _save_wav(os.path.join(BGM_DIR, "library.wav"), samples)


def generate_gym_bgm():
    """体育馆BGM — 活力运动风"""
    melody = [
        (_note_freq('C4'), 0.2), (_note_freq('C4'), 0.2),
        (_note_freq('E4'), 0.2), (_note_freq('G4'), 0.4),
        (_note_freq('G4'), 0.2), (_note_freq('E4'), 0.2),
        (_note_freq('C4'), 0.4), (0, 0.1),
        (_note_freq('F4'), 0.2), (_note_freq('F4'), 0.2),
        (_note_freq('A4'), 0.2), (_note_freq('C5'), 0.4),
        (_note_freq('A4'), 0.2), (_note_freq('F4'), 0.2),
        (_note_freq('C4'), 0.4), (0, 0.1),
    ]
    samples = _generate_melody(melody, 0.2)
    _save_wav(os.path.join(BGM_DIR, "gym.wav"), samples)


def generate_dining_hall_bgm():
    """食堂BGM — 温馨日常"""
    melody = [
        (_note_freq('G4'), 0.3), (_note_freq('A4'), 0.3),
        (_note_freq('G4'), 0.3), (_note_freq('E4'), 0.6),
        (0, 0.2), (_note_freq('D4'), 0.3),
        (_note_freq('E4'), 0.3), (_note_freq('G4'), 0.6),
        (0, 0.2), (_note_freq('A4'), 0.3),
        (_note_freq('G4'), 0.3), (_note_freq('E4'), 0.3),
        (_note_freq('D4'), 0.3), (_note_freq('C4'), 0.6),
        (0, 0.3),
    ]
    samples = _generate_melody(melody, 0.18)
    _save_wav(os.path.join(BGM_DIR, "dining_hall.wav"), samples)


def generate_nanhulou_bgm():
    """南湖综合楼BGM — 探索悬疑"""
    melody = [
        (_note_freq('A3'), 0.5), (_note_freq('C4'), 0.3),
        (_note_freq('D4'), 0.5), (0, 0.3),
        (_note_freq('E4'), 0.3), (_note_freq('D4'), 0.3),
        (_note_freq('C4'), 0.5), (_note_freq('A3'), 0.5),
        (0, 0.3), (_note_freq('D4'), 0.4),
        (_note_freq('E4'), 0.4), (_note_freq('A4'), 0.6),
        (0, 0.2), (_note_freq('G4'), 0.4),
        (_note_freq('E4'), 0.4), (_note_freq('D4'), 0.6),
        (0, 0.5),
    ]
    samples = _generate_melody(melody, 0.15)
    _save_wav(os.path.join(BGM_DIR, "nanhulou.wav"), samples)


def generate_nanhulou_secret_bgm():
    """综合楼密室BGM — 神秘秘境"""
    melody = [
        (_note_freq('E4'), 0.6), (0, 0.3),
        (_note_freq('A3'), 0.4), (_note_freq('C4'), 0.4),
        (0, 0.3), (_note_freq('E4'), 0.6),
        (0, 0.3), (_note_freq('D4'), 0.4),
        (_note_freq('C4'), 0.4), (_note_freq('A3'), 0.8),
        (0, 0.5),
    ]
    samples = _generate_melody(melody, 0.12)
    _save_wav(os.path.join(BGM_DIR, "nanhulou_secret.wav"), samples)


def generate_puzzle_bgm():
    """谜题BGM — 紧张思考"""
    melody = [
        (_note_freq('A4'), 0.3), (_note_freq('G4'), 0.3),
        (_note_freq('E4'), 0.3), (_note_freq('D4'), 0.6),
        (0, 0.2), (_note_freq('E4'), 0.3),
        (_note_freq('G4'), 0.3), (_note_freq('A4'), 0.3),
        (_note_freq('G4'), 0.6), (0, 0.2),
        (_note_freq('E4'), 0.3), (_note_freq('D4'), 0.3),
        (_note_freq('C4'), 0.3), (_note_freq('D4'), 0.6),
        (0, 0.3),
    ]
    samples = _generate_melody(melody, 0.15)
    _save_wav(os.path.join(BGM_DIR, "puzzle.wav"), samples)


def generate_outro_bgm():
    """结局BGM — 辉煌终章"""
    melody = [
        (_note_freq('C4'), 0.4), (_note_freq('E4'), 0.4),
        (_note_freq('G4'), 0.4), (_note_freq('C5'), 0.8),
        (0, 0.2), (_note_freq('B4'), 0.4),
        (_note_freq('A4'), 0.4), (_note_freq('G4'), 0.4),
        (_note_freq('E4'), 0.8), (0, 0.2),
        (_note_freq('F4'), 0.4), (_note_freq('A4'), 0.4),
        (_note_freq('G4'), 0.4), (_note_freq('E4'), 0.4),
        (_note_freq('C5'), 1.2), (0, 0.5),
    ]
    samples = _generate_melody(melody, 0.2)
    _save_wav(os.path.join(BGM_DIR, "outro.wav"), samples)


def generate_sfx_footstep():
    """脚步声"""
    samples = _generate_wave(150, 0.05, 0.15, "square")
    _save_wav(os.path.join(SFX_DIR, "footstep.wav"), samples)


def generate_sfx_pickup():
    """拾取道具"""
    notes = [(_note_freq('C5'), 0.08), (_note_freq('E5'), 0.08), (_note_freq('G5'), 0.12)]
    samples = _generate_melody(notes, 0.25)
    _save_wav(os.path.join(SFX_DIR, "pickup.wav"), samples)


def generate_sfx_door_open():
    """开门"""
    samples = _generate_wave(200, 0.15, 0.2, "triangle")
    _save_wav(os.path.join(SFX_DIR, "door_open.wav"), samples)


def generate_sfx_door_close():
    """关门"""
    samples = _generate_wave(120, 0.1, 0.2, "triangle")
    _save_wav(os.path.join(SFX_DIR, "door_close.wav"), samples)


def generate_sfx_puzzle_correct():
    """解谜正确"""
    notes = [(_note_freq('C5'), 0.1), (_note_freq('E5'), 0.1), (_note_freq('G5'), 0.2)]
    samples = _generate_melody(notes, 0.3)
    _save_wav(os.path.join(SFX_DIR, "puzzle_correct.wav"), samples)


def generate_sfx_puzzle_wrong():
    """解谜错误"""
    notes = [(_note_freq('E4'), 0.15), (_note_freq('D4'), 0.15), (_note_freq('C4'), 0.2)]
    samples = _generate_melody(notes, 0.25)
    _save_wav(os.path.join(SFX_DIR, "puzzle_wrong.wav"), samples)


def generate_sfx_puzzle_solve():
    """谜题完成"""
    notes = [
        (_note_freq('C5'), 0.1), (_note_freq('E5'), 0.1),
        (_note_freq('G5'), 0.1), (_note_freq('C6'), 0.3),
    ]
    samples = _generate_melody(notes, 0.3)
    _save_wav(os.path.join(SFX_DIR, "puzzle_solve.wav"), samples)


def generate_sfx_ui_select():
    """UI选择"""
    samples = _generate_wave(800, 0.05, 0.15, "sine")
    _save_wav(os.path.join(SFX_DIR, "ui_select.wav"), samples)


def generate_sfx_ui_confirm():
    """UI确认"""
    notes = [(_note_freq('G4'), 0.05), (_note_freq('C5'), 0.08)]
    samples = _generate_melody(notes, 0.2)
    _save_wav(os.path.join(SFX_DIR, "ui_confirm.wav"), samples)


def generate_sfx_ui_cancel():
    """UI取消"""
    notes = [(_note_freq('C5'), 0.05), (_note_freq('G4'), 0.08)]
    samples = _generate_melody(notes, 0.2)
    _save_wav(os.path.join(SFX_DIR, "ui_cancel.wav"), samples)


def generate_sfx_dialog_next():
    """对话翻页"""
    samples = _generate_wave(600, 0.04, 0.1, "sine")
    _save_wav(os.path.join(SFX_DIR, "dialog_next.wav"), samples)


def generate_sfx_badge_get():
    """获得徽章"""
    notes = [
        (_note_freq('C5'), 0.1), (_note_freq('E5'), 0.1),
        (_note_freq('G5'), 0.15), (_note_freq('C6'), 0.3),
        (_note_freq('G5'), 0.15), (_note_freq('C6'), 0.4),
    ]
    samples = _generate_melody(notes, 0.3)
    _save_wav(os.path.join(SFX_DIR, "badge_get.wav"), samples)


def generate_sfx_sprint():
    """冲刺"""
    samples = _generate_wave(100, 0.08, 0.1, "triangle")
    _save_wav(os.path.join(SFX_DIR, "sprint.wav"), samples)


def generate_sfx_item_use():
    """使用道具"""
    notes = [(_note_freq('A4'), 0.08), (_note_freq('E5'), 0.12)]
    samples = _generate_melody(notes, 0.2)
    _save_wav(os.path.join(SFX_DIR, "item_use.wav"), samples)


def generate_sfx_item_combine():
    """组合道具"""
    notes = [(_note_freq('D5'), 0.08), (_note_freq('F5'), 0.08), (_note_freq('A5'), 0.15)]
    samples = _generate_melody(notes, 0.25)
    _save_wav(os.path.join(SFX_DIR, "item_combine.wav"), samples)


def generate_all():
    """生成所有占位音频文件"""
    os.makedirs(BGM_DIR, exist_ok=True)
    os.makedirs(SFX_DIR, exist_ok=True)

    print("正在生成占位BGM...")
    bgm_generators = [
        ("标题画面", generate_title_bgm),
        ("开场", generate_intro_bgm),
        ("校园白天", generate_campus_day_bgm),
        ("校园夜晚", generate_campus_night_bgm),
        ("图书馆", generate_library_bgm),
        ("体育馆", generate_gym_bgm),
        ("食堂", generate_dining_hall_bgm),
        ("南湖综合楼", generate_nanhulou_bgm),
        ("综合楼密室", generate_nanhulou_secret_bgm),
        ("谜题", generate_puzzle_bgm),
        ("结局", generate_outro_bgm),
    ]
    for name, gen in bgm_generators:
        try:
            gen()
            print(f"  ✓ {name}")
        except Exception as e:
            print(f"  ✗ {name}: {e}")

    print("正在生成占位音效...")
    sfx_generators = [
        ("脚步声", generate_sfx_footstep),
        ("拾取", generate_sfx_pickup),
        ("开门", generate_sfx_door_open),
        ("关门", generate_sfx_door_close),
        ("解谜正确", generate_sfx_puzzle_correct),
        ("解谜错误", generate_sfx_puzzle_wrong),
        ("谜题完成", generate_sfx_puzzle_solve),
        ("UI选择", generate_sfx_ui_select),
        ("UI确认", generate_sfx_ui_confirm),
        ("UI取消", generate_sfx_ui_cancel),
        ("对话翻页", generate_sfx_dialog_next),
        ("获得徽章", generate_sfx_badge_get),
        ("冲刺", generate_sfx_sprint),
        ("使用道具", generate_sfx_item_use),
        ("组合道具", generate_sfx_item_combine),
    ]
    for name, gen in sfx_generators:
        try:
            gen()
            print(f"  ✓ {name}")
        except Exception as e:
            print(f"  ✗ {name}: {e}")

    print("占位音频生成完成！")


if __name__ == "__main__":
    generate_all()
