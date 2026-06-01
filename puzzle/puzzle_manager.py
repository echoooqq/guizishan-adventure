import json
import os
from enum import Enum


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUZZLES_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "puzzles.json")


class PuzzleState(Enum):
    UNDISCOVERED = "undiscovered"
    DISCOVERED = "discovered"
    IN_PROGRESS = "in_progress"
    SOLVED = "solved"


class PuzzleManager:
    def __init__(self):
        self._puzzles_data = {}
        self._states = {}
        self._load_puzzles_data()

    def _load_puzzles_data(self):
        try:
            with open(PUZZLES_DATA_PATH, "r", encoding="utf-8") as f:
                self._puzzles_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._puzzles_data = {}

        for puzzle_id, puzzle_info in self._puzzles_data.items():
            initial = puzzle_info.get("initial_state", "undiscovered")
            self._states[puzzle_id] = PuzzleState(initial)

    def get_state(self, puzzle_id):
        return self._states.get(puzzle_id, PuzzleState.UNDISCOVERED)

    def set_state(self, puzzle_id, state):
        if isinstance(state, str):
            state = PuzzleState(state)
        self._states[puzzle_id] = state

    def can_attempt(self, puzzle_id):
        current = self.get_state(puzzle_id)
        if current == PuzzleState.SOLVED:
            return False

        puzzle_info = self._puzzles_data.get(puzzle_id, {})
        prerequisites = puzzle_info.get("prerequisites", [])
        for prereq_id in prerequisites:
            if self.get_state(prereq_id) != PuzzleState.SOLVED:
                return False

        return True

    def solve(self, puzzle_id, inventory=None):
        self._states[puzzle_id] = PuzzleState.SOLVED

        puzzle_info = self._puzzles_data.get(puzzle_id, {})
        badge_reward = puzzle_info.get("badge_reward", "")
        if badge_reward and inventory:
            inventory.add_item(badge_reward)

        return badge_reward

    def get_badge_count(self, inventory=None):
        if inventory:
            return inventory.get_badge_count()
        count = 0
        for puzzle_id, state in self._states.items():
            if state == PuzzleState.SOLVED:
                count += 1
        return count

    def is_fountain_unlocked(self):
        fountain_info = self._puzzles_data.get("fountain", {})
        prerequisites = fountain_info.get("prerequisites", [])
        for prereq_id in prerequisites:
            if self.get_state(prereq_id) != PuzzleState.SOLVED:
                return False
        return True

    def get_puzzle_info(self, puzzle_id):
        return self._puzzles_data.get(puzzle_id, {})

    def is_night_only(self, puzzle_id):
        info = self.get_puzzle_info(puzzle_id)
        return info.get("night_only", False)

    def discover(self, puzzle_id):
        if self.get_state(puzzle_id) == PuzzleState.UNDISCOVERED:
            self.set_state(puzzle_id, PuzzleState.DISCOVERED)

    def start_puzzle(self, puzzle_id):
        if self.can_attempt(puzzle_id):
            self.set_state(puzzle_id, PuzzleState.IN_PROGRESS)
            return True
        return False

    def to_dict(self):
        return {pid: state.value for pid, state in self._states.items()}

    def from_dict_data(self, data):
        for pid, state_str in data.items():
            try:
                self._states[pid] = PuzzleState(state_str)
            except ValueError:
                pass
