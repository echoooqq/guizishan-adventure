import json
import os
from map_scene import PUZZLE_DATA, SCENE_UNLOCK_RULES, SCENE_NAMES
from item_bag import Bag


SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "save_data.json")


class PuzzleManager:
    def __init__(self):
        self.current_puzzle = None
        self.current_scene_id = None
        self.tf_index = 0
        self.tf_correct = 0
        self.puzzle_active = False

    def start_puzzle(self, scene_id):
        puzzle = PUZZLE_DATA.get(scene_id)
        if puzzle is None:
            return False
        self.current_puzzle = puzzle
        self.current_scene_id = scene_id
        self.puzzle_active = True
        self.tf_index = 0
        self.tf_correct = 0
        return True

    def check_choice_answer(self, option_index):
        if self.current_puzzle is None:
            return None
        if self.current_puzzle["type"] != "choice":
            return None
        correct = option_index == self.current_puzzle["answer"]
        return correct

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
        self.current_scene_id = None
        self.puzzle_active = False
        self.tf_index = 0
        self.tf_correct = 0


class ScoreSystem:
    def __init__(self):
        self.score = 0
        self.items_collected = 0
        self.scenes_unlocked = 2
        self.puzzles_solved = 0

    def add_score(self, points):
        self.score += points

    def on_item_collected(self):
        self.items_collected += 1
        self.add_score(10)

    def on_puzzle_solved(self):
        self.puzzles_solved += 1
        self.add_score(50)

    def on_scene_unlocked(self):
        self.scenes_unlocked += 1
        self.add_score(30)

    def reset(self):
        self.score = 0
        self.items_collected = 0
        self.scenes_unlocked = 2
        self.puzzles_solved = 0


class SaveSystem:
    @staticmethod
    def save_game(score_system, bag, scenes, current_scene_id):
        data = {
            "score": score_system.score,
            "items_collected": score_system.items_collected,
            "scenes_unlocked": score_system.scenes_unlocked,
            "puzzles_solved": score_system.puzzles_solved,
            "bag": bag.to_list(),
            "unlocked_scenes": [],
            "solved_scenes": [],
            "interacted_objects": {},
            "current_scene": current_scene_id,
        }
        for sid, scene in scenes.items():
            if scene.unlocked:
                data["unlocked_scenes"].append(sid)
            if scene.puzzle_solved:
                data["solved_scenes"].append(sid)
            obj_list = []
            for obj in scene.objects:
                if obj.interacted:
                    obj_list.append(obj.name)
            if obj_list:
                data["interacted_objects"][sid] = obj_list

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
                data = json.load(f)
            return data
        except Exception:
            return None

    @staticmethod
    def has_save():
        return os.path.exists(SAVE_FILE)

    @staticmethod
    def delete_save():
        if os.path.exists(SAVE_FILE):
            os.remove(SAVE_FILE)


class GameLogic:
    def __init__(self):
        self.puzzle_manager = PuzzleManager()
        self.score_system = ScoreSystem()
        self.bag = Bag()
        self.scenes = {}
        self.current_scene_id = "guizhong_road"
        self.game_won = False
        self.night_secret_unlocked = False

    def init_scenes(self):
        from map_scene import Scene
        scene_ids = list(PUZZLE_DATA.keys())
        for sid in scene_ids:
            self.scenes[sid] = Scene(sid)

    def get_current_scene(self):
        return self.scenes.get(self.current_scene_id)

    def try_collect_item(self, obj):
        if obj.item_id and not obj.interacted:
            if self.bag.add_item(obj.item_id):
                obj.interacted = True
                self.score_system.on_item_collected()
                scene = self.get_current_scene()
                if scene:
                    scene.add_particle(obj.rect.centerx, obj.rect.centery, (255, 255, 100))
                return True
        return False

    def try_start_puzzle(self, scene_id):
        scene = self.scenes.get(scene_id)
        if scene and scene.puzzle_solved:
            return False
        return self.puzzle_manager.start_puzzle(scene_id)

    def solve_puzzle(self, scene_id):
        scene = self.scenes.get(scene_id)
        if scene:
            scene.puzzle_solved = True
            self.score_system.on_puzzle_solved()
            self._check_unlock(scene_id)
            self._check_night_secret()
            return True
        return False

    def _check_unlock(self, solved_scene_id):
        for sid, rule in SCENE_UNLOCK_RULES.items():
            if rule == solved_scene_id:
                scene = self.scenes.get(sid)
                if scene and not scene.unlocked:
                    scene.unlocked = True
                    self.score_system.on_scene_unlocked()

    def _check_night_secret(self):
        from map_scene import Scene
        all_normal_solved = True
        for sid in list(PUZZLE_DATA.keys()):
            if sid == "night_secret":
                continue
            scene = self.scenes.get(sid)
            if scene and not scene.puzzle_solved:
                all_normal_solved = False
                break
        if all_normal_solved and not self.night_secret_unlocked:
            self.night_secret_unlocked = True
            if "night_secret" not in self.scenes:
                self.scenes["night_secret"] = Scene("night_secret")
            self.scenes["night_secret"].unlocked = True
            self.score_system.on_scene_unlocked()

    def check_win(self):
        if not self.night_secret_unlocked:
            return False
        night_scene = self.scenes.get("night_secret")
        if night_scene and night_scene.puzzle_solved:
            self.game_won = True
            return True
        return False

    def can_travel_to(self, target_scene_id):
        scene = self.scenes.get(target_scene_id)
        if scene is None:
            return False
        if not scene.unlocked:
            return False
        current = self.get_current_scene()
        if current is None:
            return False
        from map_scene import SCENE_CONNECTIONS
        connections = SCENE_CONNECTIONS.get(self.current_scene_id, [])
        return target_scene_id in connections

    def travel_to(self, target_scene_id):
        if self.can_travel_to(target_scene_id):
            self.current_scene_id = target_scene_id
            return True
        return False

    def use_bookmark(self):
        if self.bag.use_item("bookmark"):
            puzzle = self.puzzle_manager.current_puzzle
            if puzzle and "hint" in puzzle:
                return puzzle["hint"]
            return "当前没有可用的提示。"
        return None

    def save(self):
        return SaveSystem.save_game(
            self.score_system, self.bag, self.scenes, self.current_scene_id
        )

    def load(self):
        data = SaveSystem.load_game()
        if data is None:
            return False
        self.score_system.score = data.get("score", 0)
        self.score_system.items_collected = data.get("items_collected", 0)
        self.score_system.scenes_unlocked = data.get("scenes_unlocked", 2)
        self.score_system.puzzles_solved = data.get("puzzles_solved", 0)

        self.bag = Bag.from_list(data.get("bag", []))

        self.init_scenes()

        for sid in data.get("unlocked_scenes", []):
            if sid in self.scenes:
                self.scenes[sid].unlocked = True

        for sid in data.get("solved_scenes", []):
            if sid in self.scenes:
                self.scenes[sid].puzzle_solved = True

        interacted = data.get("interacted_objects", {})
        for sid, obj_names in interacted.items():
            scene = self.scenes.get(sid)
            if scene:
                for obj in scene.objects:
                    if obj.name in obj_names:
                        obj.interacted = True

        self.current_scene_id = data.get("current_scene", "guizhong_road")

        all_normal_solved = True
        for sid in list(PUZZLE_DATA.keys()):
            if sid == "night_secret":
                continue
            scene = self.scenes.get(sid)
            if scene and not scene.puzzle_solved:
                all_normal_solved = False
                break
        if all_normal_solved:
            self.night_secret_unlocked = True
            if "night_secret" in self.scenes:
                self.scenes["night_secret"].unlocked = True

        return True

    def reset(self):
        self.puzzle_manager = PuzzleManager()
        self.score_system = ScoreSystem()
        self.bag = Bag()
        self.game_won = False
        self.night_secret_unlocked = False
        self.current_scene_id = "guizhong_road"
        self.init_scenes()
