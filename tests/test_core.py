import os

from PIL import Image

from core import get_number_of_items_in_current_tile, get_number_of_characters_in_current_tile, get_health, get_mana, \
    get_stamina, is_health_potion_cooldown, is_mana_potion_cooldown, is_general_cooldown, get_focus

test_image_1 = Image.open(os.path.dirname(os.path.realpath(__file__)) + '/fixtures/snap_1583267560.png')
test_image_2 = Image.open(os.path.dirname(os.path.realpath(__file__)) + '/fixtures/snap_1584648581.png')

def test_detects_items():
    item_count = get_number_of_items_in_current_tile(test_image_1)

    assert item_count == 4


def test_detects_characters():
    player_count, enemy_count = get_number_of_characters_in_current_tile(test_image_1)

    assert player_count == 1
    assert enemy_count == 2


def test_detects_resources():
    health = get_health(test_image_1)
    mana = get_mana(test_image_1)
    stamina = get_stamina(test_image_1)

    assert health == 98
    assert mana == 100
    assert stamina == 47

    focus = get_focus(test_image_2)

    assert focus == 59


def test_detects_cooldowns():
    is_health_pot_cooldown = is_health_potion_cooldown(test_image_1)
    is_mana_pot_cooldown = is_mana_potion_cooldown(test_image_1)
    is_gen_cooldown = is_general_cooldown(test_image_1)

    assert is_health_pot_cooldown
    assert is_mana_pot_cooldown
    assert is_gen_cooldown
