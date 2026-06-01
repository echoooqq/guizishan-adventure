import json
import os


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ITEMS_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "items.json")

_items_database = None


def load_items_database():
    global _items_database
    if _items_database is not None:
        return _items_database
    try:
        with open(ITEMS_DATA_PATH, "r", encoding="utf-8") as f:
            _items_database = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        _items_database = {}
    return _items_database


def get_item_data(item_id):
    db = load_items_database()
    return db.get(item_id)


class Item:
    def __init__(self, item_id, count=1):
        self.id = item_id
        self.count = count
        data = get_item_data(item_id)
        if data:
            self.name = data.get("name", item_id)
            self.category = data.get("category", "material")
            self.description = data.get("description", "")
            self.droppable = data.get("droppable", True)
            self.combinable_with = data.get("combinable_with", [])
            self.combine_result = data.get("combine_result", "")
            self.sprite = data.get("sprite", item_id)
            self.effect = data.get("effect", None)
        else:
            self.name = item_id
            self.category = "material"
            self.description = ""
            self.droppable = True
            self.combinable_with = []
            self.combine_result = ""
            self.sprite = item_id
            self.effect = None

    def can_combine_with(self, other_id):
        return other_id in self.combinable_with

    def to_dict(self):
        return {
            "id": self.id,
            "count": self.count,
        }

    @staticmethod
    def from_dict(data):
        return Item(data["id"], data.get("count", 1))


class Inventory:
    MAX_SLOTS = 20

    def __init__(self):
        self.items = []

    def add_item(self, item_id, count=1):
        for item in self.items:
            if item.id == item_id:
                item.count += count
                return True
        if len(self.items) >= self.MAX_SLOTS:
            return False
        self.items.append(Item(item_id, count))
        return True

    def remove_item(self, item_id, count=1):
        for i, item in enumerate(self.items):
            if item.id == item_id:
                item.count -= count
                if item.count <= 0:
                    self.items.pop(i)
                return True
        return False

    def has_item(self, item_id):
        for item in self.items:
            if item.id == item_id and item.count > 0:
                return True
        return False

    def get_item(self, item_id):
        for item in self.items:
            if item.id == item_id:
                return item
        return None

    def get_item_count(self, item_id):
        item = self.get_item(item_id)
        return item.count if item else 0

    def combine(self, item_id_1, item_id_2):
        item1 = self.get_item(item_id_1)
        item2 = self.get_item(item_id_2)
        if not item1 or not item2:
            return None
        if not item1.can_combine_with(item_id_2):
            return None
        if not item2.can_combine_with(item_id_1):
            return None
        result_id = item1.combine_result
        if not result_id:
            return None
        self.remove_item(item_id_1)
        self.remove_item(item_id_2)
        self.add_item(result_id)
        return result_id

    def use_item(self, item_id, target=None):
        item = self.get_item(item_id)
        if not item:
            return {"success": False, "message": "没有这个道具。"}
        if item.category == "consumable":
            effect = item.effect
            self.remove_item(item_id)
            result = {"success": True, "message": f"使用了{item.name}。", "item": item}
            if effect:
                result["effect"] = effect
                if effect.get("type") == "reveal_badge":
                    badge_target = effect.get("target", "")
                    if badge_target:
                        self.add_item(badge_target)
                        result["message"] = f"{item.name}裂开了！里面竟然藏着一枚桂花徽章碎片！"
                        result["reveal_badge"] = badge_target
            return result
        if item.category == "tool":
            return {"success": True, "message": f"在合适的地方使用{item.name}吧。", "item": item}
        if item.category == "key_item":
            return {"success": False, "message": f"{item.name}不能直接使用。", "item": item}
        return {"success": False, "message": "这个道具无法使用。", "item": item}

    def get_combinable_items(self, item_id):
        item = self.get_item(item_id)
        if not item:
            return []
        result = []
        for other in self.items:
            if other.id != item_id and item.can_combine_with(other.id):
                result.append(other.id)
        return result

    def is_full(self):
        return len(self.items) >= self.MAX_SLOTS

    def get_badge_count(self):
        count = 0
        for i in range(1, 8):
            if self.has_item(f"badge_{i}"):
                count += 1
        return count

    def to_dict(self):
        return [item.to_dict() for item in self.items]

    def from_dict_data(self, data):
        self.items = [Item.from_dict(d) for d in data]
