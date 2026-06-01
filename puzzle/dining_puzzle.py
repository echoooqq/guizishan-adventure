import random
from puzzle.puzzle_manager import PuzzleState


class DiningPuzzle:
    TABLE_COUNT = 3

    def __init__(self, puzzle_manager, inventory):
        self.puzzle_manager = puzzle_manager
        self.inventory = inventory
        self._card_table_index = random.randint(0, self.TABLE_COUNT - 1)
        self._searched_tables = set()
        self._card_found = False
        self._card_returned = False

    @property
    def card_found(self):
        return self._card_found

    @property
    def card_returned(self):
        return self._card_returned

    def search_table(self, table_index):
        if table_index < 0 or table_index >= self.TABLE_COUNT:
            return {"found": False, "already_searched": True}
        if table_index in self._searched_tables:
            return {"found": False, "already_searched": True}

        self._searched_tables.add(table_index)
        if table_index == self._card_table_index:
            self._card_found = True
            self.inventory.add_item("meal_card")
            return {"found": True, "already_searched": False}
        else:
            return {"found": False, "already_searched": False}

    def return_card(self):
        if not self._card_found or self._card_returned:
            return
        self._card_returned = True
        self.inventory.remove_item("meal_card")
        self.inventory.add_item("osmanthus_cake")

    def reveal_badge(self):
        if self.puzzle_manager.get_state("dining_hall") == PuzzleState.SOLVED:
            return
        self.puzzle_manager.solve("dining_hall", self.inventory)
