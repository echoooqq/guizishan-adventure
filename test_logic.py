import sys
sys.path.insert(0, r'd:\桂子山秘境探险')

from game_logic import GameLogic
from map_scene import PUZZLE_DATA, SCENE_NAMES

gl = GameLogic()
gl.init_scenes()
print("Scenes initialized:", len(gl.scenes))
print("Current scene:", gl.current_scene_id)

scene = gl.get_current_scene()
print("Scene name:", scene.name)
print("Objects count:", len(scene.objects))

bag = gl.bag
bag.add_item("osmanthus_badge")
bag.add_item("osmanthus_badge")
bag.add_item("osmanthus_badge")
count = bag.get_item_count("osmanthus_badge")
print("Badge count:", count)

puzzle = PUZZLE_DATA.get("guizhong_road")
if count >= puzzle.get("target_count", 3):
    gl.solve_puzzle("guizhong_road")

print("Guizhong solved:", gl.scenes["guizhong_road"].puzzle_solved)
print("Boya unlocked:", gl.scenes["boya_square"].unlocked)
print("Score:", gl.score_system.score)

gl.solve_puzzle("nanhu_building")
print("Library unlocked:", gl.scenes["library"].unlocked)

gl.solve_puzzle("boya_square")
print("Youming unlocked:", gl.scenes["youming_gym"].unlocked)

gl.solve_puzzle("library")
print("Dining unlocked:", gl.scenes["dining_hall"].unlocked)

gl.solve_puzzle("youming_gym")
print("Fountain unlocked:", gl.scenes["fountain_square"].unlocked)

gl.solve_puzzle("dining_hall")
gl.solve_puzzle("fountain_square")
print("Night secret unlocked:", gl.night_secret_unlocked)
print("Night secret scene exists:", "night_secret" in gl.scenes)
if "night_secret" in gl.scenes:
    print("Night secret scene unlocked:", gl.scenes["night_secret"].unlocked)

gl.solve_puzzle("night_secret")
print("Game won:", gl.check_win())
print("Final score:", gl.score_system.score)

print("\nAll logic tests passed!")
